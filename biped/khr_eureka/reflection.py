"""学習結果から reward reflection フィードバック文字列を構築する.

Eureka の policy_feedback に相当。各報酬成分の統計（mean/max/min）と、
タスク fitness（速度/方向追従・旋回追従・安定・生存）を LLM に提示し、改善を促す。
目標は「安定して・速く・頑健に」歩くこと。
"""


def build_feedback(eval_result: dict, rl_iterations: int) -> str:
    cs = eval_result.get("component_stats", {})
    lines = [
        f"We trained the policy for {rl_iterations} PPO iterations, then evaluated it under a "
        f"MIXED command distribution. The OVERRIDING GOAL is SIM-TO-REAL: this gait will be "
        f"deployed on a PHYSICAL KHR-3HV servo robot (via Meridian, 50 Hz PD control). So it must "
        f"be SMOOTH and gentle on the servos, not just fast in simulation.",
        "  Commands (all within the real-robot-safe +/-0.2 m/s range): ~50% forward (vx 0.12-0.20),",
        "  ~20% forward+turn (yaw +/-0.25-0.45), ~15% diagonal, ~15% sideways. Domain randomization",
        "  (friction, base mass, COM), observation noise, and 1-step action latency are active, so",
        "  the policy must be ROBUST to model mismatch (that is what makes it transfer to hardware).",
        "",
        "Held-out TASK metrics (these define the fitness we maximize; NOT part of your reward).",
        "fitness = survival * (0.40*progress + 0.15*yaw + 0.20*stability + 0.25*SMOOTHNESS).",
        "SMOOTHNESS = exp(-action_rate/6) rewards low action jerk; it is a FIRST-CLASS objective "
        "because jittery, high-jerk motion wears out / burns the real servos and does NOT transfer. "
        "A fast but jittery gait now scores WORSE than a smooth, slightly-slower one.",
        f"  - fitness (higher is better)          : {eval_result['fitness']:.4f}",
        f"  - progress (0=not moving,1=at cmd vel): {eval_result['progress_mean']:.4f}   (speed & direction, +/-0.2 range)",
        f"  - mean_forward_speed [m/s]            : {eval_result['mean_fwd_speed']:.4f}",
        f"  - yaw_tracking (1=matches turn/straight): {eval_result['yaw_track_mean']:.4f}",
        f"  - stability (1=upright,on-height,calm): {eval_result['stability_mean']:.4f}",
        f"  - SMOOTHNESS (1=smooth,0=jittery)     : {eval_result.get('smoothness_mean', float('nan')):.4f}   <-- sim2real critical",
        f"  - survival_fraction (1=never falls)   : {eval_result['survival_frac']:.4f}",
        "",
        "Auxiliary sim2real diagnostics (reduce these for a hardware-friendly gait):",
        f"  - action_rate (action jerk, lower=smoother): {eval_result.get('action_rate_mean', float('nan')):.4f}   (a hand-tuned baseline reaches ~1.0)",
        f"  - joint torque^2 sum (servo load, lower better): {eval_result.get('torque_sq_mean', float('nan')):.2f}",
        f"  - joint vel^2 sum (servo speed, lower better)  : {eval_result.get('dof_vel_sq_mean', float('nan')):.4f}",
        f"  - upright (1=torso vertical)          : {eval_result.get('upright_mean', float('nan')):.4f}",
        f"  - mean base height [m] (target ~0.24) : {eval_result.get('base_height_mean', float('nan')):.4f}",
        f"  - vertical bounce RMS [m/s] (lower=better): {eval_result.get('vbounce_rms', float('nan')):.4f}",
        f"  - mean of your total_reward           : {eval_result['total_reward_mean']:.4f}",
        "",
        "How to read this:",
        "  (a) progress & mean_forward_speed near 0 while survival high => robot STANDS STILL: "
        "strengthen linear-velocity tracking and a real stepping gait.",
        "  (b) mean_forward_speed high but survival ~0 => robot LUNGES/FALLS: add stability "
        "(upright, base-height ~0.24, low vertical bounce); do NOT reward speed beyond the command.",
        "  (c) SMOOTHNESS low / action_rate high (>>1) => JITTERY, high-frequency actions that "
        "will NOT run on real servos: add stronger action-rate, joint-velocity, joint-acceleration "
        "and torque penalties, and reward staying near the default pose. This is the #1 lever now.",
        "  (d) high torque^2 or joint vel^2 => the gait over-drives the servos: penalize torque and "
        "joint velocity; prefer a lower, more compliant, energy-efficient gait.",
        "  (e) survival high & progress ok but stability/upright low or vbounce high => UNSTABLE/"
        "BOUNCY: penalize vertical velocity, base-height error, torso tilt and roll/pitch ang. vel.",
        "  (f) yaw_tracking low => cannot follow turns / drifts: reward matching commanded yaw.",
        "  IMPORTANT: keep smoothing penalties large enough to matter, but not so large they stop "
        "the robot from stepping. The target is a gait that is BOTH faster than a slow hand-tuned "
        "baseline AND just as smooth/stable.",
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
