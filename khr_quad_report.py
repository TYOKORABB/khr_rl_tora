"""四足学習の研究記録を自動生成する（設定・メトリクス・推移を収集して整理）。

logs/<exp>/ の成果物（cfgs.pkl / run_info.json / tensorboard events）を解析し、
experiments/<exp>/ に人間可読なレポートと CSV を出力する。さらに全実験の一覧を
experiments/INDEX.md に追記していく。**Genesis / GPU を一切使わない**ので、学習を
GPU で実行中でも安全に併走できる（ファイル読み取りのみ）。

使い方:
    python khr_quad_report.py -e khr-quadruped          # 単発でレポート生成
    # khr_train_quad.py の学習終了時にも自動で generate() が呼ばれる

出力:
    experiments/<exp>/report.md    … 設定・最終メトリクス・推移・所見
    experiments/<exp>/metrics.csv  … 全スカラーの時系列（後でプロット可能）
    experiments/INDEX.md           … 実験ごとに1行追記される履歴台帳
"""

import argparse
import csv
import datetime
import json
import os
import pickle
import subprocess

EXPERIMENTS_DIR = "experiments"

# レポートに出す主要メトリクスと日本語ラベル
KEY_METRICS = [
    ("Train/mean_reward", "平均報酬"),
    ("Train/mean_episode_length", "エピソード長(最大は episode_length_s/dt)"),
    ("Episode/rew_tracking_lin_vel", "前進追従報酬"),
    ("Episode/rew_tracking_ang_vel", "旋回追従報酬"),
    ("Policy/mean_std", "ポリシー標準偏差(探索量)"),
]


def _git(*args):
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _load_scalars(log_dir):
    """tensorboard events から {tag: [(step, value), ...]} を取り出す。"""
    from tensorboard.backend.event_processing import event_accumulator

    ea = event_accumulator.EventAccumulator(log_dir, size_guidance={event_accumulator.SCALARS: 0})
    ea.Reload()
    data = {}
    for tag in ea.Tags().get("scalars", []):
        data[tag] = [(s.step, s.value) for s in ea.Scalars(tag)]
    return data


def _nearest(series, target_step):
    """series=[(step,val)] から target_step に最も近い点の (step, val) を返す。"""
    if not series:
        return None, None
    i = min(range(len(series)), key=lambda k: abs(series[k][0] - target_step))
    return series[i]


def _fmt(v, nd=4):
    return "n/a" if v is None else f"{v:.{nd}f}"


def _milestones(max_step):
    base = [0, 100, 250, 500, 1000, 1500, 2000, 3000, 4000, 5000, 7500, 10000]
    ms = [m for m in base if m <= max_step]
    if max_step not in ms:
        ms.append(max_step)
    return ms


def _write_metrics_csv(scalars, path):
    """全スカラーを step 横断のワイド表として CSV 出力。"""
    tags = sorted(scalars.keys())
    # step -> {tag: val}
    table = {}
    for tag in tags:
        for step, val in scalars[tag]:
            table.setdefault(step, {})[tag] = val
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step"] + tags)
        for step in sorted(table.keys()):
            row = [step] + [table[step].get(tag, "") for tag in tags]
            w.writerow(row)


def _judgment(scalars):
    """簡易な自動所見（歩けているかの目安）。"""
    el = scalars.get("Train/mean_episode_length", [])
    tv = scalars.get("Episode/rew_tracking_lin_vel", [])
    if not el:
        return "メトリクス不足で判定不可。"
    first_el = el[0][1]
    last_el = el[-1][1]
    max_el = max(v for _, v in el)
    lines = []
    lines.append(f"- エピソード長: 開始 {first_el:.1f} → 最終 {last_el:.1f}（最大 {max_el:.1f}）")
    if last_el > first_el * 1.5 and last_el > 50:
        lines.append("- ✅ エピソード長が明確に伸びており、転倒せず立てる時間が増えている（学習が進行）。")
    elif max_el > first_el * 1.5:
        lines.append("- △ 一時的に伸びたが最終では戻り気味。途中のチェックポイントが良い可能性。")
    else:
        lines.append("- ❌ エピソード長がほぼ横ばい。まだ自立/歩行を獲得できていない可能性が高い。")
    if tv:
        last_tv = tv[-1][1]
        max_tv = max(v for _, v in tv)
        lines.append(f"- 前進追従報酬: 最終 {last_tv:.4f}（最大 {max_tv:.4f}）")
    return "\n".join(lines)


