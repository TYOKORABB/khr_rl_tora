"""四足歩行 学習スクリプト v7 — 足裏を水平に接地させる（ベタ足歩行）版。

khr_train_quad6.py (v6) からのコピー。環境は足裏水平報酬を実装した khr_quad_env4.py。

動機: v4→v6 で「足の縁で歩く」挙動が悪化していた（実測）。
  後脚の足裏の傾き   v4 12.4度 → v5 22.7度 → v6 24.3度
  ankle_pitch        -6.3  → -15.4 → -34.4 度
  ankle_roll        -12.6  → -29.3 → -29.7 度
  hip_yaw            +6.0  → +18.9 → +20.0 度（脚が外にねじれる）
押し外乱に耐える「踏ん張り姿勢」に流れた副作用で、実機では ankle_roll/hip_yaw が
定格トルク(1.373Nm)を連続使用する原因にもなっていた（発熱・脱調のリスク）。

v6 → v7 の変更点:
  - 環境を khr_quad_env4 に変更（_reward_feet_orientation を追加）
  - reward_scales に "feet_orientation": -1.0 を追加
    足裏法線の水平成分を罰する＝足裏が水平なら 0。push カリキュラムは v6 のまま維持。

既定 exp_name は khr-quadruped7。v1〜v6 の成果物には一切触れない。
"""

# --- 以下、v6 からの継承説明 ---
"""四足歩行 学習スクリプト v6 (1b) — push カリキュラムで頑健化と歩行性能を両立する版。

khr_train_quad5.py (v5, exp=khr-quadruped5) からのコピー。**環境は push カリキュラムを
実装した khr_quad_env3.py を使う**（v5 は khr_quad_env2.py で最初から最大押し）。

背景: v5(最初から最大1.0m/sの押し)は前方・横+y の耐性を +0.5m/s 改善したが、歩行追従が
低下(前進93→69%, 横78→35%, 旋回87→64%)し、後方耐性はやや悪化、最弱の横−yは不変だった。
強い外乱を最初から与えたため守りに入り歩行が鈍った、という頑健性↔性能のトレードオフ。

v5 → v6 の変更点:
  - import 先: khr_quad_env2 → khr_quad_env3（push カリキュラム実装）
  - push_curriculum_steps=50000 を追加。押し強度を step 進行で 0→max へ線形に増やす。
    まず歩行を習得→徐々に押しを強めるので、歩行性能を保ったまま外乱耐性を上げる狙い。
  - 押し間隔・最大強度(3s, 1.0m/s)は v5 のまま。

先行研究: legged_gym の push は curriculum で徐々に強くするのが定番。
既定 exp_name は khr-quadruped6。eval/record/report/push テストはそのまま流用可。
v1〜v5 の成果物(logs, experiments, 学習済みモデル, env)には一切触れない。
"""

import argparse
import json
import os
import pickle
import shutil
from importlib import metadata

try:
    if int(metadata.version("rsl-rl-lib").split(".")[0]) < 5:
        raise ImportError
except (metadata.PackageNotFoundError, ImportError) as e:
    raise ImportError("Please install 'rsl-rl-lib>=5.0.0'.") from e
from rsl_rl.runners import OnPolicyRunner

import genesis as gs

from khr_quad_env4 import KHRQuadEnv  # v7: push カリキュラム + 足裏水平報酬の環境を使う


def get_train_cfg(exp_name):
    train_cfg_dict = {
        "algorithm": {
            "class_name": "PPO",
            "clip_param": 0.2,
            "desired_kl": 0.01,
            "entropy_coef": 0.01,  # 0.002→0.01: 探索(std)の早期崩壊を抑え、歩容発見の機会を残す
            "gamma": 0.99,
            "lam": 0.95,
            "learning_rate": 0.001,
            "max_grad_norm": 1.0,
            "num_learning_epochs": 5,
            "num_mini_batches": 4,
            "schedule": "adaptive",
            "use_clipped_value_loss": True,
            "value_loss_coef": 1.0,
        },
        "actor": {
            "class_name": "MLPModel",
            "hidden_dims": [128, 64, 32],
            "activation": "elu",
            "distribution_cfg": {
                "class_name": "GaussianDistribution",
                "init_std": 0.5,  # 1.0→0.5: 初期探索を穏やかにし、早期に全滅して学習信号が消えるのを防ぐ
                "std_type": "scalar",
            },
        },
        "critic": {
            "class_name": "MLPModel",
            "hidden_dims": [128, 64, 32],
            "activation": "elu",
        },
        "obs_groups": {
            "actor": ["policy"],
            "critic": ["policy","privileged"],
        },
        "num_steps_per_env": 24,
        "save_interval": 100,
        "run_name": exp_name,
        "logger": "tensorboard",
    }

    return train_cfg_dict


