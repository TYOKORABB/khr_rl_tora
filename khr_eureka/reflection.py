"""学習結果から reward reflection フィードバック文字列を構築する.

Eureka の policy_feedback に相当。各報酬成分の統計（mean/max/min）と、
タスク fitness（速度/方向追従・旋回追従・安定・生存）を LLM に提示し、改善を促す。
目標は「安定して・速く・頑健に」歩くこと。
"""


def build_feedback(eval_result: dict, rl_iterations: int) -> str:
    cs = eval_result.get("component_stats", {})
    lines = [
        f"We trained the policy for {rl_iterations} PPO iterations, then evaluated it under a "
        f"MIXED command distribution designed to test STABLE + FAST + ROBUST walking:",
        "  ~50% brisk forward (vx 0.15-0.30 m/s), ~20% forward+turn (yaw +/-0.25-0.45 rad/s),",
        "  ~15% diagonal (vx + vy), ~15% sideways (vy dominant). Domain randomization (friction,",
        "  base mass, COM) is active, so the policy must generalize.",
        "",
        "Held-out TASK metrics (these define the fitness we maximize; NOT part of your reward).",
        "fitness = survival_fraction * (0.60*progress + 0.20*yaw_tracking + 0.20*stability).",
        "Goal: STABLE, FAST, ROBUST command-following gait. Falling drives fitness ~0; merely",
        "standing gives ~0 progress; a fast but bouncy/tilting gait loses stability.",
        f"  - fitness (higher is better)          : {eval_result['fitness']:.4f}",
        f"  - progress (0=not moving,1=at cmd vel): {eval_result['progress_mean']:.4f}   <-- primary (speed & direction)",
        f"  - mean_forward_speed [m/s]            : {eval_result['mean_fwd_speed']:.4f}   (commanded up to 0.30)",
        f"  - yaw_tracking (1=matches turn/straight): {eval_result['yaw_track_mean']:.4f}",
        f"  - stability (1=upright,on-height,calm): {eval_result['stability_mean']:.4f}",
        f"  - survival_fraction (1=never falls)   : {eval_result['survival_frac']:.4f}",
        "",
        "Auxiliary diagnostics (for tuning stability/robustness; not directly in fitness):",
        f"  - upright (1=torso vertical)          : {eval_result.get('upright_mean', float('nan')):.4f}",
        f"  - mean base height [m] (target ~0.24) : {eval_result.get('base_height_mean', float('nan')):.4f}",
        f"  - vertical bounce RMS [m/s] (lower=better): {eval_result.get('vbounce_rms', float('nan')):.4f}",
        f"  - action_rate (jerkiness, lower=smoother): {eval_result.get('action_rate_mean', float('nan')):.4f}",
        f"  - mean of your total_reward           : {eval_result['total_reward_mean']:.4f}",
        "",
        "How to read this:",
        "  (a) progress & mean_forward_speed near 0 while survival high => robot STANDS STILL: "
        "strengthen linear-velocity tracking and a real stepping gait.",
        "  (b) mean_forward_speed high but survival ~0 => robot LUNGES/FALLS: add stability "
        "(upright, base-height ~0.24, low vertical bounce, controlled foot contact); do NOT reward "
        "speed beyond the commanded velocity.",
        "  (c) survival high & progress ok but stability/upright low or vbounce high => gait is "
        "UNSTABLE/BOUNCY: penalize vertical velocity, base-height error, and torso tilt.",
        "  (d) action_rate large => JITTERY actions (bad for the real robot): add an action-rate / "
        "joint-velocity penalty, but keep it small so it does not suppress stepping.",
        "  (e) yaw_tracking low => cannot follow turn commands / drifts: reward matching commanded "
        "yaw angular velocity.",
        "",
        "Per-component statistics of YOUR reward over the evaluation (per-step mean / max / min):",
    ]
    if cs:
        for name, st in cs.items():
            lines.append(
                f"  - {name:<22}: mean={st['mean']:+.4f}  max={st['max']:+.4f}  min={st['min']:+.4f}"
            )
    else:
        lines.append("  (no components were reported — make sure to return a components dict)")
    return "\n".join(lines)


def build_failure_feedback(error_text: str) -> str:
    return (
        "Training/evaluation FAILED with this reward function. "
        "Treat fitness as -inf for this candidate.\n"
        f"Error:\n{error_text[:1500]}"
    )
