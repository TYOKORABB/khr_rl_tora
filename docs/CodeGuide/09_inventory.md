# 9. 全ファイルの一覧

[目次へ戻る](README.md)

リポジトリの中のプログラム（`.py`・`.sh`・`.patch`）を、ディレクトリごとに並べました。
`quad/` は版ごとの複製が多いので、まとめて書いています。それ以外は、各ファイルの先頭の説明文の 1 行目を自動で取り出したものです（先頭の説明文が中身を表していないものだけ、`_spec/inventory_override.txt` で書き換えています）。
`quad/archive_v1_v15/`（v1〜v15 の環境と学習、39 本）は除いています。

## 9.1 quad/（四脚歩行、93 本）

| ファイル | 本数 | 何をするか |
|---|---|---|
| `khr_quad_env13.py`〜`khr_quad_env21.py` | 9 | 四脚歩行の学習環境の各版（版との対応は 1 章 1.7）。v30・v31 は env21（2 章） |
| `khr_quad_env17_abl_clearance.py` | 1 | 報酬の総点検のため、足上げの項を変えた env17 |
| `khr_train_quad16.py`〜`khr_train_quad31.py`、`khr_train_quad27_p075.py`・`27_p080.py` | 17 | 各版の学習スクリプト（v31 は 3 章）。v27 は着地の直前の位相 0.75・0.80 の 2 案を比べ、0.80 を採った |
| `khr_train_quad23_abl_*.py`（4）、`khr_train_quad27_abl_*.py`（13）、`khr_train_quad28_combo9.py` | 18 | 報酬の総点検: 1 項・1 群ずつ外して学習し直す。9 項をまとめて外した combo9 が v28 になった |
| `khr_train_quad31_abl.py` | 1 | v31 を基準に報酬を外して学習し直す（報酬の総点検） |
| `khr_train_quad31_tqsens.py` | 1 | トルクの罰の閾値だけを変えて学習する（感度分析: 50・60・70 %） |
| `khr_quad_eval.py` | 1 | 方策を画面で再生する（CPU） |
| `khr_quad_eval_metrics.py` | 1 | 測る条件を固定した定量の測定（7 章） |
| `khr_quad_compare.py` | 1 | 測った値をノイズ床に対して 2σ で判定する（7 章） |
| `khr_quad_eval_symmetry.py` | 1 | 後脚の左右の対称と、接地の質を測る |
| `khr_quad_plot_torque.py` | 1 | 22 関節のトルクの時間の変化を図にする |
| `khr_quad_progress.py` | 1 | 学習の経過（100 イテレーションごとの方策）を同じ条件で測り、図と動画にする |
| `khr_quad_report.py` | 1 | 学習のあとに研究の記録（設定・指標・経過）を自動で作る |
| `khr_quad_record13.py`〜`khr_quad_record21.py` | 8 | 方策の動きを MP4 に録画する（画面なし）。版ごとの環境用 |
| `khr_quad_record_seeds.py` | 1 | 複数のシードの方策を同じ場面に並べて録画する |
| `build_noise_floor.py` | 1 | シード間のばらつき（ノイズ床）を作る |
| `summarize_abl31.py`・`summarize_abl31_ext.py`・`summarize_tqsens.py`・`summarize_v28v30.py` | 4 | 報酬の総点検・感度分析・シードの追加の結果を、学習の前に決めた基準でまとめる |
| `update_reward_reference.py` | 1 | 報酬の総点検の結果から `docs/RewardReference.md` の自動の部分を更新する |
| `quad_pose_test.py` | 1 | 四脚の初期姿勢の試作と、静的・動的な安定の確かめ（四脚化の最初の段階） |
| `quad_compat.py` | 1 | 古い版の環境を、今の測定の道具で公平に測れるようにする互換の層 |
| `run_record.py` | 1 | `quad/` から `khr_common.run_record` を使う入口 |
| `fix_joint_limits.py`・`train_with_urdf_fix.py`・`train_fixurdf_abl.py`・`eval_with_urdf_fix.py`・`record_with_urdf_fix.py`・`sym_with_urdf_fix.py`・`prove_hip_limit_asymmetry.py`・`check_joint_saturation.py` | 8 | 機体のモデル（URDF）の可動域の点検と、それに合わせた全版の学習し直し・測り直しの道具（卒論では扱わない） |
| `jobs/run_abl31.sh`・`run_abl31_ext.sh`・`run_ablation_queue.sh` | 3 | 報酬の総点検の学習を、GPU の空きに合わせて自動で回す |
| `jobs/run_tqsens.sh` | 1 | トルクの罰の閾値の感度分析を自動で回す |
| `jobs/run_v28v30.sh` | 1 | v28 と v30 にシード 4〜6 を足して回す |
| `jobs/run_kp_robust.sh` | 1 | 比例ゲインのずれへの強さを測る（3 並列） |
| `jobs/run_retrain_fixurdf.sh`・`measure_strafe_fixurdf.sh` | 2 | 全版の学習し直しと、横移動の測り直し（卒論では扱わない） |
| `jobs/verify_v28.sh` | 1 | v28 の方向ごとの追従の確かめと動画 |
| `jobs/v31_progress_videos.sh`・`v31_seeds_compare_video.sh` | 2 | v31 の学習の経過の動画と、3 シードを並べた動画 |
| `jobs/repeat_until_done.sh` | 1 | 待ち行列のスクリプトを、全部終わるまで一定の間隔で呼び直す |
| `jobs/whisper_overlap_test.sh` | 1 | 音声の解析（whisper）と学習を重ねてよいかの試験 |

## 9.2 そのほかのディレクトリ

