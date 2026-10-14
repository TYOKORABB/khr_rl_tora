"""Eureka のプロンプト群（KHR 二足歩行タスク向けに調整）.

原典 eureka-research/Eureka の initial_system / code_output_tip / policy_feedback /
execution_error_feedback を参考に、Genesis+rsl_rl+KHR の文脈へ書き換えたもの。
"""
import re

from .env_context import build_env_context

SYSTEM_PROMPT = """You are a reward engineer trying to write reward functions to solve \
reinforcement learning tasks as effectively as possible.
Your goal is to write a reward function for the environment that will help the agent learn \
the task described in text. Your reward function should use useful variables from the \
environment as inputs. As an example, the reward function signature can be:
    def compute_reward(self):
        ...
        return total_reward, reward_components
Make sure any new tensor or variable you introduce is on the same device as the environment \
tensors (self.device). The code output should be formatted as a single python code string \
inside a ```python ... ``` block. Use only torch (and math); do not import anything.
"""

TASK_DESCRIPTION = """The task is: make the KHR-3HV small humanoid WALK on flat ground with a \
gait that TRANSFERS TO THE REAL ROBOT (sim-to-real). The learned policy will be deployed on a \
PHYSICAL KHR-3HV servo robot via the Meridian interface at 50 Hz. Therefore a SMOOTH, gentle, \
hardware-feasible gait matters as much as speed. Concretely, the policy must:
- TRACK the commanded base velocities in self.commands (forward/lateral linear velocity in \
m/s and yaw angular velocity in rad/s). Commands stay within a real-robot-safe range \
(|vx|,|vy| <= 0.2 m/s, |yaw| <= 0.5 rad/s). Walk at the commanded speed (do not just shuffle), \
and also follow turning and sideways commands.
- Be SMOOTH and HARDWARE-FRIENDLY (this is critical): small changes in actions between steps \
(low action-rate / jerk), low joint velocities and joint accelerations, low joint torques, and \
a posture close to the natural default pose. High-frequency, jittery, or high-torque motions \
destroy real servos and do NOT transfer. Aim to be as smooth as a carefully hand-tuned \
controller while walking faster than a slow one.
- Stay STABLE: torso upright, base height near nominal (~0.24 m), minimal vertical bouncing and \
roll/pitch oscillation, feet making clean periodic contact with little slip.
- Be ROBUST to model mismatch: domain randomization (friction, base mass, center of mass), \
observation noise, and a 1-step action latency are active; the gait must not fall under them.
Produce a natural, periodic, energy-efficient walking gait without falling."""


def build_initial_user_prompt() -> str:
    return (
        "The Python environment exposes the following state to your reward function:\n\n"
        f"{build_env_context()}\n\n"
        f"{TASK_DESCRIPTION}\n\n"
        "Write the compute_reward function. Output ONLY a single ```python code block "
        "containing the function definition (and nothing else)."
    )


REFLECTION_TIPS = """Some helpful tips for analyzing the policy feedback:
(1) If the success/fitness metric is stagnant or worsening, you should rethink the reward: \
rescale components, change their functional form (e.g. exp(-error) vs -error^2), or add \
new terms.
(2) If a reward component's value is nearly constant or saturates, it is uninformative — \
rescale its temperature/weight or redesign it.
(3) If a component's magnitude dominates all others, downweight it so the agent does not \
ignore the rest.
(4) Keep components on comparable scales. Velocity-tracking should remain a primary positive \
signal; penalties (action rate, torque, posture) should be small enough not to suppress walking.
(5) An explicit "alive"/upright reward and a swing-foot clearance term usually help bipedal walking.
(6) STABLE: if stability/upright is low, base height drifts from ~0.24 m, or vertical bounce is \
high, add/strengthen terms for upright torso (self.projected_gravity[:, :2] -> 0), base-height \
tracking, and small |base_lin_vel[:, 2]| and roll/pitch angular velocity.
(7) SPEED: velocity tracking should reward matching the commanded speed within +/-0.2 m/s (use \
exp(-error) on the command vector). Reward actually moving when commanded, but do NOT reward \
speed beyond the command.
(8) SMOOTHNESS / SIM-TO-REAL (highest priority when action_rate >> 1): the gait must run on \
real servos. Add meaningful penalties on action-rate (sum of squared self.actions - \
self.last_actions), joint velocity (self.dof_vel), joint acceleration ((self.dof_vel - \
self.last_dof_vel)/self.dt), and joint torque (self.robot.get_dofs_control_force()), plus a term \
keeping the pose near self.default_dof_pos. A hand-tuned baseline achieves action_rate ~1.0; if \
yours is far higher, INCREASE these penalties. Encourage a symmetric periodic gait via \
self.leg_phase / self.sin_phase. Balance is key: make smoothing penalties strong enough to kill \
jitter, but not so strong that the robot stops stepping. The winning gait is BOTH smooth AND \
walking at the commanded speed."""


def build_reflection_user_prompt(prev_reward_code: str, feedback: str) -> str:
    return (
        "We trained an RL policy using the reward function you provided and evaluated it.\n\n"
        "The reward function was:\n"
        f"```python\n{prev_reward_code}\n```\n\n"
        f"{feedback}\n\n"
        f"{REFLECTION_TIPS}\n\n"
        "Based on this, write an IMPROVED compute_reward function. "
        "Output ONLY a single ```python code block containing the new function definition."
    )


def build_execution_error_prompt(prev_reward_code: str, error_text: str) -> str:
    return (
        "The reward function you provided FAILED to execute / train. The code was:\n"
        f"```python\n{prev_reward_code}\n```\n\n"
        f"The traceback / error was:\n```\n{error_text[:2000]}\n```\n\n"
        "Fix the bug and output ONLY a single ```python code block with a corrected "
        "compute_reward function."
    )


_CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)


def extract_reward_code(llm_text: str) -> str:
    """LLM 応答から ```python ...``` のコード本体を取り出す。

    フェンスが無い場合は def compute_reward 以降を拾うフォールバック。
    """
    blocks = _CODE_BLOCK_RE.findall(llm_text)
    if blocks:
        # compute_reward を含むブロックを優先
        for b in blocks:
            if "def compute_reward" in b:
                return b.strip()
        return blocks[0].strip()
    idx = llm_text.find("def compute_reward")
    if idx != -1:
        return llm_text[idx:].strip()
    raise ValueError("LLM 応答から compute_reward のコードを抽出できませんでした。")
