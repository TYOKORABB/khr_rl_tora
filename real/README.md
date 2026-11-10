# real/ — 実機側（Meridian 経由の Sim2Real）

`docs/GetUpSim2RealPlan.md` §4.1・§5.2 の実機側のコード。実行はリポジトリのルートから `python -m real.<名前>`。

| パス | 内容 |
|---|---|
| `firmware_patches/` | ESP32 ファーム（梶田研の Meridian_LITE）への改造パッチ。`khr-getup.4`: IMU の重力ベクトル送信（一括読み取り）・通信監視による脱力・受信の古いパケットの読み捨て。**`khr-getup.5`（11/7、11/9 から実機に入っている）**: .4 に、肩・肘のサーボの電流と温度、全サーボの設定の読み出しを足した（読むだけで書き換えない）。バックアップつき書き込み `flash_with_backup.py`、作り直し `build_fw.sh`。詳細は同フォルダの README |
| `fw_check.py` | 改造ファームの実機確認ツール（状態表示・IMU の 6 姿勢記録と取り付け回転の推定・通信監視の試験・IMU の読み取り方の比較 `imu-ab`・往復遅れ `latency`）。サーボに電源を入れる指令は送らない |
| `pose_session.py` | IMU の 6 姿勢試験を、全サーボに電源を入れて今の姿勢を保ったまま行う（`serve` を裏で動かし `record <姿勢>`）。指令とのずれが 5° を 0.3 s 超えたら全サーボ脱力 |
| `walk_session.py` | 四脚歩行の方策（既定 v31-s2）を画面なしで実機に動かす（コンソールの代わり）。観測は学習時と同じ作り方で、`replay-check` で学習環境と一致することを確かめられる。転倒（45°）・関節のずれ（30°）で全サーボ脱力 |
| `walk_analyze.py` | `walk_session` の記録を指令の区間ごとに分析し、同じ指令の列を学習環境でも動かして比べる（`--sim`）。結果は記録の日付の `experiments/real/<日付>_walk/` |
| `walk_joints.py` | 歩行の記録で 22 関節の動きを学習環境と比べ、関節を 1 つずつ反転したシミュとの比較で符号表（`khr_common/joint_map.py`）を確かめる |
| `obs_check.py` | P0-3 の単体テスト（実機なし）: 学習環境の状態を、実機から届く形（サーボと IMU の分解能・Meridim の int16・取り付け回転・0〜10 ms の古さ）にしてから `walk_session` の観測の作り方に通し、学習環境の観測と比べる |
| `imu_tests.py` | IMU の P0-1 の残りの確かめ（斜めの静止・360° 回し・落下からの戻り）。`--npz` で記録だけの分析もできる |
| `getup_session.py` | 起き上がりの方策を実機で動かす。`getup`（通電した起き上がり。脱力 1 秒 → 通電で可動域の内側へ寄せる 1.5 秒 → 方策 8 秒 → 保持 3 秒 → 脱力。`--gap` でずれの上限、`--freeze N` で四脚の条件が N 周期続いたら目標角を固定（11/10））、`getup-loop`（機体が評価用バンクの関節角へ自分で動いてから起き上がる、を繰り返す。11/9）、`getup-selftest`・`getup-loop-selftest`（偽の ESP32）、`analyze-trial`、`sign-hand`（脱力のまま手で回した関節の読みの正負）。止める条件は、受信の 0.4 秒の途切れ（11/10 に 0.2 秒から変更）、stop ファイル、目標とのずれ。R0（全サーボ脱力のまま観測・方策の出力・目標角を記録）は `shadow`、`obs-check` は実機なしの P0-3 の起き上がり版。符号の表 `calib/joint_sign.json`（右の肘ヨーは −1、起き上がりの道具だけが使う） |
| `servo_tel.py` | khr-getup.5 のサーボの読み出しを受ける・読む: 肩・肘の電流と温度（`live`）、全サーボの設定（`dump`。プロテクション、電流制限、ストレッチなど）。電流の換算（1 = 0.1 A）は仮 |
| `summarize_r3.py` | 実機の起き上がり 2 回目（11/9）の全試行を同じ基準で集計する → `experiments/real/20261109_getup_r2/summary.md`（止まった肩の電流、受信の隙間も） |
| `protection_check.py` | プロテクション（ロックから設定の時間で出力 50 %）が働いたかを、押し続けた区間の電流で確かめる（11/9 は働いた跡なし） |
| `stand_cost.py` | 立ったあとに方策が目標角を動かし続けることの実害（崩れたか、外れる条件、腕の電流）を実機の記録で見る（11/10） |
| `video_analysis.py` | スマホの動画（`media/mp4/`）と実機の記録の時刻を合わせ、どの動画がどの試行か、手の写り込み、立っている間の揺れ、脱力のあとの様子を求める（11/10） |
| `servo_jog.py` | サーボ 1 個だけに電源を入れ、今の角度から小さく（既定 ±5°）1 往復させる動作確認。追従誤差と遅れを記録。ずれが 2° を 0.3 s 超えたら脱力 |
| `step_response.py` | E1-lite（計画書 §5.3）: 胴体を台に固定し、全関節 0° を保ったまま代表の関節を段差状に動かして、遅れ・立ち上がり・行き過ぎ・2 次の遅れの当てはめを記録。`selftest` は偽の ESP32 で動作確認。学習環境のモデルでの同じ計算は `sysid/step_sim.py` |
| `calib/` | 実機で測った IMU の取り付け回転など（`fw_check pose` / `solve` が書く） |

PC 側の共通コードは `khr_common/`（`gravity.py`: IMU 信号 → base 座標の重力ベクトル）。
実機の記録と学習環境の突き合わせ（ずれの原因探し・区間再生）は `sysid/`。機体の現状は `ROBOT_STATUS.md`。

## 出所とライセンス

- `firmware_patches/khr-getup.4.patch`・`khr-getup.5.patch` は `s-kajita/Meridian_LITE`（公開 fork）のコミット `85a62d1` に対する差分で、
  差分の文脈として元のコードを数行ずつ含む。上流は `Ninagawa123/Meridian_LITE`
  — MIT License, Copyright (c) 2021 Ninagawa123 (GitHub) and Project Meridian Team。
- 四脚デプロイヤ（`Meridian_consoleS_quad.py`・`khr_quad_env_no_gs.py`）は研究室の手元にだけある版なので、
  梶田先生の了承を得るまでこのリポジトリには入れない（計画書 §4.1）。
- Wi-Fi の設定（`keys.h`）・`board_ip.txt`・生ログ（`data/raw/`）・フラッシュのバックアップ（`firmware_patches/_work/`、Wi-Fi の設定を含む）はコミットしない（`.gitignore`）。

実機に載せた方策（チェックポイントと設定）は `policies/` に凍結してある（`policies/README.md`）。`walk_session.py` は `logs/` に無ければそこから読む。