### khr_common/（7 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `khr_common/action_post.py` | 139 | 行動 → 関節の目標角の共通後処理（GetUpSim2RealPlan.md §4.3.2）。学習環境とデプロイヤが同じ関数を使う。 |
| `khr_common/gravity.py` | 208 | IMU 信号 → base 座標の重力ベクトル（全姿勢で使える）。Genesis に依存しない（numpy のみ）。 |
| `khr_common/height_est.py` | 137 | h_est: 関節角と重力の向き（base 座標）から、順運動学で「いちばん低い点から胴体（base_link の原点）までの高さ」を求める。 |
| `khr_common/joint_map.py` | 156 | 22 関節の順序・公称姿勢・Meridim 番号・符号表の唯一の定義元（Genesis 非依存）。 |
| `khr_common/mirror.py` | 86 | 左右反転（2026-11-04、getup-v9）。観測と行動を左右の鏡像に写す（Genesis 非依存、学習環境と実機のデプロイヤで共用できる形）。 |
| `khr_common/paths.py` | 67 | リポジトリ内のパス解決（Genesis 非依存）。 |
| `khr_common/run_record.py` | 57 | 学習を始めたときのコードの状態を、学習の出力先に残す（Genesis 非依存、標準ライブラリだけ）。 |

### getup/（96 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `getup/envs/getup_env1.py` | 501 | getup-v1: 転倒状態（うつ伏せ系）→ 四脚の公称姿勢（v31 の初期姿勢）へ起き上がる環境（GetUpSim2RealPlan.md §4.3〜4.5・§4.8）。 |
| `getup/envs/getup_env2.py` | 509 | getup-v2: getup-v1（getup_env1.py）に、目標角を測った関節角の近くに収める制限を足した環境（2026-10-14）。 |
| `getup/envs/getup_env3.py` | 740 | getup-v3: getup-v2（getup_env2.py）に、学習のトルクの上限と行動の 2 階差分の罰を足した環境（2026-10-15）。 |
| `getup/envs/getup_env4.py` | 80 | getup-v10 の環境（2026-11-04）: getup_env3 に、候補 B・C の報酬と初期状態の選び方を足す（docs/GetUpImprovementOptions.md）。使わない項は getup_env3 と同じ。 |
| `getup/eval_getup.py` | 357 | 起き上がり方策の検証（GetUpSim2RealPlan.md §6.1・§4.8 の判定）。**動画は毎回撮る**（2026-10-14 のユーザーの指示）。 |
| `getup/gen_init_states.py` | 217 | 起き上がりの初期状態バンク（GetUpSim2RealPlan.md §4.3.1）を作る。 |
| `getup/jobs/gpu_gate.sh` | 50 | GPU を使う学習・検証の前に「空いているか」を見る関数（source して使う、2026-10-16 に train_eval.sh から切り出し）。 |
| `getup/jobs/pause_whisper.sh` | 20 | whisper の cron を止める（11/7 の本人の決定「GPUを使う必要がある場合は、Whisperを止めていいので、研究第一で行こう。」）。何度動かしても同じ結果。 |
| `getup/jobs/run_queue.sh` | 22 | 起き上がりの学習 → 検証（動画つき）を、キューのファイルの順に 1 本ずつ回す（whisper の解析は train_eval.sh --wait が避ける）。 |
| `getup/jobs/run_v10.sh` | 47 | getup-v10 を最後まで自動で回す（2026-11-05）: 候補ごとに 学習と検証（queue_v10、スイッチなし）→ スイッチありの検証と動画 → スイッチなしの転んだ状態・胸が上 → 失敗の型 → まとめ。 |
| `getup/jobs/run_v10_c3.sh` | 64 | getup-v10 の C3 を自動で回す（2026-11-06）: run_v10*.sh がすべて終わるのを待って、A1 の構成のシード 4・5・6 を 学習と検証 → スイッチ（固定の向き）ありの検証と動画 |
| `getup/jobs/run_v10_still_seeds.sh` | 45 | getup-v10 の B1 のシード追加を自動で回す（2026-11-05）: run_v10.sh と run_v10_sym.sh が終わるのを待って、シード 4・5・6 を、学習と検証 → スイッチありの検証と動画 → スイッチ… |
| `getup/jobs/run_v10_sym.sh` | 45 | getup-v10 の追加を自動で回す（2026-11-05）: run_v10.sh（C2 まで）が終わるのを待って、sym ＋ C1、sym ＋ C2、sym ＋ C1 ＋ C2 を順に、学習と検証 → 追加の検証と動画 → 失敗の… |
| `getup/jobs/run_v11.sh` | 33 | getup-v11（experiments/getup/v11_plan.md、11/6）: getup9-sym-s1 から 3 シードを学習 → 検証（動画）→ 判定の計算（CPU）。 |
| `getup/jobs/run_v11b.sh` | 31 | getup-v11b（experiments/getup/v11_plan.md §5、11/6）: v11 のシード 1 の学習が崩れた（std の発散）ので、std 固定・エントロピー 0・弱さを |
| `getup/jobs/run_v11c.sh` | 35 | getup-v11c（experiments/getup/v11_plan.md §7、11/7、学習の前に固定）: 実機に近い 3 つの弱さの模型（kp 10〜12 ＋ 上限 30 %、電源の合計を抑える模型）の |
| `getup/jobs/run_v12.sh` | 32 | getup-v12（experiments/getup/v12_plan.md §3、11/9、学習の前に固定）: 実機に合わせた硬さ（kp 5〜10）、ずれの上限 0.08 rad、胸が上の状態、立っている間の目標角の動きの罰で、 |
| `getup/jobs/run_v12k.sh` | 31 | getup-v12k（experiments/getup/v12_plan.md §4、11/10、学習の前に固定）: v12 から硬さの範囲（--kp 5 10）だけを外した比較（kp 25 に固定）。 |
| `getup/jobs/run_v13.sh` | 57 | getup-v13（2026-11-13、experiments/getup/v13_plan.md）: v12 から 1 つずつ変えた案を、待ち行列のファイルの順に 1 つずつ回す。 |
| `getup/jobs/run_v13b.sh` | 60 | getup-v13 の 2 回目（2026-11-16、experiments/getup/v13_plan.md §7）。run_v13.sh と同じ流れで、案ごとにシードを選べる。 |
| `getup/jobs/run_v13c.sh` | 61 | getup-v13 の 3 回目（2026-11-17、experiments/getup/v13_plan.md §8）。run_v13b.sh と同じで、引数の {s} をシードの番号に置き換える。 |
| `getup/jobs/run_v13d.sh` | 61 | getup-v13 の 4 回目（2026-11-18、experiments/getup/v13_plan.md §9）。run_v13c.sh と同じで、待ち行列とまとめだけ替えた。 |
| `getup/jobs/run_v7.sh` | 31 | getup-v7 を最後まで自動で回す（2026-11-02）: 学習 → 検証（queue_v7）→ 脱力の横倒しの動画 → 失敗の型 → まとめ。 |
| `getup/jobs/run_v8.sh` | 34 | getup-v8 を最後まで自動で回す（2026-11-04）: 学習 → 検証（queue_v8）→ 脱力の横倒しと転んだ状態と胸が上の状態の検証（動画つき）→ 失敗の型 → まとめ。 |
| `getup/jobs/run_v9.sh` | 60 | getup-v9 を最後まで自動で回す（2026-11-04）: A1（v7 の B ＋ 左右反転のスイッチ）の検証 → A2 の学習と検証（queue_v9）→ 追加の検証 → 失敗の型 → まとめ。 |
| `getup/jobs/train_eval.sh` | 61 | 起き上がりの学習 → 検証（成功率・トルク・動画）を続けて行う。検証では毎回動画を撮る（2026-10-14 のユーザーの指示）。 |
| `getup/jobs/v13_cpu_refs.sh` | 28 | getup-v13 の参考の量（2026-11-17、experiments/getup/v13_plan.md §8.2）。CPU だけ（GPU の学習とは重ならない）。判定には使わない。 |
| `getup/jobs/v13_cpu_refs2.sh` | 21 | getup-v13 の参考の量の続き（2026-11-17、experiments/getup/v13_plan.md §8.2）。CPU だけ。判定には使わない。 |
| `getup/jobs/v13_kp_eval.sh` | 31 | getup-v13 の追加の判定（2026-11-13、experiments/getup/v13_plan.md §3）: 各案の学習と eval_v13.py が終わったら、 |
| `getup/levels.py` | 26 | 起き上がりのカリキュラムの段階ごとに、初期状態バンクのどの状態を使うかを決める（環境と評価の道具で共用、2026-10-30）。 |
| `getup/ppo_bound.py` | 201 | rsl-rl 5.4.0 の PPO に「行動の平均が ±bound を超えた分の 2 乗」の罰（bound loss）を足したもの（getup-v2 の候補 1、2026-10-14）。 |
| `getup/precheck/_scene.py` | 103 | 事前検証で共通に使う、CPU・1 env のシーン構築（GetUpSim2RealPlan.md §4.2）。 |
| `getup/precheck/p1_collision_geom.py` | 243 | 事前検証 1: 衝突形状の監査（GetUpSim2RealPlan.md §4.2-1 / F14）。 |
| `getup/precheck/p2_self_collision.py` | 298 | 事前検証 2: 自己衝突と接触バッファ（GetUpSim2RealPlan.md §4.2-2 / §4.3.5 / F14）。 |
| `getup/precheck/p3_static_torque.py` | 323 | 事前検証 3: キー姿勢と経路の静的トルク（GetUpSim2RealPlan.md §4.2-3 / F10 / C3-lite）。 |
| `getup/precheck/p4_handoff_domain.py` | 285 | 事前検証 4: 四脚歩行 v31 の引き継ぎ可能域（GetUpSim2RealPlan.md §4.2-4）。 |
| `getup/sym_aug.py` | 23 | rsl-rl の対称性のデータ拡張の関数（2026-11-04、getup-v9 の sym）。ミニバッチに左右反転した観測と行動を足す（Mittal ら、ICRA 2024）。 |
| `getup/tools/after_stand.py` | 125 | 起き上がったあと、方策が動いている間に成功の条件がどう外れるかを、実機の記録とシミュで比べる（2026-11-09、順 3。判定には使わない）。CPU。 |
| `getup/tools/check_height_est.py` | 57 | h_est（khr_common/height_est.py）を、初期状態バンクの「床の上で落ち着いた状態」で確かめる。 |
| `getup/tools/check_mirror.py` | 70 | 左右反転の並びが正しいかを物理で確かめる（2026-11-04、getup-v9。CPU、1 分以内）。 |
| `getup/tools/check_success.py` | 99 | 学習済みの起き上がり方策で、成功判定（§3.2）のどの条件が満たされないかを調べる（GPU）。 |
| `getup/tools/current_estimate.py` | 175 | 起き上がりの方策が電源から引く電流を、シミュの関節トルクから見積もる（2026-11-06）。 |
| `getup/tools/current_power_form.py` | 154 | 電源の電流を「電力の形」でも見積もり、起き上がりと四脚歩行（同じ電源で実機で歩けた）を同じ式で比べる（2026-11-07）。 |
| `getup/tools/diag_levers.py` | 140 | 学習し直さずに、既存の方策で「何が成功を妨げているか」と「どのレバーが効きそうか」を調べる（2026-11-04、getup-v8 の不合格の後。判定には使わない）。 |
| `getup/tools/diag_mirror.py` | 211 | 方策を左右反転して動かす診断（2026-11-04、diag_stuck の続き。学習はしない。判定には使わない）。 |
| `getup/tools/diag_stuck.py` | 165 | 胸を向けられない失敗が止まっている姿勢を調べる（2026-11-04、diag_levers の続き。判定には使わない）。 |
| `getup/tools/diag_switch_path.py` | 91 | 左右反転のスイッチを入れると落ちる方策で、体が何をしているかを見る（2026-11-05）。getup10-fliplim-s2 はスイッチなしで F 97.8 %、ありで 0.9 %。 |
| `getup/tools/diag_sym.py` | 37 | sym の 3 シードの止まり方（2026-11-05、判定には使わない）: u0 < 0.5 の評価用の状態から 8 秒後に、どちらの体側で止まるかを数える。 |
| `getup/tools/dr_factor_eval.py` | 223 | 個体差の要素を 1 つずつ入れて、起き上がりの成功率がどれで下がるかを切り分ける（診断用、2026-10-14）。 |
| `getup/tools/eval_freeze.py` | 129 | 実機で「四脚の条件がそろったら目標角を固定する」機能の見込みをシミュで確かめる（2026-11-10）。CPU。 |
| `getup/tools/eval_v12.py` | 137 | getup-v12 の判定に使う量を、実機に合わせた条件（kp 7、ずれの上限 0.08 rad）で計算する（2026-11-09、experiments/getup/v12_plan.md §3）。CPU。 |
| `getup/tools/eval_v13.py` | 205 | getup-v13 の判定に使う量（2026-11-13、experiments/getup/v13_plan.md §3）。条件は v12 と同じ kp 7・ずれの上限 0.08 rad。CPU。 |
| `getup/tools/failure_modes.py` | 171 | 起き上がりの評価用の状態を動かし直して、失敗した体が途中で何をしているかを分類する（2026-11-02、L3 の成功と失敗の違いを調べるため）。 |
| `getup/tools/fall_survey.py` | 285 | 四脚歩行の方策が転ぶと、どの向きで止まるかを数える（2026-10-30、起き上がりの L3 を作る前の確かめ）。 |
| `getup/tools/hold_analysis.py` | 223 | 立ち上がった後の姿勢の維持を調べる（診断用、2026-10-15）。 |
| `getup/tools/hold_video.py` | 170 | 立った後の揺れの比較動画（診断用、2026-10-15）: 「方策のまま」と「途中から目標角を固定（PD と物理だけ）」を同じ状態・同じ個体差で並べる。 |
| `getup/tools/make_bank_v2.py` | 82 | 初期状態バンク v2 を作る: bank_v1 をそのまま先頭に置き、歩行中の転倒の状態（F、kind 2）を後ろに足す（2026-10-30、getup-v6 の L3 用）。 |
| `getup/tools/make_getup_urdf.py` | 170 | 起き上がり用の別名 URDF を作る: 床に当たるリンクの衝突形状を、凸包 1 個から「凸な部品いくつか」に作り直す。 |
| `getup/tools/pick_mirror_dir.py` | 84 | スイッチの向きを方策ごとに選ぶ（getup-v10 §10、2026-11-05）。評価に使わない転んだ状態で、left（左が下で反転）と right（右が下で反転）を比べる。 |
| `getup/tools/plot_current.py` | 72 | 起き上がりの電流の見積もり（getup/tools/current_estimate.py の結果）を時間の図にする（2026-11-06）。 |
| `getup/tools/plot_real_vs_sim_traj.py` | 87 | 実機の起き上がりの関節角と、同じ始めの姿勢からのシミュ（弱さの模型ごと、16 回の中央値）を重ねた図（2026-11-06 夜）。 |
| `getup/tools/real_repro_sweep.py` | 103 | 実機の起き上がりの試行の始めの姿勢から、サーボの強さ・硬さ・重さを変えて、実機と同じ失敗（肩が上限いっぱいで止まる）が出るかを見る（2026-11-06）。 |
| `getup/tools/real_vs_sim_traj.py` | 178 | 実機の起き上がりの記録と、同じ始めの姿勢から動かしたシミュを、関節角の時間の変化で比べる（2026-11-06 夜）。 |
| `getup/tools/real_vs_sim_video.py` | 184 | 実機の起き上がりの動画と、同じ始めの姿勢から動かしたシミュを横に並べた比較動画を作る（2026-11-06）。 |
| `getup/tools/run_r3_fit.py` | 78 | シミュの弱さの模型を実機の 11/9 の結果に合わせる（experiments/getup/v12_plan.md §1、結果を見る前に固定）。CPU。 |
| `getup/tools/sat_breakdown.py` | 129 | トルクが上限（100 %）に達した瞬間の内訳（診断用、2026-10-14）。 |
| `getup/tools/side_split.py` | 50 | 左右の体側ごとの起き上がりの成功を、シミュの評価用の状態で測る（2026-11-09、v11b に左右反転のスイッチが要るかの確認。判定には使わない）。CPU。 |
| `getup/tools/summarize_falls.py` | 53 | 転び方の数え上げ（fall_survey.py）の結果を 1 つの表にまとめる（2026-10-30）。 |
| `getup/tools/summarize_traj_fit.py` | 88 | 実機の起き上がりの 4 回と、弱さの模型ごとのシミュの合い方をまとめる（2026-11-06 夜）。 |
| `getup/tools/summarize_v10.py` | 113 | getup-v10 の結果をまとめて判定する（2026-11-05）。判定の基準は experiments/getup/v10_plan.md §3（学習の前に固定）。 |
| `getup/tools/summarize_v10_c3.py` | 108 | getup-v10 の C3（A1 の構成にシード 4・5・6 を足す）の結果をまとめて判定する（2026-11-06）。判定の基準は experiments/getup/v10_plan.md §11（学習の前に固定）。 |
| `getup/tools/summarize_v10_dir.py` | 97 | getup-v10 §10（スイッチの向きを方策ごとに選ぶ）の結果をまとめて判定する（2026-11-05）。基準は experiments/getup/v10_plan.md §10（検証の前に固定）。 |
| `getup/tools/summarize_v10_still_seeds.py` | 64 | getup-v10 の B1 のシード追加（シード 1〜6）の結果をまとめて判定する（2026-11-05）。判定の基準は experiments/getup/v10_plan.md §9（学習の前に固定）。 |
| `getup/tools/summarize_v10_sym.py` | 96 | getup-v10 の追加（sym に C1・C2 を足す）の結果をまとめて判定する（2026-11-05）。判定の基準は experiments/getup/v10_plan.md §8（学習の前に固定）。 |
| `getup/tools/summarize_v11.py` | 83 | getup-v11 の判定（experiments/getup/v11_plan.md §3、学習の前に固定）をまとめる（2026-11-06）。 |
| `getup/tools/summarize_v11c.py` | 102 | getup-v11c の判定（experiments/getup/v11_plan.md §7.3、学習の前に固定）をまとめる（2026-11-07）。 |
| `getup/tools/summarize_v12.py` | 77 | getup-v12 の判定（experiments/getup/v12_plan.md §3.3、学習の前に固定）をまとめる（2026-11-09）。 |
| `getup/tools/summarize_v12k.py` | 55 | getup-v12k の判定（experiments/getup/v12_plan.md §4、学習の前に固定）をまとめる（2026-11-10）。 |
| `getup/tools/summarize_v13.py` | 163 | getup-v13 のまとめ（2026-11-13、experiments/getup/v13_plan.md §3 の判定）。結果の JSON は experiments/getup/eval/v13/。 |
| `getup/tools/summarize_v13b.py` | 124 | getup-v13 の 2 回目のまとめ（2026-11-16、experiments/getup/v13_plan.md §7 の判定）。結果の JSON は experiments/getup/eval/v13/。 |
| `getup/tools/summarize_v13c.py` | 117 | getup-v13 の 3 回目のまとめ（2026-11-17、experiments/getup/v13_plan.md §8 の判定）。結果の JSON は experiments/getup/eval/v13/。 |
| `getup/tools/summarize_v13d.py` | 70 | getup-v13 の 4 回目のまとめ（2026-11-18、experiments/getup/v13_plan.md §9 の判定）。結果の JSON は experiments/getup/eval/v13/。 |
| `getup/tools/summarize_v7.py` | 132 | getup-v7 の結果をまとめて判定する（2026-11-02）。判定の基準は experiments/getup/v7_plan.md §3（学習の前に固定）。 |
| `getup/tools/summarize_v8.py` | 135 | getup-v8 の結果をまとめて判定する（2026-11-04）。判定の基準は experiments/getup/v8_plan.md §3（学習の前に固定）。 |
| `getup/tools/summarize_v9.py` | 120 | getup-v9 の結果をまとめて判定する（2026-11-04）。判定の基準は experiments/getup/v9_plan.md §3（学習の前に固定）。 |
| `getup/tools/verify_getup_urdf.py` | 94 | 起き上がり用の別名 URDF（make_getup_urdf.py が作る）を、元の URDF と Genesis（CPU）で比べる。 |
| `getup/train_getup1.py` | 151 | getup-v1 の学習（GetUpSim2RealPlan.md §4.7・§4.8）。設定はこのファイルの get_cfgs() / get_train_cfg() が唯一の出所。 |
| `getup/train_getup10.py` | 78 | getup-v10 の学習（2026-11-04）: getup-v9 の結果の土台に、候補 B・C を 1 つずつ足す。計画と判定の基準は experiments/getup/v10_plan.md（学習の前に固定）。 |
| `getup/train_getup11.py` | 154 | getup-v11 の学習（2026-11-06）: 実機の力の不足に合わせて、sym のシード 1（getup9-sym-s1）から学習を続ける。計画と判定の基準は |
| `getup/train_getup2.py` | 160 | getup-v2 の学習（2026-10-14）。設定はこのファイルの get_cfgs() / get_train_cfg() が唯一の出所。 |
| `getup/train_getup3.py` | 171 | getup-v3 の学習（2026-10-15）。設定はこのファイルの get_cfgs() / get_train_cfg() が唯一の出所。 |
| `getup/train_getup4.py` | 148 | getup-v4 の学習（2026-10-15）: v2 を土台に、v3 の変更を 1 つずつ（または選んだ組み合わせで）足す切り分け。 |
| `getup/train_getup6.py` | 132 | getup-v6 の学習（2026-10-30）: 採用版 v5 dcthr に、カリキュラムの段階 L3（横向き ＋ 歩行中の転倒 F）を足す。 |
| `getup/train_getup7.py` | 53 | getup-v7 の学習（2026-11-02）: getup-v6（L3）の弱点の、脱力の横倒しを改善する。計画と判定の基準は experiments/getup/v7_plan.md（学習の前に固定）。 |
| `getup/train_getup8.py` | 50 | getup-v8 の学習（2026-11-04）: getup-v7 の B（hard ＋ flipthr）に、カリキュラムの段階 L4（胸が上の範囲を含むすべての向き）を足す。 |
| `getup/train_getup9.py` | 54 | getup-v9 の学習（2026-11-04）: v7 の B に、左右対称を入れる。計画と判定の基準は experiments/getup/v9_plan.md（学習の前に固定）。 |