def get_cfgs():
    env_cfg = {
        "num_actions": 22,  # 【変更】腕・頭・胸を含めるため12から22へ変更
        # joint/link names
        "default_joint_angles": {  # [rad]
            # --- 前脚（腕） ---
            "l_shoulder_pitch": -1.5708,
            "l_shoulder_roll": 0.0,
            "l_elbow_yaw": 0.0,
            "l_elbow_pitch": 0.0,

            "r_shoulder_pitch": -1.5708,
            "r_shoulder_roll": 0.0,
            "r_elbow_yaw": 0.0,
            "r_elbow_pitch": 0.0,

            # --- 後脚（元の脚） ---
            "l_hip_yaw": 0.0,
            "l_hip_roll": 0.0,
            "l_hip_pitch": -1.671,
            "l_knee_pitch": 0.1,
            "l_ankle_pitch": 0.0,
            "l_ankle_roll": 0.0,

            "r_hip_yaw": 0.0,
            "r_hip_roll": 0.0,
            "r_hip_pitch": -1.671,
            "r_knee_pitch": 0.1,
            "r_ankle_pitch": 0.0,
            "r_ankle_roll": 0.0,

            # --- 胴体・頭 ---
            "c_chest_yaw": 0.0,
            "c_head_yaw": 0.0,
        },
        "joint_names": [
            "l_shoulder_pitch", "l_shoulder_roll", "l_elbow_yaw", "l_elbow_pitch",
            "r_shoulder_pitch", "r_shoulder_roll", "r_elbow_yaw", "r_elbow_pitch",
            "l_hip_yaw", "l_hip_roll", "l_hip_pitch", "l_knee_pitch", "l_ankle_pitch", "l_ankle_roll",
            "r_hip_yaw", "r_hip_roll", "r_hip_pitch", "r_knee_pitch", "r_ankle_pitch", "r_ankle_roll",
            "c_chest_yaw", "c_head_yaw"
        ],

        # PD
        "kp": 25.0,  # 【確認】指定通り25.0
        "kd": 0.5,   # 【確認】指定通り0.5
 
        "armature": 0.01,   # [kgm^2]  default 0.1
        
        # termination
        # base_euler は初期(公称)姿勢からの相対角なので、前傾四足姿勢を基準にそのまま使える。
        "termination_if_roll_greater_than": 50,   # degree（公称姿勢からのロール逸脱）
        "termination_if_pitch_greater_than": 50,  # degree（公称姿勢からのピッチ逸脱）
        "termination_if_height_smaller_than": 0.10,  # m（転倒=胴体が沈み込んだら終了）

        # base pose
        # 【変更】高さを0.197m、y軸周りに+90度回転（[w, x, y, z]）
        "base_init_pos": [0.0, 0.0, 0.197],
        "base_init_quat": [0.7071, 0.0, 0.7071, 0.0], 
        
        "episode_length_s": 20.0,
        "resampling_time_s": 4.0,
        "action_scale": 0.15,  # 0.25→0.15: 1 アクションあたりの関節オフセットを抑え、即転倒しにくくする
        "gait_period": 0.5,    # [s] トロット歩容の1周期（記録・再現のため cfg 化）
        "simulate_action_latency": True,
        "clip_actions": 100.0,
    
        #domain randomization
        'randomize_friction': True,
        'friction_range': [0.1, 1.5],
        'randomize_base_mass': True,
        'mass_range': [-0.1,0.5],
        'randomize_com': True,
        'com_range': [-0.02, 0.02],
        'randomize_kp': False,
        'kp_scale_range': [0.9, 1.1],
        'randomize_kd' : False,
        'kd_scale_range': [0.8, 1.2],

        'push_interval_s': 3,        # 押しの間隔（v5 と同じ）
        'Mode_push_vel': True,       # push 外乱を有効化
        'Mode_push_power': False,
        'max_push_vel_xy': 1.0,      # 押し強度の最終目標[m/s]（カリキュラムで 0→この値へ）
        # v6: push カリキュラム。env.step 呼び出し 50000 回かけて押し強度を 0→max へ線形に上げる。
        # num_steps_per_env=24 なので約 2080 iter で最大に到達（-I 4000 なら約半分の時点）。
        # まず歩行を習得→徐々に押しを強める狙い。0 なら最初から max（=v5 と同挙動）。
        'push_curriculum_steps': 50000,
        'max_push_force': 20, #N（未使用）

    }
    obs_cfg = {
        # actor obs 121 次元 = ang_vel3 + gravity3 + commands3 + dof_pos22 + dof_vel22
        #   + actions22 + cos1 + sin1 + last_actions22 + last_dof_vel22
        "num_obs": 121,
        "obs_scales": {
            "lin_vel": 2.0,
            "ang_vel": 0.25,
            "dof_pos": 1.0,
            "dof_vel": 0.05,

        },

        'add_noise': True,
        "obs_noise": {
            'ang_vel': 0.1,
            "gravity": 0.05,
            "dof_pos": 0.05,
            "dof_vel": 0.1, 
            "action" : 0.0,
        }
    }
    reward_cfg = {
        "tracking_sigma": 0.15,  # v2: 0.25→0.15 速度追従を厳しく（指令速度に届かないと報酬が減る）
        "base_height_target": 0.197,  # 【変更】初期高さに合わせて目標高さを0.197mに修正
        "feet_height_target": 0.06,  # v2: 0.035→0.06 遊脚をしっかり持ち上げ、すり足を減らして自然な歩容に
        "reward_scales": {
            "tracking_lin_vel": 4.0,  # v3: 1.5→4.0 指令速度に合わせることを明確に割に合わせる
            "tracking_ang_vel": 1.0,
            
            "orientation": -5.0, # 環境側で loco 座標系(公称姿勢基準)の重力 xy を使うため前傾姿勢でも整合済み
            "lin_vel_z": -0.1,
            "ang_vel_xy": -0.2,
            "base_height": -10.0,
            "gait_contact" : 0.18,
            "gait_swing": -0.05,
            "contact_no_vel": -0.2,
            "feet_clearance": 0.2,
            "hip_pos": -1.0,
            # v7: 足裏を水平に保たせる（v6は足裏が平均24度傾き縁で歩いていた）
            "feet_orientation": -1.0,
            "alive" : 0.5,

            "action_rate": -0.02,  # v3: -0.05→-0.02 能動的な足運びを許容（滑らかさ罰を緩める）
            "similar_to_default": -0.02,  # v3: -0.1→-0.02 歩行は姿勢を崩すので、この罰を弱める
            "dof_vel": -0.001,
            "acceleration" : -0.00002,  # v3: -0.0001→-0.00002 動的な足運びを抑えすぎないよう1/5に緩める
            "joint_torques":-0.0005,
        },
    }
    command_cfg = {
        # v4(1a): 前進のみ → 全方向歩行へ拡張。x は据え置き、横移動(y)と旋回(yaw)を開放。
        # 追従報酬は既に commands の x/y(tracking_lin_vel) と yaw(tracking_ang_vel) を扱うため
        # 環境コードは変更不要（コマンド範囲を開くだけ）。
        "num_commands": 3,
        "lin_vel_x_range": [0.0, 0.4],     # 前進（v3 のまま。変更を横・旋回の追加だけに限定）
        "lin_vel_y_range": [-0.15, 0.15],  # v4: 横移動を開放（横は前進より難しいので控えめに）
        "ang_vel_range": [-0.5, 0.5],      # v4: その場旋回(yaw)を開放 [rad/s]
    }

    return env_cfg, obs_cfg, reward_cfg, command_cfg