def generate(exp_name, log_root="logs", quiet=False):
    """experiments/<exp>/ に記録を生成し、INDEX に追記する。パスは cwd 基準。"""
    log_dir = os.path.join(log_root, exp_name)
    if not os.path.isdir(log_dir):
        raise FileNotFoundError(f"ログが見つかりません: {log_dir}")

    # --- 収集 ---
    with open(os.path.join(log_dir, "cfgs.pkl"), "rb") as f:
        env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(f)

    run_info = {}
    ri_path = os.path.join(log_dir, "run_info.json")
    if os.path.exists(ri_path):
        with open(ri_path) as f:
            run_info = json.load(f)

    scalars = _load_scalars(log_dir)
    max_step = max((s[-1][0] for s in scalars.values() if s), default=0)

    ckpts = sorted(
        (int(fn[len("model_"):-3]) for fn in os.listdir(log_dir)
         if fn.startswith("model_") and fn.endswith(".pt")),
    )

    # --- 出力先 ---
    out_dir = os.path.join(EXPERIMENTS_DIR, exp_name)
    os.makedirs(out_dir, exist_ok=True)
    _write_metrics_csv(scalars, os.path.join(out_dir, "metrics.csv"))

    now = datetime.datetime.now().isoformat(timespec="seconds")
    cur_sha = _git("rev-parse", "--short", "HEAD")
    cur_dirty = bool(_git("status", "--porcelain"))

    alg = train_cfg.get("algorithm", {})
    actor = train_cfg.get("actor", {})
    dist = actor.get("distribution_cfg", {})

    # --- report.md 生成 ---
    L = []
    L.append(f"# 実験レポート: {exp_name}")
    L.append("")
    L.append(f"- レポート生成日時: {now}")
    L.append(f"- 学習到達 iteration: {max_step}")
    if run_info:
        L.append(f"- 学習開始: {run_info.get('started_at','?')}  "
                 f"(num_envs={run_info.get('num_envs','?')}, "
                 f"max_iterations={run_info.get('max_iterations','?')}, seed={run_info.get('seed','?')})")
        L.append(f"- 学習時の git: `{run_info.get('git_sha','?')}`"
                 f"{' (未コミット変更あり)' if run_info.get('git_dirty') else ''}")
    L.append(f"- レポート時の git: `{cur_sha}`{' (未コミット変更あり)' if cur_dirty else ''}")
    L.append("")

    L.append("## 自動所見")
    L.append(_judgment(scalars))
    L.append("")

    L.append("## 主要ハイパーパラメータ")
    L.append("")
    L.append("| 項目 | 値 |")
    L.append("|---|---|")
    hp = [
        ("num_actions", env_cfg.get("num_actions")),
        ("action_scale", env_cfg.get("action_scale")),
        ("kp / kd", f"{env_cfg.get('kp')} / {env_cfg.get('kd')}"),
        ("gait_period[s]", env_cfg.get("gait_period", "(env コード側 / cfg未記録)")),
        ("init_std", dist.get("init_std")),
        ("entropy_coef", alg.get("entropy_coef")),
        ("learning_rate", alg.get("learning_rate")),
        ("gamma / lam", f"{alg.get('gamma')} / {alg.get('lam')}"),
        ("hidden_dims", actor.get("hidden_dims")),
        ("base_init_pos", env_cfg.get("base_init_pos")),
        ("base_init_quat", env_cfg.get("base_init_quat")),
        ("termination pitch/roll/height",
         f"{env_cfg.get('termination_if_pitch_greater_than')} / "
         f"{env_cfg.get('termination_if_roll_greater_than')} / "
         f"{env_cfg.get('termination_if_height_smaller_than')}"),
        ("command x/y/yaw range",
         f"{command_cfg.get('lin_vel_x_range')} / {command_cfg.get('lin_vel_y_range')} / {command_cfg.get('ang_vel_range')}"),
    ]
    for k, v in hp:
        L.append(f"| {k} | {v} |")
    L.append("")

    L.append("## 報酬スケール")
    L.append("")
    L.append("| 報酬項 | scale |")
    L.append("|---|---|")
    for k, v in reward_cfg.get("reward_scales", {}).items():
        L.append(f"| {k} | {v} |")
    L.append(f"| (base_height_target) | {reward_cfg.get('base_height_target')} |")
    L.append(f"| (feet_height_target) | {reward_cfg.get('feet_height_target')} |")
    L.append("")

    L.append("## メトリクス推移（主要指標）")
    L.append("")
    ms = _milestones(max_step)
    header = "| iter | " + " | ".join(label for _, label in KEY_METRICS) + " |"
    L.append(header)
    L.append("|" + "---|" * (len(KEY_METRICS) + 1))
    for m in ms:
        cells = []
        for tag, _ in KEY_METRICS:
            _, val = _nearest(scalars.get(tag, []), m)
            cells.append(_fmt(val))
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("")

    L.append("## 全スカラーの最終値")
    L.append("")
    L.append("| tag | 最終値 | 最小 | 最大 |")
    L.append("|---|---|---|---|")
    for tag in sorted(scalars.keys()):
        s = scalars[tag]
        if not s:
            continue
        vals = [v for _, v in s]
        L.append(f"| {tag} | {_fmt(vals[-1])} | {_fmt(min(vals))} | {_fmt(max(vals))} |")
    L.append("")

    L.append("## チェックポイント")
    L.append("")
    if ckpts:
        L.append(f"- 保存数: {len(ckpts)}  範囲: model_{ckpts[0]}.pt 〜 model_{ckpts[-1]}.pt")
        L.append(f"- 一覧: {', '.join(str(c) for c in ckpts)}")
    else:
        L.append("- チェックポイントなし")
    L.append("")
    L.append(f"（詳細な時系列は `{os.path.join(out_dir, 'metrics.csv')}` を参照）")
    L.append("")

    report_path = os.path.join(out_dir, "report.md")
    with open(report_path, "w") as f:
        f.write("\n".join(L))

    # --- INDEX.md に追記 ---
    _update_index(exp_name, now, max_step, cur_sha, run_info, scalars)

    if not quiet:
        print(f"[report] 生成完了: {report_path}")
        print(f"[report] CSV     : {os.path.join(out_dir, 'metrics.csv')}")
        print(f"[report] INDEX   : {os.path.join(EXPERIMENTS_DIR, 'INDEX.md')}")
    return report_path