### real/（26 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `real/firmware_patches/build_fw.sh` | 103 | 梶田研の Meridian_LITE（s-kajita/Meridian_LITE）の固定コミットに起き上がり実験用のパッチを当て、 |
| `real/firmware_patches/flash_with_backup.py` | 164 | ESP32 のフラッシュ全体をバックアップしてから、アプリ（firmware.bin）だけを書き込む。 |
| `real/firmware_patches/khr-getup.4.patch` | 616 | 改造ファーム .4: 重力ベクトル・状態語・通信監視・IMU のまとめ読み・受信の読み捨て（6 章） |
| `real/firmware_patches/khr-getup.5.patch` | 834 | 改造ファーム .5（今の版）: .4 ＋ サーボの電流・温度・設定の読み出し（読むだけ）（6 章） |
| `real/firmware_patches/udp-drain-only.patch` | 99 | 受信の読み捨てだけを研究室の版にそのまま当てられる形に取り出した単独のパッチ（教授への説明用。実機には書き込んでいない） |
| `real/fw_check.py` | 661 | 改造ファーム（real/firmware_patches/khr-getup.N.patch）の実機確認ツール。 |
| `real/getup_session.py` | 1164 | 起き上がりの方策を実機で扱う道具（GetUpSim2RealPlan.md §5.5・§5.6）。今は R0（影の実行）と、その前の実機なしの確認だけ。 |
| `real/getup_then_walk.sh` | 50 | 起き上がって、そのまま歩く（つなぎを短くした版、11/10）。 |
| `real/imu_tests.py` | 193 | IMU の P0-1 の残りの確かめ（計画書 §5.2）: 斜めの姿勢・ゆっくり 360° 回す・落としたあとの戻り。 |
| `real/marker_track.py` | 414 | 実機の歩行の測り直し（2026-11-20）: 上から撮った動画のマーカーで、機体の位置・向き・速度を測る。 |
| `real/obs_check.py` | 151 | P0-3（観測の一致、GetUpSim2RealPlan.md §5.2）の単体テスト: 学習環境の状態を「実機から届く形」にしてから |
| `real/pose_session.py` | 326 | IMU の 6 姿勢試験（計画書 P0-1）を、サーボに電源を入れて姿勢を保ったまま行う。 |
| `real/protection_check.py` | 80 | プロテクション（ロックから設定の時間で出力 50 %）が起き上がりの間に働いたかを、サーボの電流で確かめる（2026-11-09）。 |
| `real/servo_drive_check.py` | 115 | 起き上がりの 1 回ごとに、肘のピッチのサーボが「遅れているのに押していない」かを見る（2026-11-13。卒論では扱わない） |
| `real/servo_failure_analysis.py` | 163 | 11/10 の左肘のピッチのサーボの記録を、実機のログ全部から調べる（2026-11-11、本人の依頼。卒論では扱わない） |
| `real/servo_jog.py` | 242 | サーボ 1 個だけに電源を入れ、今の角度から小さく 1 往復させる動作確認（PC → ESP32 → サーボの指令経路）。 |
| `real/servo_tel.py` | 300 | 改造ファーム khr-getup.5 のサーボの読み出し（肩・肘の電流と温度、全サーボの設定）を受ける・読む（2026-11-07）。 |
| `real/stand_cost.py` | 63 | 立ったあとに方策が目標角を動かし続けることの実害を、11/9 の実機ログで見る（2026-11-10）。 |
| `real/step_response.py` | 527 | E1-lite: 関節のステップ応答（計画書 §5.3。遅れ・立ち上がり・減衰を測り、学習環境のサーボのモデルと比べる）。 |
| `real/summarize_r3.py` | 151 | 実機の起き上がり 2 回目（2026-11-09）の全試行を同じ基準でまとめる。 |
| `real/unified_session.py` | 646 | 四脚歩行と起き上がりを 1 つの方策（unified、論文には入れない本人の興味）で実機を動かす道具（2026-11-25）。 |
| `real/video_analysis.py` | 229 | 11/9 実機の動画 IMG_0018〜0043 と実機ログの対応、手の写り込み、立っている間の揺れ、脱力のあとの様子を求める（2026-11-09）。 |
| `real/video_analysis_1110.py` | 461 | 11/10 実機の動画 IMG_0044〜0081 と実機ログの対応・分析（2026-11-11）。 |
| `real/walk_analyze.py` | 253 | walk_session の記録（real/data/raw/walk_*.npz）を分析し、同じ指令の列を学習環境（Genesis）でも動かして比べる。 |
| `real/walk_joints.py` | 265 | v31 の実機歩行の記録で、22 関節すべての動きを学習環境と比べ、関節の符号表（khr_common/joint_map.py、全て +1）を確かめる。 |
| `real/walk_session.py` | 616 | 四脚歩行の方策（既定 v31-s2）を実機で動かす、画面なしの実行ツール。コンソール（Meridian_consoleS_quad*.py）の代わり。 |

