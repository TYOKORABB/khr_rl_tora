# real/ — 実機側（Meridian 経由の Sim2Real）

`docs/GetUpSim2RealPlan.md` §4.1・§5.2 の実機側のコード。実行はリポジトリのルートから `python -m real.<名前>`。

| パス | 内容 |
|---|---|
| `firmware_patches/` | ESP32 ファーム（梶田研の Meridian_LITE）への改造パッチ `khr-getup.4`: IMU の重力ベクトル送信（一括読み取り）・通信監視による脱力・受信の古いパケットの読み捨て。バックアップつき書き込み `flash_with_backup.py`。詳細は同フォルダの README |
| `fw_check.py` | 改造ファームの実機確認ツール（状態表示・IMU の 6 姿勢記録と取り付け回転の推定・通信監視の試験・IMU の読み取り方の比較 `imu-ab`・往復遅れ `latency`）。サーボに電源を入れる指令は送らない |
| `pose_session.py` | IMU の 6 姿勢試験を、全サーボに電源を入れて今の姿勢を保ったまま行う（`serve` を裏で動かし `record <姿勢>`）。指令とのずれが 5° を 0.3 s 超えたら全サーボ脱力 |
| `walk_session.py` | 四脚歩行の方策（既定 v31-s2）を画面なしで実機に動かす（コンソールの代わり）。観測は学習時と同じ作り方で、`replay-check` で学習環境と一致することを確かめられる。転倒（45°）・関節のずれ（30°）で全サーボ脱力 |
| `walk_analyze.py` | `walk_session` の記録を指令の区間ごとに分析し、同じ指令の列を学習環境でも動かして比べる（`--sim`）。結果は記録の日付の `experiments/real/<日付>_walk/` |
| `walk_joints.py` | 歩行の記録で 22 関節の動きを学習環境と比べ、関節を 1 つずつ反転したシミュとの比較で符号表（`khr_common/joint_map.py`）を確かめる |
| `obs_check.py` | P0-3 の単体テスト（実機なし）: 学習環境の状態を、実機から届く形（サーボと IMU の分解能・Meridim の int16・取り付け回転・0〜10 ms の古さ）にしてから `walk_session` の観測の作り方に通し、学習環境の観測と比べる |
| `imu_tests.py` | IMU の P0-1 の残りの確かめ（斜めの静止・360° 回し・落下からの戻り）。`--npz` で記録だけの分析もできる |
| `servo_jog.py` | サーボ 1 個だけに電源を入れ、今の角度から小さく（既定 ±5°）1 往復させる動作確認。追従誤差と遅れを記録。ずれが 2° を 0.3 s 超えたら脱力 |
| `calib/` | 実機で測った IMU の取り付け回転など（`fw_check pose` / `solve` が書く） |

PC 側の共通コードは `khr_common/`（`gravity.py`: IMU 信号 → base 座標の重力ベクトル）。
実機の記録と学習環境の突き合わせ（ずれの原因探し・区間再生）は `sysid/`。機体の現状は `ROBOT_STATUS.md`。

## 出所とライセンス

- `firmware_patches/khr-getup.4.patch` は `s-kajita/Meridian_LITE`（公開 fork）のコミット `85a62d1` に対する差分で、
  差分の文脈として元のコードを数行ずつ含む。上流は `Ninagawa123/Meridian_LITE`
  — MIT License, Copyright (c) 2021 Ninagawa123 (GitHub) and Project Meridian Team。
- 四脚デプロイヤ（`Meridian_consoleS_quad.py`・`khr_quad_env_no_gs.py`）は研究室の手元にだけある版なので、
  梶田先生の了承を得るまでこのリポジトリには入れない（計画書 §4.1）。
- Wi-Fi の設定（`keys.h`）・`board_ip.txt`・生ログ（`data/raw/`）・フラッシュのバックアップ（`firmware_patches/_work/`、Wi-Fi の設定を含む）はコミットしない（`.gitignore`）。