def _update_index(exp_name, now, max_step, sha, run_info, scalars):
    os.makedirs(EXPERIMENTS_DIR, exist_ok=True)
    index_path = os.path.join(EXPERIMENTS_DIR, "INDEX.md")

    def last(tag):
        s = scalars.get(tag, [])
        return f"{s[-1][1]:.3f}" if s else "n/a"

    def best(tag):
        s = scalars.get(tag, [])
        return f"{max(v for _, v in s):.1f}" if s else "n/a"

    header = (
        "# 実験履歴 INDEX\n\n"
        "四足学習(khr_train_quad.py)の実行ごとに1行追記される台帳。詳細は "
        "`experiments/<exp>/report.md`。\n\n"
        "| 生成日時 | 実験名 | iter | git | 最終報酬 | 最終ep長 | 最大ep長 | 最終前進追従 |\n"
        "|---|---|---|---|---|---|---|---|\n"
    )
    row = (
        f"| {now} | {exp_name} | {max_step} | `{sha}` | "
        f"{last('Train/mean_reward')} | {last('Train/mean_episode_length')} | "
        f"{best('Train/mean_episode_length')} | {last('Episode/rew_tracking_lin_vel')} |\n"
    )
    if not os.path.exists(index_path):
        with open(index_path, "w") as f:
            f.write(header + row)
    else:
        with open(index_path, "a") as f:
            f.write(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exp_name", type=str, default="khr-quadruped")
    args = parser.parse_args()
    generate(args.exp_name)


if __name__ == "__main__":
    main()