### sysid/（5 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `sysid/closed_loop.py` | 247 | 学習環境（Genesis）で四脚歩行の方策を、walk_session と同じ観測の作り方で何体も同時に動かす（閉ループ）。 |
| `sysid/sim_disp.py` | 46 | 歩行の速さの比較（2026-11-10 追加）: 実機と同じ指令の列（前後・左右）を学習環境で 1 体動かし、胴体の水平の移動量を出す（世界座標の x が始めの前、y が左）。 |
| `sysid/sim_replay.py` | 196 | E4a（GetUpSim2RealPlan.md §5.3）: 実機の記録を短い区間に切り、各区間を実機の状態から始めて、実際に送った目標角で学習環境を動かす。 |
| `sysid/step_sim.py` | 110 | E1-lite のシミュ側: 学習環境のサーボのモデルで、実機と同じステップ応答を計算する（計画書 §5.3・§5.4、2026-10-19）。 |
| `sysid/walk_sweep.py` | 240 | v31 の実機歩行と学習環境のずれ（傾き・旋回 88 %・関節の追従・可動域の端）が、どの「実機との違い」で再現できるかを探す。 |

### unified/（33 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `unified/envs/unified_env0.py` | 370 | 四脚歩行と起き上がりを 1 つの方策で（論文には入れない、本人の興味）: 段階 0 の環境（2026-11-20）。 |
| `unified/envs/unified_env0r.py` | 33 | 段階 0 の変種 0r（2026-11-21）: 行動の変化の罰 2 項を「制限の前の目標角」で測る。ほかは unified_env0 と同じ。 |
| `unified/envs/unified_env1.py` | 139 | 四脚歩行と起き上がりを 1 つの方策で: 段階 1 の環境（2026-11-22、論文には入れない）。計画は experiments/unified/stage1_plan.md（§5.2 に混ぜ方の直し）。 |
| `unified/envs/unified_env2.py` | 70 | 四脚歩行と起き上がりを 1 つの方策で: 段階 1 の直しと改善案の環境（2026-11-22、論文には入れない）。 |
| `unified/envs/unified_env3.py` | 52 | 四脚歩行と起き上がりを 1 つの方策で: 指令 0 では立ち止まる（2026-11-23、段階 1b の次の案、論文には入れない）。 |
| `unified/envs/unified_env4.py` | 57 | 四脚歩行と起き上がりを 1 つの方策で: 体全体が弱いエピソードを混ぜる（2026-11-24、論文には入れない）。 |
| `unified/eval_walk.py` | 194 | 1 つの方策（段階 0 以降）の歩行の測定と動画（2026-11-20）。v31 の比例ゲインの測定（experiments/v31_kp_robustness/plan.md、 |
| `unified/jobs/getup_eval_after.sh` | 17 | 段階 1 のシードの学習と歩行の測定（run_stage1.sh）が終わるのを待って、起き上がりの測定（eval_getup_u）を CPU で回す（2026-11-22）。 |
| `unified/jobs/run_dir_push.sh` | 80 | 前進以外の指令（後退・左右の旋回・左の横移動）と押しを、1 つの方策（C）と v31 で測る（2026-11-24、本人「６、７は測ってください」。記録だけ）。 |
| `unified/jobs/run_stage0.sh` | 47 | 四脚歩行と起き上がりを 1 つの方策で: 段階 0 の待ち行列（2026-11-20、experiments/unified/stage0_plan.md）。 |
| `unified/jobs/run_stage0c.sh` | 44 | 張りつきの調べの 1 つの変更、2 回目（2026-11-21、experiments/unified/saturation/README.md §5）: 方策の平均の目標角が周期ごとに跳ぶことを |
| `unified/jobs/run_stage0d.sh` | 44 | 張りつきの調べの 1 つの変更、3 回目（2026-11-21、experiments/unified/saturation/README.md §7）: 固定した std を 1000〜3000 イテレーションで |
| `unified/jobs/run_stage0r.sh` | 43 | 張りつきの調べの 1 つの変更（2026-11-21、experiments/unified/saturation/README.md §3）: 行動の変化の罰を制限の前の目標角で測る unified_env0r。 |
| `unified/jobs/run_stage1.sh` | 39 | 段階 1（2026-11-22、experiments/unified/stage1_plan.md）: 四脚歩行と起き上がりを 1 つの方策に。起き上がり getup13-kpjk-long の同じシードの |
| `unified/jobs/run_stage1x.sh` | 54 | 段階 1 の直しと改善案（2026-11-22、experiments/unified/stage1_analysis.md）を 3 シードずつ回す待ち行列。 |
| `unified/ppo_caps.py` | 242 | PPOBound（getup/ppo_bound.py）に、方策の平均の目標角が周期ごとに跳ぶことへの罰（CAPS の時間の項）を足したもの（2026-11-21）。 |
| `unified/tools/analyze_saturation.py` | 193 | 目標角の張りつきの中身を調べる（2026-11-21、段階 0b のあと。本人「張り付きを調べた後に段階１の案を作ってください。」）。 |
| `unified/tools/diag_kp5.py` | 244 | 比例ゲイン 5 で 1 つの方策の胴体が沈む原因を、学習せずに調べる（2026-11-24、本人「１をやってみてほしい」）。 |
| `unified/tools/diag_still.py` | 133 | 指令 0 のとき、起き上がったあとに足踏みしているか・胴体が沈むかを比例ゲインごとに測る（2026-11-23、段階 1b の次の案の確かめ）。 |
| `unified/tools/eval_getup_u.py` | 287 | 段階 1 の起き上がりの測定（2026-11-22、experiments/unified/stage1_plan.md §3）。getup/tools/eval_v13.py の A・B・D と kp-sweep を、 |
| `unified/tools/eval_push_recover.py` | 156 | 押されて転んだあと、起き上がって歩き直せるかを測る（2026-11-24、本人「６、７は測ってください」。1 つの方策だけ、記録だけ）。 |
| `unified/tools/imu_offset_sim.py` | 191 | IMU の向きのずれで 1 つの方策が止まるかをシミュで見る（2026-11-26、experiments/unified/real_pose_sim.md §6）。 |
| `unified/tools/kl_split.py` | 96 | 方策の変化（KL）が、立っている状態と起き上がりの途中の状態のどちらで大きいかを測る（2026-11-22、段階 1 の分析）。 |
| `unified/tools/make_digest.py` | 125 | 1 つの方策の各版の動画を 1 本にまとめる（2026-11-23、本人の依頼「各版の動画をわかりやすい様に一つの動画に」）。 |
| `unified/tools/make_reference.py` | 459 | 各版の参考動画（多視点＋計測の表示）を作る（2026-11-24、本人の依頼「改善点を見つけやすいように各種版の参考動画を。 |
| `unified/tools/noise_vs_rate.py` | 108 | 探索のゆらぎと速さの制限の関係を測る（2026-11-21、0c のシード 1 が歩かなかったあと）。 |
| `unified/tools/real_pose_sim.py` | 292 | 11/25 の実機の姿勢をシミュに置いて、同じことが起きるかを見る（2026-11-26、本人「優先度順の２に取り掛かって」）。 |
| `unified/tools/reward_budget.py` | 118 | 学習と同じ条件で、報酬の項ごとの大きさを「立っている（α ≥ 0.99）／起き上がりの途中（α < 0.99）」に分けて測る（2026-11-22、段階 1 の分析）。 |
| `unified/tools/summarize_dir_push.py` | 106 | 前進以外の指令と押しの測定（unified/jobs/run_dir_push.sh）を、C・C を gap 0.10 で・v31 で並べた表にする（2026-11-24、記録だけ）。 |
| `unified/tools/summarize_stage0.py` | 93 | 段階 0 のまとめ（experiments/unified/stage0_plan.md §4 の基準）。結果は experiments/unified/stage0_results.md。 |
| `unified/tools/walk_alpha.py` | 121 | 歩いている間の「立っている度合い α」と胴体の高さを測る（2026-11-22、段階 1 の分析 experiments/unified/stage1_analysis.md）。 |
| `unified/train_unified0.py` | 206 | 四脚歩行と起き上がりを 1 つの方策で: 段階 0 の学習（2026-11-20、論文には入れない）。計画と判定の基準は experiments/unified/stage0_plan.md。 |
| `unified/train_unified1.py` | 261 | 四脚歩行と起き上がりを 1 つの方策で: 段階 1 の学習（2026-11-22、論文には入れない）。計画と判定の基準は experiments/unified/stage1_plan.md。 |