env=[]

def main():
    global env
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exp_name", type=str, default="khr-quadruped7") # v7: 足裏水平化
    parser.add_argument("-B", "--num_envs", type=int, default=4096)
    parser.add_argument("-I","--max_iterations", type=int, default=101)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--view", action='store_true')
    args = parser.parse_args()

    if not args.view:
       print("[No viewer mode] To watch the learing robot, add --view flag.")

    log_dir = f"logs/{args.exp_name}"
    env_cfg, obs_cfg, reward_cfg, command_cfg = get_cfgs()
    train_cfg = get_train_cfg(args.exp_name)

    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir, exist_ok=True)

    with open(f"{log_dir}/cfgs.pkl", "wb") as f:
        pickle.dump([env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg], f)

    # 研究記録用: 実行条件(git/CLI/日時)を run_info.json に残す（学習が途中終了しても残る）
    import datetime as _dt
    import subprocess as _sp

    def _git(*a):
        try:
            return _sp.check_output(["git", *a], text=True, stderr=_sp.DEVNULL).strip()
        except Exception:
            return None

    run_info = {
        "exp_name": args.exp_name,
        "num_envs": args.num_envs,
        "max_iterations": args.max_iterations,
        "seed": args.seed,
        "started_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "git_sha": _git("rev-parse", "--short", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
    }
    with open(f"{log_dir}/run_info.json", "w") as f:
        json.dump(run_info, f, ensure_ascii=False, indent=2)

    gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=args.seed, performance_mode=True)

    env = KHRQuadEnv(
        num_envs=args.num_envs, env_cfg=env_cfg, obs_cfg=obs_cfg, reward_cfg=reward_cfg, command_cfg=command_cfg, show_viewer=args.view
    )

    runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)

    runner.learn(num_learning_iterations=args.max_iterations, init_at_random_ep_len=True)

    # 学習完了後、研究記録(experiments/<exp>/report.md, metrics.csv, INDEX.md)を自動生成
    try:
        import khr_quad_report
        khr_quad_report.generate(args.exp_name)
    except Exception as e:
        print(f"[report] 記録の自動生成に失敗しました（学習自体は完了しています）: {e}")


if __name__ == "__main__":
    main()