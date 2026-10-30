"""初期状態バンク v2 を作る: bank_v1 をそのまま先頭に置き、歩行中の転倒の状態（F、kind 2）を後ろに足す（2026-10-30、getup-v6 の L3 用）。

  python -m getup.tools.make_bank_v2 getup/data/banks/falls_khr-quadruped31-s{1,2,3}.pt    # → getup/data/banks/bank_v2.pt と MANIFEST.json

- bank_v1 の 24,000 状態は番号も学習用・評価用の分け方も変えない（v1〜v5 の評価と同じ状態を同じ番号で引ける）。
- F は getup/tools/fall_survey.py が保存した状態（v31 の歩行の方策を押して転ばせ、脱力して止まった状態）。
  胴体の水平の位置は 0 に戻す（床は平らで無限なので物理は変わらない。bank_v1 と同じく原点に置く）。
- F の学習用 80 % / 評価用 20 % は seed で決まる。どのシードの方策で転んだかで分けない（混ぜてから分ける）。
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess

from khr_common.paths import REPO_ROOT

OUT_DIR = REPO_ROOT / "getup" / "data" / "banks"
KEYS = ("pos", "quat", "q", "u0", "h_base", "h_chest", "limp", "kind")


def sha256(p) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("falls", nargs="+", help="fall_survey.py --states の .pt")
    ap.add_argument("--base", default="getup/data/banks/bank_v1.pt")
    ap.add_argument("--out", default="bank_v2.pt", help="getup/data/banks/ の中の名前。絶対パスなら動作確認用（MANIFEST に書かない）")
    ap.add_argument("--eval_frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    import torch
    git = lambda *x: subprocess.run(["git", *x], text=True, capture_output=True, cwd=REPO_ROOT).stdout.strip()
    base = torch.load(REPO_ROOT / a.base, map_location="cpu")
    parts, src = [], []
    for f in a.falls:
        d = torch.load(REPO_ROOT / f, map_location="cpu")
        if int((d["kind"] != 2).sum()):
            raise ValueError(f"{f} に kind 2 以外の状態がある")
        parts.append(d)
        src.append({"file": f, "sha256": sha256(REPO_ROOT / f), "count": int(len(d["u0"])), "meta": d["meta"]})
    F = {k: torch.cat([p[k] for p in parts]) for k in KEYS}
    F["pos"][:, :2] = 0.0
    n = len(F["u0"])
    g = torch.Generator().manual_seed(a.seed)
    ev = torch.zeros(n, dtype=torch.bool)
    ev[torch.randperm(n, generator=g)[: int(round(n * a.eval_frac))]] = True
    out = {k: torch.cat([base[k], F[k]]) for k in KEYS}
    out["eval"] = torch.cat([base["eval"], ev])
    out["meta"] = dict(base["meta"], base=a.base, falls=[s["file"] for s in src])
    from pathlib import Path
    path = Path(a.out) if Path(a.out).is_absolute() else OUT_DIR / a.out   # 絶対パスは動作確認用（MANIFEST に書かない）
    torch.save(out, path)
    u0 = F["u0"]
    if Path(a.out).is_absolute():
        print(f"-> {path}（動作確認用、MANIFEST には書かない）")
        return 0
    man_p = OUT_DIR / "MANIFEST.json"
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    man[a.out] = {
        "created": dt.datetime.now().isoformat(timespec="seconds"), "generator": "getup/tools/make_bank_v2.py",
        "generator_commit": git("rev-parse", "--short", "HEAD"), "generator_dirty": bool(git("status", "--porcelain", "--", "getup")),
        "seed": a.seed, "sha256": sha256(path), "base": a.base, "base_sha256": sha256(REPO_ROOT / a.base),
        "count": {"base": int(len(base["u0"])), "falls": n, "falls_train": int((~ev).sum()), "falls_eval": int(ev.sum())},
        "u0_falls": {"ge_0.9": int((u0 >= 0.9).sum()), "ge_0.5": int((u0 >= 0.5).sum()), "ge_0": int((u0 >= 0).sum()),
                     "lt_0": int((u0 < 0).sum())},
        "falls_sources": src,
        "note": "番号 0〜23,999 は bank_v1 と同じ（学習用・評価用の分け方も同じ）。その後ろが歩行中の転倒 F（kind 2）。",
    }
    man_p.write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n")
    print(f"-> {path}（bank_v1 {len(base['u0'])} ＋ F {n}、F の評価用 {int(ev.sum())}）")
    print(json.dumps(man[a.out]["u0_falls"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