### experiments/（16 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `experiments/ablation_v31/check_split_seeds.py` | 46 | 報酬の総点検（v31 基準）で、seed で結果が割れたために悪化と判定されなかった指標を挙げる（2026-10-23）。 |
| `experiments/real/session7_sim/run_sim.sh` | 14 | 実機の歩行の測り直し（session7_plan.md）と同じ指令の列を、学習環境で 1 体動かした移動量（sysid/sim_disp.py、CPU）。2026-11-20 |
| `experiments/real/session7_sim/summarize.py` | 24 | session7 のシミュの移動量をまとめる（run_sim.sh の出力）。2026-11-20 |
| `experiments/retrain_fixurdf/make_queue.py` | 52 | 機体のモデルの可動域に合わせた、全版の学習し直しの待ち行列を作る（卒論では扱わない） |
| `experiments/retrain_fixurdf/summarize.py` | 129 | 全版の学習し直し（fixurdf-*）を版ごとに集計する（卒論では扱わない） |
| `experiments/thesis_figs/make_diagrams.py` | 356 | 卒論の仕組みの図（模式図）を描く（2026-10-26、v4 で追加。2026-11-11 に rlloop・actorcritic・system・joints を描き直した）。 |
| `experiments/thesis_figs/make_figs.py` | 792 | 卒論の図を、研究の記録（機械可読のファイル）から作る（2026-10-23）。 |
| `experiments/thesis_figs/make_getup_walk_frames.py` | 50 | 卒論の図: 実機で仰向けから起き上がり、そのまま四脚で歩くこま（2026-11-11、卒論 v13）。 |
| `experiments/thesis_figs/make_real_frames.py` | 96 | 卒論の図: 実機の四脚歩行のこま（2026-10-23）。 |
| `experiments/thesis_figs/record_gait.py` | 195 | 卒論の「歩き方の分析」の材料: v31 の方策をシミュレーションで動かし、関節ごとのトルクと歩容の時系列を記録する（2026-10-26）。 |
| `experiments/thesis_figs/record_getup_seq.py` | 93 | ゼミのドラフトの図「起き上がりの連続図」のデータを作る（2026-11-02）。 |
| `experiments/thesis_figs/record_jointerr.py` | 71 | 卒論の「実機とシミュレーションの比較」の材料: 関節ごとの追従のずれ（目標関節角と実際の関節角の差）を、実機とシミュレーションで比べる（2026-10-26）。 |
| `experiments/thesis_figs/record_pooled_sigma.py` | 116 | シード間のばらつき σ の取り方による判定の感度（卒論 v7 の 6.3・6.4・8.6 節、他の AI の改善案 B3、2026-10-28）。 |
| `experiments/thesis_figs/record_simreal.py` | 43 | 卒論の「実機とシミュレーションの比較」の図の材料: 実機の歩行 3（2026-10-13）と同じ指令の列で、学習環境の機体を動かした記録を残す（2026-10-26）。 |
| `experiments/thesis_figs/welch_check.py` | 71 | 2σ の判定と Welch の t 検定（両側、95 % 信頼区間）を比べる（2026-11-11、院生の指摘 1 への確認）。 |
| `experiments/v31_kp_robustness/analyze.py` | 101 | 比例ゲインのずれへの強さの集計（判定の基準は plan.md §4、計算の前に固定）。 |

