"""四足歩行 学習スクリプト v19 — 前進追従を回復させる版（速度不足を実際に痛くする）。

khr_train_quad18.py (v18) のコピー。**環境コードは変更せず設定値のみ**なので
環境は khr_quad_env15.py を流用する（v3/v4 と同じ方針）。

v18 の到達点と残課題:
  ✅ 足裏全面接地を達成（後脚 足裏傾き 21.4→**6.1°**、過去最良）。膝も主動力を維持（ROM 38.5/47.5°）。
  ✅ トルク: ピーク 91→81%、定格90%超 0/22、duty 0/22。
  ❌ **前進追従 57%（実測 0.171 m/s）**。v16 の 75% から戻らず、これが最大の残課題。

診断（なぜ遅いままなのか）:
  トルクは平均18%・ピーク81%・duty 0/22 で**物理的な限界ではない**。
  追従報酬 exp(-err^2/sigma) を計算すると、指令0.3に対し実測0.171（43%不足）でも
      exp(-(0.129)^2/0.15) = **0.895**
  ＝ **最大報酬の 89.5% を獲得できている**。遅くてもほとんど損をしない一方、速く動くと
  action_rate / dof_vel / torque_limits のコストが増えるため、**遅いままが最適解**になっていた。
  これは v2 で経験した「静止でも追従報酬の94%が得られる」のと同じ構造である。

v18 → v19 の変更点（1つの意図＝「速さの限界価値を上げる」を2つのパラメータで実現）:
  - `tracking_sigma` **0.15 → 0.08**（速度不足を実際に痛くする。43%不足時の報酬 0.895→0.812）
  - `tracking_lin_vel` **4.0 → 5.0**
  → 速度に対する報酬の勾配（限界価値）は 6.16 → 13.1 と **約2.1倍**になる。

据え置き（v18 の成果を壊さないため）: `feet_orientation` -3.0 と着地直前の水平要求
（足裏全面接地）、`knee_swing_flexion` 1.8、脚別クリアランス目標、トルク安全策
（torque_limits -5.0 / dof_pos_error -1.0）、base_height -3.0 等。

リスクと監視項目:
  - v2 の教訓では「sigma を厳しくしただけでは かえって遅くなった」。当時は動作系の罰が
    大きかった（action_rate -0.05, similar_to_default -0.1）が、現在は -0.02 と小さいため
    条件が異なる。それでも**遅くなる可能性**は残るので実測で確認する。
  - 速く歩けば**トルクのピークが上がる**（v18 で 81%）。「100%は絶対NG」の要件があるため、
    90%を超えないかを最重要で監視する。超えたら次版で knee/tracking を戻す。
  - 足裏傾き 6.1° が悪化しないか（ユーザ要望の成果）。

既定 exp_name は khr-quadruped19。v1〜v18 の成果物には一切触れない。

--- 以下、v18 の説明 ---
四足歩行 学習スクリプト v18 — 足裏全面で接地させ、膝の可動域を適正化する版。
  knee_swing_flexion 3.0→1.8、feet_orientation -1.0→-3.0＋着地直前(phase>=0.85)からも水平要求。
  足裏傾き 21.4→6.1° と過去最良を達成。膝 ROM は 38.5/47.5° で主動力を維持。

--- 以下、v17 の説明 ---
四足歩行 学習スクリプト v17 — 膝の「swing−stance 差」を報酬にする版（v16の報酬ハック修正）。
  基準を「その脚自身の接地時の膝角度(EMA)」に取り、遊脚中の追加屈曲だけを加点。
  膝 ROM は 2.7→56.2° に増え主動力に復帰したが、ピークトルク91%・追従低下・接地悪化を招いた。

--- 以下、v16 の説明 ---
四足歩行 学習スクリプト v16 — 遊脚期の膝屈曲を直接報酬にする版。※報酬ハックで失敗。
  `_reward_knee_flexion`（位置ベース）を追加したが、膝を目標角度で固定されて ROM が縮小した。

--- 以下、v15 の説明 ---
四足歩行 学習スクリプト v15 — 遊脚を解放し膝を主動力に戻す版。
  `_reward_feet_orientation` を接地時のみに限定（feet_orientation_stance_only）。
  足首負荷は 32%→24% に低下したが膝 ROM は未回復。接地時の足裏傾きは 11.0→13.5° に悪化。

--- 以下、v14 の説明 ---
四足歩行 学習スクリプト v14 — 後脚の「変な力の入れ方」に挑戦（base_height 仮説は反証）。
  base_height -10.0→-3.0（胴体の上下動を許す狙い。結果は上下動 2.0→1.8mm と不変で仮説は棄却）、
  クリアランス目標を脚別テンソル化（前脚 0.012 = v12水準へ復帰 / 後脚 0.02）。

--- 以下、v13 の説明 ---
四足歩行 学習スクリプト v13 — すり足を解消し、足をしっかり上げて歩かせる版。
  feet_clearance を「絶対高さ」から「各足の接地基準からの相対クリアランス」へ修正（前脚は3倍改善）、
  _reward_feet_air_time 新設、contact_no_vel -0.2→-1.0。

--- 以下、v11(失敗) の説明 ---
四足歩行 学習スクリプト v11 — 前進時の yaw ドリフト（首振り）を解消する版。※並進崩壊で不採用。
  _reward_drift の yaw 成分を yaw_drift_weight=5.0 で重み付け（横の5倍）した結果、並進が消えた。

--- 以下、v10 の継承説明 ---
四足歩行 学習スクリプト v10 — 左右対称化・低負荷化でトルク100%飽和と横逸れを止める版。
khr_train_quad9.py (v9) のコピー。環境は khr_quad_env7.py。

v9 の実機安全性フィードバック（教授）と実測診断:
 - 「トルク100%はモーター焼損リスクで絶対NG、負荷はなるべく低く」「前進なのに横に逸れる」
   「ところどころカクッとする」。
 - 実測: 前進時に **右 hip_pitch だけ平均100%張り付き（左は56%）＝左右非対称な歩容**。
   前脚(腕)は平均22%で余裕。横速度 +0.030m/s・yaw +0.028rad/s のドリフト（10秒で16度）。
   → 右hip飽和と横逸れは「片脚に荷重を預ける非対称歩容」という同一原因。

v9 → v10 の変更点（環境 khr_quad_env7、姿勢・トロットは v8/v9 のまま。報酬側で対症）:
  - _reward_leg_load_balance 新設・"leg_load_balance": -1.0（横逸れの根本対策）
      左右後脚の平均トルク負荷(EMA)の差を罰し、片脚集中（右hip100%）を是正。
  - _reward_drift 新設・"drift": -10.0（補助）
      指令からの横速度/旋回のズレを二乗で罰し、直進時の横逸れ・首振りを抑制。
  - _reward_action_smoothness2 新設・"action_smoothness2": -0.01
      行動の2階差分(躍度)を罰し、カクッとした動きを低減。
  - torque_limits を強化: soft比 0.85→0.65、scale -2.0→-5.0（100%張り付きを許さない）。
  - lin_vel_x_range 前進上限 0.4→0.3（推進トルクのピークを下げ低負荷化）。後退 -0.2 は維持。
  - dof_pos_error(-1.0) 等 v9 の対策は維持。
  ※ 新報酬の scale は初期値。学習後に飽和が残れば torque_limits/leg_load_balance を強め、
    歩容が消える(立ち止まる)なら弱める。次段(v11)でミラー対称化学習/クロール歩容も検討可。

既定 exp_name は khr-quadruped10。v1〜v9 の成果物には一切触れない。

--- 以下、v9 の継承説明 ---
四足歩行 学習スクリプト v9 — トルク飽和を止め、後退を追加する版（実機フィードバック反映）。
khr_train_quad8.py (v8) のコピー。環境は khr_quad_env6.py。

実機で教授から受けた3指摘への対策:
 ① ぎこちない / ② トルクが最大 … 実測診断で、前進・横・旋回すべてで後脚の
    l/r_hip_pitch が **常時トルク100%飽和**し、指令位置から **50〜66度ズレ続ける**
    （bang-bang制御）ことが判明。静止保持なら同姿勢を43%で支えられる＝ハード弱ではなく
    「方策がアクチュエータ飽和を悪用した」報酬設計の問題。実機では最大トルク＋カクつきとして出る。
 ③ 後退できない … lin_vel_x_range=[0,0.4] で負の速度を一度も学習していなかった。

v8 → v9 の変更点（環境は khr_quad_env6、姿勢は v8 のまま）:
  - [A] _reward_torque_limits を新設・"torque_limits": -2.0
        定格(1.373Nm)の85%超のトルクを罰し、飽和(限界張り付き)を抑制。
  - [B] _reward_dof_pos_error を新設・"dof_pos_error": -1.0（主対策）
        PD目標角と実角の誤差を罰し、到達不能な指令＝飽和の直接原因を叩く。
  - [D] acceleration -0.00002 → -0.00004（カクつきの補助的低減）
  - [E] lin_vel_x_range [0,0.4] → [-0.2, 0.4]（後退を開放。前進0.4/後退0.2）

既定 exp_name は khr-quadruped9。v1〜v8 の成果物には一切触れない。

--- 以下、v8 の継承説明 ---
四足歩行 学習スクリプト v8 — 膝をハードストップから解放し、脚の横開きを抑える版。
khr_train_quad7.py (v7) のコピー。環境は khr_quad_env5.py（横開き抑制を追加）。

v7 の診断で判明した2つの問題:
 (1) 【膝のロック】knee_pitch の初期値 0.10rad は機械的下限 0.0 のわずか 5.7度上。
     膝は片方向にしか曲がらないため主動力の膝がハードストップに押し付けられ、
     可動幅わずか6.4度なのにトルク張り付き100%。これが「関節が動かない・
     ぎこちない」の正体だった。
 (2) 【脚の横開き】hip_yaw ±20度, ankle_roll ±30度で開いたまま保持され、
     その4関節が定格トルク95%以上に時間の98〜99%張り付き（実機で発熱・脱調リスク）。

v7 → v8 の変更点:
  - 初期姿勢の再導出（膝に可動余地を与える。足裏水平条件 hip+knee+ankle=-1.5708 は維持）
      knee_pitch  0.10 → 0.40  (下限までの余裕 5.7度 → 22.9度)
      hip_pitch  -1.671 → -1.770
      ankle_pitch  0.0 → -0.201
      shoulder_pitch -1.5708 → -1.771 / elbow_pitch 0.0 → 0.20
        （後脚が短くなる分、前脚も曲げてリーチを一致させる。前後差 3.0mm → 2.0mm）
      base_init_pos z 0.197 → 0.1946、base_height_target も同値
  - 環境を khr_quad_env5 に変更（_reward_hip_pos に hip_yaw/ankle_roll を追加）

検証: 新姿勢は静的に安定（400step で base_z 0.193 維持、x ずれ1.7mm）、
      静止保持時のトルクは定格95%超が 0/22（膝はわずか7〜8%）。

既定 exp_name は khr-quadruped8。v1〜v7 の成果物には一切触れない。
"""

