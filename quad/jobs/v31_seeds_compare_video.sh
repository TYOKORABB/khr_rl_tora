#!/bin/bash
# v31 の 3 seed を並べた比較の動画（1 体ずつ → 群れ → 1 体ずつ の 3 本を作ってつなぐ）
cd "$(dirname "$0")/../.."   # リポジトリのルート
source ../bin/activate
E=(khr-quadruped31-s1 khr-quadruped31-s2 khr-quadruped31-s3)
C=(--stats_prefix experiments/quad_progress/v31 --marks 100 200 300 400 1000 2000 3200 3999 --card_s 6)
OUT=media/videos/quad_progress
TMP=${TMP:-$(mktemp -d)}   # 3 つの部分（つなぐ前）を置く。C だけ作り直すときは前と同じ TMP を渡す
export DISPLAY=:1 OMP_NUM_THREADS=5

partA() {
python quad/khr_quad_progress.py compare -e "${E[@]}" "${C[@]}" --first 1 \
  --intro "v31 の 3 seed の比較" "同じ設定・同じ報酬で、学習の乱数の種（seed）だけを変えた 3 本" \
    "同じ時点・同じ指令・同じ押しで横に並べて動かす（行動の乱数・個体差なし）。見えた違いはすべて seed によるもの" \
    "図: はじめて基準を満たした学習の回数（点の横の数字が seed）" \
  --intro_image experiments/quad_progress/v31_seeds_milestones.png --intro_s 10 \
  --scene 100 diag "0,0,0.5:5" "その場旋回を最初に覚えるのは？" \
    "学習で最初にできるようになるのはその場旋回。その時期が seed で違う/左旋回の達成率: 100 回目 {turn} → 200 回目 {turn@200} → 300 回目 {turn@300}" \
  --scene 200 diag "0,0,0.5:5" "seed 1 も回れるようになる。seed 3 はまだ" \
    "左旋回の達成率: {turn}/seed 3 は 300 回目に回れるようになる" \
  --scene 300 diag "0,0,0.5:3;0.3,0,0:6" "seed 3 も回れる。前に歩き出したのは seed 1 だけ" \
    "左旋回 {turn}/前進 {fwd}・後退 {back}/400 回目には 3 seed とも前後に歩ける（前進 {fwd@400}）" \
  -o $TMP/cmp_A.mp4 2>&1 | grep "^\[compare\]\|Error"
}

partB() {
python quad/khr_quad_progress.py compare -e "${E[@]}" "${C[@]}" --first 4 --crowd \
  --scene 400 crowd "" "押しへの強さ: 歩き出したばかり" \
    "30 体ずつ（5 つの指令 × 6 体）に、学習の最後と同じ全強度の押し（3 秒ごと）/押しの向きと大きさは乱数。3 seed に同じ乱数を使う/赤い輪が転んだ所。転んだ体は最初の位置に戻して続ける/測定（同じ条件を 3 回）で転んだ回数: {push}" \
  --scene 1000 crowd "" "押しへの強さ: 中盤も seed 1 は転びやすい" \
    "測定で転んだ回数: 400 回目 {push@400} → 1000 回目 {push}/学習では押しを 2080 回目まで少しずつ強くしている" \
  --scene 2000 crowd "" "押しへの強さ: 2000 回目には 3 seed とも転ばない" \
    "測定で転んだ回数: {push}/学習の押しが最大になる 2080 回目とほぼ同じ時期" \
  -o $TMP/cmp_B.mp4 2>&1 | grep "^\[compare\]\|Error"
}

partC() {
python quad/khr_quad_progress.py compare -e "${E[@]}" "${C[@]}" --first 7 \
  --scene 3200 side "0.3,0,0:6" "終盤: 脚を大きく振り始める時期が seed で違う" \
    "前進のときの膝の振れ幅: {knee}（2000 回目は {knee@2000}）/seed 1・2 は 2900〜3000 回目に大きく振り始めた。seed 3 は 3800 回目から/横から 0.5 倍速で、脚の振り方を比べる" \
  --scene 3999 diag "0.3,0,0:3;push:0,-1.0;0.3,0,0:2;0,0,0.5:2.5;0,0.15,0:2.5;-0.3,0,0:2.5" "完成: 3 seed とも全方向に歩き、押されても転ばない" \
    "前進 {fwd}・後退 {back}・左へ {left}・左旋回 {turn}/膝の振れ幅 {knee}、後脚の足上げ {clear_r}" \
  --scene 3999 back "0.3,0,0:5" "完成: 後ろから見ると、後脚の幅と胴体の傾きが違う" \
    "前進中の後脚の左右の間隔（別の測定、64 体・個体差あり）: 8.0・4.4・6.7 cm/胴体の傾き（前進、8 体）: {tilt}" \
  --outro "3 seed の違いのまとめ" "同じ設定で、学習の乱数の種（seed）だけが違う 3 本" \
    "覚える順番は 3 seed で同じ: その場旋回 → 前後 → 押しに強くなる → 横歩き・脚の大きな振り" \
    "その時期は seed でずれる: その場旋回は 100〜300 回目、横歩きは 1200〜2400 回目、脚の大きな振りは 2900〜3800 回目" \
    "押しへの強さは中盤に大きく違う（400 回目で 37・7・16 回）。2000 回目ごろに 3 seed とも転ばなくなる" \
    "完成した方策の達成率は近い。くせは残る: seed 2 は前進が遅く胴体が傾く、seed 3 は足上げが低い" \
    "→ 1 seed だけで「何回目に何ができるか」を言うと、100〜1200 回ずれる" \
  --intro_image experiments/quad_progress/v31_seeds_milestones.png --outro_s 14 \
  -o $TMP/cmp_C.mp4 2>&1 | grep "^\[compare\]\|Error"
}

if [ "$1" = "C" ]; then partC; else partA & partB & partC & wait; fi
printf "file '%s'\n" $TMP/cmp_A.mp4 $TMP/cmp_B.mp4 $TMP/cmp_C.mp4 > $TMP/cmp_list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i $TMP/cmp_list.txt -c copy -movflags +faststart $OUT/v31-seeds_compare.mp4
ffmpeg -i $OUT/v31-seeds_compare.mp4 2>&1 | grep Duration