### docs/tools/（1 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `docs/tools/make_seminar_20261204_figs.py` | 244 | 12/4 のゼミの進捗報告の図（2026-11-26、本人「来週の金曜日のゼミで進捗報告を行うから、材料を集めてほしい」）。 |

### biped/（12 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `biped/khr_env.py` | 630 | 二足歩行の学習環境（khr_rl_sample 由来、脚 12 関節、観測 71 次元） |
| `biped/khr_eureka/env_context.py` | 108 | LLM に渡す「環境コンテキスト」。 |
| `biped/khr_eureka/llm_client.py` | 194 | Gemini の REST クライアント（モデルフォールバック対応）. |
| `biped/khr_eureka/prompts.py` | 121 | Eureka のプロンプト群（KHR 二足歩行タスク向けに調整）. |
| `biped/khr_eureka/reflection.py` | 77 | 学習結果から reward reflection フィードバック文字列を構築する. |
| `biped/khr_eureka/reward_env.py` | 270 | LLM 生成報酬を注入する KHR 環境と、候補評価ユーティリティ. |
| `biped/khr_eval.py` | 59 | 二足歩行の方策を画面で再生する（CPU） |
| `biped/khr_eval_metrics.py` | 160 | 学習済みポリシーを「ビューアなしで定量評価」し、比較用メトリクスを表示する. |
| `biped/khr_train.py` | 239 | 二足歩行の学習スクリプト（設定は get_cfgs・get_train_cfg） |
| `biped/khr_train_eureka.py` | 410 | Eureka による報酬自動設計付き KHR 歩行学習. |
| `biped/khr_train_ql.py` | 239 | 二足歩行の学習スクリプトの別の版（脚の初期の角度だけが違う） |
| `biped/pd_test.py` | 165 | 二足の機体の PD 制御の単体テスト（図を出す） |

### go2_reference/（3 本）

| ファイル | 行数 | 何をするか |
|---|---|---|
| `go2_reference/go2_env.py` | 308 | Genesis の四足ロボット Go2 の見本の環境（参考。どこからも import しない） |
| `go2_reference/go2_eval.py` | 59 | Go2 の見本の再生（参考） |
| `go2_reference/go2_train.py` | 183 | Go2 の見本の学習スクリプト（参考） |