# --- 以下、v7 からの継承説明 ---
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

from khr_quad_env15 import KHRQuadEnv  # v18: 上記 + 足裏全面接地（着地直前から水平）


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
            "l_shoulder_pitch": -1.771,  # v8: 前脚を後脚のリーチに合わせる
            "l_shoulder_roll": 0.0,
            "l_elbow_yaw": 0.0,
            "l_elbow_pitch": 0.20,   # v8

            "r_shoulder_pitch": -1.771,  # v8
            "r_shoulder_roll": 0.0,
            "r_elbow_yaw": 0.0,
            "r_elbow_pitch": 0.20,   # v8

            # --- 後脚（元の脚） ---
            "l_hip_yaw": 0.0,
            "l_hip_roll": 0.0,
            "l_hip_pitch": -1.770,   # v8
            "l_knee_pitch": 0.40,    # v8: 0.1は下限0.0の5.7度上でロックしていた
            "l_ankle_pitch": -0.201, # v8
            "l_ankle_roll": 0.0,

            "r_hip_yaw": 0.0,
            "r_hip_roll": 0.0,
            "r_hip_pitch": -1.770,   # v8
            "r_knee_pitch": 0.40,    # v8
            "r_ankle_pitch": -0.201, # v8
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
        "base_init_pos": [0.0, 0.0, 0.1946],  # v8: 新姿勢の接地高さ
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
        "tracking_sigma": 0.08,  # v19: 0.15→0.08 速度不足を実際に痛くする（v18は43%不足でも報酬89.5%を獲得できていた）
        "base_height_target": 0.1946,  # 【変更】初期高さに合わせて目標高さを0.197mに修正
        "feet_height_target": 0.06,  # v12以前の絶対高さ目標（v13のenv10では未使用。互換のため残置）
        "knee_swing_flexion_target": 0.25,  # v17: 遊脚中に「接地時の自分の膝角度」から追加で曲げる目標[rad]
        "knee_stance_ema_alpha": 0.05,      # v17: 接地時の膝角度(基準)のEMA係数
        "feet_orientation_stance_only": True,   # v15: 足裏水平罰は接地時のみ（遊脚中の膝・足首を解放）
        "feet_orientation_prelanding_phase": 0.85,  # v18: 着地直前(遊脚終盤)からも足裏水平を要求＝足裏全面で接地
        "foot_clearance_target_front": 0.012,  # v14: 前脚は v12 水準で十分（v13で0.032まで上がったが不要）
        "foot_clearance_target_rear": 0.02,    # v14: 問題の後脚だけ目標を上げる（v13実測は0.005m）
        "air_time_target": 0.2,     # v13: 滞空時間の目標[s]（swing期=0.45*0.5s=0.225s に対応）
        "torque_soft_ratio": 0.65,  # v10: 0.85→0.65 定格65%超のトルクを罰し、100%張り付きを許さない
        "yaw_drift_weight": 1.0,    # v12: v11の5.0は瞬時yawを罰しすぎ並進が崩壊→v10相当の1.0に戻す
        "reward_scales": {
            "tracking_lin_vel": 5.0,  # v19: 4.0→5.0 sigma縮小と併せて「速さの限界価値」を約2.1倍に
            "tracking_ang_vel": 1.0,

            "orientation": -5.0, # 環境側で loco 座標系(公称姿勢基準)の重力 xy を使うため前傾姿勢でも整合済み
            "lin_vel_z": -0.1,
            "ang_vel_xy": -0.2,
            "base_height": -3.0,      # v14: -10.0→-3.0 胴体の上下動を許し後脚が畳める余地を作る（主対策）
            "gait_contact" : 0.18,
            "gait_swing": -0.05,
            "contact_no_vel": -1.0,   # v13: -0.2→-1.0 接地中の引きずり(前脚0.13-0.15m/s)を強く罰す
            "feet_clearance": 1.0,    # v13: 0.2→1.0 相対クリアランス化と併せて足上げの価値を明確に
            "knee_swing_flexion": 1.8,  # v18: 3.0→1.8 ROM56度は過剰。トルクピーク91%と追従低下を戻す
            "feet_air_time": 1.0,     # v13: 接地の瞬間に滞空時間を加点し「上げて運んで置く」歩容へ
            "hip_pos": -1.0,
            # v7: 足裏を水平に保たせる（v6は足裏が平均24度傾き縁で歩いていた）
            "feet_orientation": -3.0,  # v18: -1.0→-3.0 つま先/踵だけの接地を止め足裏全面で接地させる
            "alive" : 0.5,

            # v9: 教授指摘①②の根本原因＝後脚 hip_pitch がトルク飽和(常時100%)し、指令から
            #     50〜66度ズレたまま bang-bang 制御になっていた。到達不能な指令と飽和を直接罰する。
            "dof_pos_error": -1.0,   # v9-B: PD目標角と実角の誤差を罰し「実現可能な指令」へ誘導
            "torque_limits": -5.0,   # v10: -2.0→-5.0 定格65%超のトルクを強く罰し100%を禁止（要件: 100%絶対NG）

            # v10: 前進時の右hip_pitch常時100%飽和＋横逸れ＝左右非対称歩容が根本原因。報酬で対称化する。
            "leg_load_balance": -1.0,   # v10: 左右後脚の平均負荷(EMA)差を罰し片脚集中を是正（横逸れの根本対策）
            "drift": -10.0,             # v10: 指令からの横速度/旋回のズレを二乗で罰し直進時の横逸れを補助的に抑制
            "heading_drift": -40.0,     # v12: yaw誤差のEMA(持続的な首振り偏り)を罰し、並進を潰さず直進化
            "action_smoothness2": -0.01, # v10: 行動の2階差分(躍度)を罰しカクつきを低減

            "action_rate": -0.02,  # v3: -0.05→-0.02 能動的な足運びを許容（滑らかさ罰を緩める）
            "similar_to_default": -0.02,  # v3: -0.1→-0.02 歩行は姿勢を崩すので、この罰を弱める
            "dof_vel": -0.001,
            "acceleration" : -0.00004,  # v9-D: -0.00002→-0.00004 カクつき低減のため加速度罰を微増
            "joint_torques":-0.0005,
        },
    }
    command_cfg = {
        # v4(1a): 前進のみ → 全方向歩行へ拡張。x は据え置き、横移動(y)と旋回(yaw)を開放。
        # 追従報酬は既に commands の x/y(tracking_lin_vel) と yaw(tracking_ang_vel) を扱うため
        # 環境コードは変更不要（コマンド範囲を開くだけ）。
        "num_commands": 3,
        "lin_vel_x_range": [-0.2, 0.3],    # v10: 前進上限 0.4→0.3（推進トルクのピークを下げ低負荷化）
        "lin_vel_y_range": [-0.15, 0.15],  # v4: 横移動を開放（横は前進より難しいので控えめに）
        "ang_vel_range": [-0.5, 0.5],      # v4: その場旋回(yaw)を開放 [rad/s]
    }

    return env_cfg, obs_cfg, reward_cfg, command_cfg

env=[]

def main():
    global env
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exp_name", type=str, default="khr-quadruped19") # v19: 前進追従の回復
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