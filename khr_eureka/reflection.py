"""学習結果から reward reflection フィードバック文字列を構築する.

Eureka の policy_feedback に相当。各報酬成分の統計（mean/max/min）と、
タスク fitness（速度追従・生存率・直立）を LLM に提示し、改善を促す。
"""


def build_feedback(eval_result: dict, rl_iterations: int) -> str:
    cs = eval_result.get("component_stats", {})
    lines = [
        f"We trained the policy for {rl_iterations} PPO iterations, then evaluated it while "
        f"COMMANDING a constant FORWARD walk (commanded vx ~0.10-0.20 m/s, vy=0, yaw=0).",
        "",
        "Held-out TASK metrics (these define the fitness we maximize; NOT part of your reward).",
        "The key goal is ACTUAL FORWARD LOCOMOTION, not merely standing upright:",
        f"  - fitness (higher is better)        : {eval_result['fitness']:.4f}",
        f"  - progress (0=not moving, 1=at cmd) : {eval_result['progress_mean']:.4f}   <-- primary",
        f"  - mean_forward_speed [m/s]          : {eval_result['mean_fwd_speed']:.4f}   (target ~0.1-0.2)",
        f"  - yaw_tracking (1=goes straight)    : {eval_result['yaw_track_mean']:.4f}",
        f"  - survival_fraction (1=never falls) : {eval_result['survival_frac']:.4f}",
        f"  - mean of your total_reward         : {eval_result['total_reward_mean']:.4f}",
        "",
        "Interpretation: if progress / mean_forward_speed are near 0 while survival is high, "
        "the robot is just STANDING STILL instead of walking — strengthen forward-velocity "
        "tracking and add/strengthen terms that reward actually moving and a stepping gait.",
        "",
        "Per-component statistics of YOUR reward over the evaluation "
        "(per-step mean / max / min):",
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
