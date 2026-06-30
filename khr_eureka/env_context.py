"""LLM に渡す「環境コンテキスト」。

Eureka の environment-as-context に相当。KHREnv のうち、報酬関数から参照してよい
状態テンソル（step() 実行直後に更新済みのもの）と、報酬関数が満たすべき契約を記述する。
ここは KHR-3HV 二足歩行タスク専用に手書きで要約している（khr_env.py と整合させること）。
"""

# 報酬関数が参照できる self.* の一覧（step() 後に最新化される）。
ENV_STATE_CONTEXT = r'''
You are designing the reward for a KHR-3HV small humanoid robot (12 actuated leg DoFs)
learning to WALK while tracking velocity commands, simulated in Genesis with rsl_rl PPO.
Control runs at 50 Hz (self.dt = 0.02 s). num_envs parallel copies run on GPU.

Inside the reward function, `self` is the environment instance. All tensors below are
already updated for the CURRENT timestep and live on `self.device`. Shapes use
N = self.num_envs.

# Base (torso) state, expressed in the robot's local/base frame unless noted
self.base_pos          : (N, 3)  world position of base; self.base_pos[:, 2] is height [m]
self.base_quat         : (N, 4)  base orientation quaternion (w, x, y, z)
self.base_euler        : (N, 3)  roll, pitch, yaw in DEGREES (relative to init orientation)
self.base_lin_vel      : (N, 3)  linear velocity in base frame [m/s]
self.base_ang_vel      : (N, 3)  angular velocity in base frame [rad/s]
self.projected_gravity : (N, 3)  gravity unit vector in base frame; [0,0,-1] when upright

# Commands the policy must follow (target velocities)
self.commands          : (N, 3)  [target_lin_vel_x, target_lin_vel_y, target_ang_vel_yaw]

# Joint (DoF) state for the 12 leg joints (order = self.env_cfg["joint_names"])
self.dof_pos           : (N, 12) joint angles [rad]
self.dof_vel           : (N, 12) joint angular velocities [rad/s]
self.last_dof_vel      : (N, 12) previous-step joint velocities [rad/s]
self.default_dof_pos   : (12,)   nominal standing/crouch pose [rad]
self.actions           : (N, 12) current policy actions (position targets, scaled)
self.last_actions      : (N, 12) previous-step actions

# Feet / contacts
self.contact_forces    : (N, n_links, 3) net contact force per link [N]
self.feet_indices      : list[int] local link indices of [left_foot, right_foot]
self.feet_pos          : (N, 2, 3) world positions of the two feet
self.feet_vel          : (N, 2, 3) world linear velocities of the two feet
self.l_ankle_pos       : (N, 3) world position of left ankle
self.r_ankle_pos       : (N, 3) world position of right ankle

# Gait phase (period 0.8 s, left/right are anti-phase by 0.5)
self.leg_phase         : (N, 2) phase in [0,1) for [left, right]; <0.55 => stance, >=0.55 => swing
self.sin_phase         : (N, 1) sin(2*pi*phase)
self.cos_phase         : (N, 1) cos(2*pi*phase)

# Useful constants / config
self.dt                : float, 0.02
self.num_envs          : int
self.device            : torch device
self.reward_cfg["base_height_target"]  : float (~0.2395 m) nominal torso height
self.reward_cfg["feet_height_target"]  : float (~0.035 m) target swing-foot clearance
self.command_cfg["lin_vel_x_range"], ["lin_vel_y_range"], ["ang_vel_range"]

# You may call torch ops and robot getters such as
#   self.robot.get_dofs_control_force()  -> (N, n_dofs) applied joint torques [Nm]
'''

# 報酬関数の出力契約（Eureka の reward_signature に相当）。
REWARD_CONTRACT = r'''
Write a single Python function with EXACTLY this signature:

    def compute_reward(self):
        # ... your code using torch and self.* ...
        return total_reward, reward_components

Requirements:
- `total_reward` is a torch.Tensor of shape (self.num_envs,) on self.device, dtype float.
- `reward_components` is a dict[str, torch.Tensor], each value shape (self.num_envs,), giving
  the (already weighted, per-step) contribution of each named term. The SUM of all component
  tensors MUST equal total_reward. These components are logged and shown back to you for
  reflection, so name them clearly (e.g. "tracking_lin_vel", "alive", "action_rate").
- Use torch tensors only (no numpy). Create new tensors on self.device.
- Multiply each term by self.dt is NOT required (the env does not rescale your output);
  choose absolute per-step weights yourself.
- Do NOT import anything, do NOT read files, do NOT print. `torch` and `math` are available
  in the namespace. Do NOT define any function other than compute_reward.
- Encourage: following self.commands (xy linear + yaw angular velocity), staying upright,
  a periodic stable gait, and not falling. Discourage: large jerky actions, excessive joint
  velocity/torque, deviating from a reasonable posture.
- The episode terminates if |roll|>50deg, |pitch|>50deg, or the feet cross
  (horizontal ankle distance < 0.085 m), so an "alive"/upright term is usually helpful.
'''


def build_env_context() -> str:
    return ENV_STATE_CONTEXT.strip() + "\n\n" + REWARD_CONTRACT.strip()
