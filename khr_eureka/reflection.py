"""学習結果から reward reflection フィードバック文字列を構築する.

Eureka の policy_feedback に相当。各報酬成分の統計（mean/max/min）と、
タスク fitness（速度追従・生存率・直立）を LLM に提示し、改善を促す。
"""


def build_feedback(eval_result: dict, rl_iterations: int) -> str:
    cs = eval_result.get("component_stats", {})
    lines = [
        f"We trained the policy for {rl_iterations} PPO iterations and then evaluated it.",
        "",
        "Held-out TASK metrics (these define the fitness we maximize; not part of your reward):",
        f"  - fitness (higher is better)      : {eval_result['fitness']:.4f}",
        f"  - velocity_tracking_score (~0..1.5): {eval_result['track_mean']:.4f}",
        f"  - upright_score (1=upright,0=fell): {eval_result['upright_mean']:.4f}",
        f"  - survival_fraction (1=never falls): {eval_result['survival_frac']:.4f}",
        f"  - mean of your total_reward        : {eval_result['total_reward_mean']:.4f}",
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
