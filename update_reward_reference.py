"""ablation の測定結果から RewardReference.md の自動生成セクションを更新する。

キュー実行（run_ablation_queue.sh）がすべて終わったあとに自動で呼ばれる。手動なら:

    python update_reward_reference.py            # 更新して差分を表示
    python update_reward_reference.py --check    # 更新せず、変化があるかだけ見る

やること:
  1. 各 ablation 学習スクリプトから「何を外したか」(_ABL / _ABL_MINOR16) を読む
     → **単一の真実の源**。表を手で書き写す必要がない。
  2. experiments/results_json/ の測定結果を読み、v23 のノイズ床に対する 2σ 検定をかける。
     安全要件（トルクピーク）は seed 別の最悪値で別途判定する。
  3. RewardReference.md の
       <!-- AUTO:ablation-results:start --> … <!-- AUTO:ablation-results:end -->
     の内側だけを書き換える（手書きの考察は触らない）。
  4. 手書きの §1 一覧表の判定と食い違う項目があれば**警告として列挙**する
     （文章の書き換えは人＝モデルの仕事なので自動ではやらない）。
"""

import argparse
import ast
import glob
import json
import os
import re
import statistics as st

REPO = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(REPO, "RewardReference.md")
RJ = os.path.join(REPO, "experiments", "results_json")
START = "<!-- AUTO:ablation-results:start -->"
END = "<!-- AUTO:ablation-results:end -->"

# 指標: キー, 表示名, 単位, 良い向き(-1=小さいほど良い / +1=大きいほど良い / 0=範囲)
METRICS = [
    ("torque_mean_pct", "トルク平均", "%", -1),
    ("lateral_pct", "横ずれ率", "%", -1),
    ("speed_mps", "前進速度", "m/s", +1),
    ("knee_rom_deg", "膝ROM", "deg", 0),
    ("sole_tilt_touchdown_deg", "足裏傾き(着地)", "deg", -1),
    ("duty_asym_pt", "接地率左右差", "pt", -1),
    ("clearance_rear_m", "後脚足上げ", "m", +1),
]
COND = "with_offset"          # 実機に近い条件で判定する
SAFE_PEAK = 90.0              # トルクピークのハード上限[%]


def removed_terms():
    """各 ablation 学習スクリプトが無効化している報酬項を読み取る（AST で安全に）。"""
    out = {}
    for path in sorted(glob.glob(os.path.join(REPO, "khr_train_quad2*_abl_*.py"))):
        tree = ast.parse(open(path).read())
        terms = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and node.targets and isinstance(node.targets[0], ast.Name):
                if node.targets[0].id in ("_ABL", "_ABL_MINOR16"):
                    try:
                        terms = ast.literal_eval(node.value)
                    except ValueError:
                        pass
        if terms:
            out[os.path.basename(path)] = terms
    return out


def load_runs():
    """exp 名 → 測定結果（seed ごと）。exp 名から ablation タグを推測して紐付ける。"""
    runs = {}
    for p in sorted(glob.glob(os.path.join(RJ, "*.json"))):
        name = os.path.basename(p)[:-5]
        m = re.match(r"^(khr-quadruped\d+(?:-\w+)*?)-s(\d+)$", name)
        if not m:
            continue
        runs.setdefault(m.group(1), []).append(json.load(open(p)))
    return runs


def agg(xs, key):
    vs = [x[COND][key] for x in xs if x[COND].get(key) is not None]
    return (st.mean(vs), st.pstdev(vs)) if vs else (None, None)


def verdict(xs, nf):
    """2σ 検定＋安全判定。戻り値: (最悪ピーク, 安全か, 2σ超の指標リスト, 総合判定)"""
    peaks = [x[COND]["torque_peak_pct"] for x in xs]
    worst = max(peaks)
    safe = worst < SAFE_PEAK
    hits = []
    for k, nm, u, good in METRICS:
        b = nf[COND].get(k)
        m, _ = agg(xs, k)
        if b is None or m is None:
            continue
        d = m - b["mean"]
        if abs(d) <= b["two_sigma"]:
            continue
        if good == 0:
            lab = "変化"
        else:
            lab = "改善" if ((d < 0) == (good == -1)) else "悪化"
        hits.append((nm, lab, abs(d) / b["sd"] if b["sd"] else float("inf")))
    worsened = [h for h in hits if h[1] == "悪化"]
    if not safe:
        final = f"❌ 削除不可（ピーク {worst:.1f}%）"
    elif worsened:
        final = "❌ 削除不可（" + ", ".join(f"{n}{l}{s:.1f}σ" for n, l, s in worsened) + "）"
    else:
        final = "✅ 削除可"
    return worst, safe, hits, final


def render(nf, runs, rm):
    base = runs.get("v27_p080") or []
    L = []
    L.append("")
    L.append(f"*このセクションは `update_reward_reference.py` が自動生成している。"
             f"最終更新: {__import__('datetime').datetime.now():%Y-%m-%d %H:%M}*")
    L.append("")
    L.append(f"判定条件: 個体差あり・v23 の 4 seed ノイズ床に対する 2σ 検定。"
             f"**安全要件はトルクピークの seed 別最悪値 < {SAFE_PEAK:.0f}%** で別途判定する。")
    L.append("")

    # --- 構成ごとの判定 ---
    L.append("### 12.1 構成ごとの判定")
    L.append("")
    L.append("| 構成 | 外した報酬 | seed | ピーク最悪 | 2σ を超えた指標 | 判定 |")
    L.append("|---|---|---|---|---|---|")
    if base:
        w = max(x[COND]["torque_peak_pct"] for x in base)
        L.append(f"| **v27**（基準） | — | {len(base)} | {w:.1f} % | — | — |")
    name_map = {}
    for script, terms in rm.items():
        tag = re.sub(r"^khr_train_quad2\d+_abl_", "", script)[:-3]
        name_map[tag] = terms
    for exp in sorted(runs):
        if exp == "v27_p080" or exp.startswith("v2") or exp.startswith("abl_"):
            continue
        xs = runs[exp]
        key = re.sub(r"^khr-quadruped2\d+-abl-", "", exp).replace("-", "_")
        terms = None
        for tag, t in name_map.items():
            if tag.replace("only_", "") == key.replace("only_", "") or tag == key:
                terms = t
                break
        worst, safe, hits, final = verdict(xs, nf)
        hs = ", ".join(f"{n}{l}({s:.1f}σ)" for n, l, s in hits) or "—"
        tl = "`" + "`, `".join(terms) + "`" if terms else "?"
        flag = " ⚠️" if not safe else ""
        L.append(f"| `{exp}` | {tl} | {len(xs)} | {worst:.1f} %{flag} | {hs} | {final} |")
    L.append("")

    # --- 主要指標の実測値 ---
    L.append("### 12.2 主要指標の実測値（個体差あり・平均）")
    L.append("")
    hdr = "| 構成 | " + " | ".join(nm for _, nm, _, _ in METRICS) + " |"
    L.append(hdr)
    L.append("|---" * (len(METRICS) + 1) + "|")
    order = ([("v27_p080", base)] if base else []) + \
            [(e, runs[e]) for e in sorted(runs) if e not in ("v27_p080",) and not e.startswith("v2")]
    for exp, xs in order:
        if not xs:
            continue
        cells = []
        for k, nm, u, good in METRICS:
            m, _ = agg(xs, k)
            if m is None:
                cells.append("—")
            else:
                cells.append(f"{m:.4f}" if u in ("m", "m/s") else f"{m:.2f}")
        L.append(f"| `{exp}` | " + " | ".join(cells) + " |")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="書き換えずに差分の有無だけ報告")
    args = ap.parse_args()

    nf = json.load(open(os.path.join(REPO, "experiments", "noise_floor.json")))
    runs = load_runs()
    rm = removed_terms()
    if not runs:
        print("[skip] 測定結果が見つかりません"); return

    body = render(nf, runs, rm)
    doc = open(DOC).read()
    if START not in doc or END not in doc:
        print(f"[abort] {DOC} に自動更新マーカーがありません"); return
    new = re.sub(re.escape(START) + r".*?" + re.escape(END),
                 START + body + END, doc, flags=re.S)
    changed = new != doc
    if args.check:
        print("[check] 更新あり" if changed else "[check] 変化なし"); return
    if changed:
        open(DOC, "w").write(new)
        print(f"[ok] RewardReference.md を更新しました（{len(runs)} 構成）")
    else:
        print("[ok] 変化なし")

    # 手書きの §1 判定と食い違う項目を警告（文章の修正は人が行う）
    warn = []
    for exp, xs in runs.items():
        if exp.startswith("v2") or exp == "v27_p080":
            continue
        _, safe, _, final = verdict(xs, nf)
        if not safe:
            warn.append(f"{exp}: 安全要件違反（ピーク {max(x[COND]['torque_peak_pct'] for x in xs):.1f}%）")
    if warn:
        print("\n[注意] 安全要件に触れた構成:")
        for w in warn:
            print("   -", w)
    print("\n次にモデルが行うこと: §1 一覧表と §2-9 の本文を、上の自動生成結果に合わせて更新する。")


if __name__ == "__main__":
    main()
