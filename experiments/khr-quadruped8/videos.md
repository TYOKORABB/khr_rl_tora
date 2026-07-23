# khr-quadruped8 (v8) — 6方向 動作記録

ckpt `model_3999.pt` / 各10秒 / 観測ノイズ・ドメインランダム化は無効（素の方策の実力を見るため）。
録画スクリプト: `khr_quad_record5.py`（`khr_quad_env5` を読む v8 用。`*.mp4` は .gitignore 対象なので
動画本体はリポジトリに含まれない）。

## 動画一覧と実測追従

「実測」は立ち上がり2秒を除いた8秒間の平均。速度は移動座標系（`loco_lin_vel` /
`loco_ang_vel`）で評価している — 胴体が90°ピッチしているため、ベース座標系のままでは
前後方向を取り違える。

| 動画 | 指令 (vx, vy, wz) | 実測 (vx, vy, wz) | 追従率 |
|---|---|---|---|
| `walk_v8_forward.mp4`    | (+0.40, 0, 0)     | (+0.347, +0.000, +0.066) | 87% |
| `walk_v8_backward.mp4`   | (−0.25, 0, 0)     | (−0.019, −0.019, −0.003) | **7%** |
| `walk_v8_left.mp4`       | (0, +0.15, 0)     | (+0.036, +0.095, +0.053) | 63% |
| `walk_v8_right.mp4`      | (0, −0.15, 0)     | (+0.032, −0.138, +0.017) | 92% |
| `walk_v8_turn_left.mp4`  | (0, 0, +0.50)     | (+0.034, +0.005, +0.454) | 91% |
| `walk_v8_turn_right.mp4` | (0, 0, −0.50)     | (+0.026, −0.012, −0.503) | 101% |

再現コマンド:

```bash
export DISPLAY=:1
python khr_quad_record5.py -e khr-quadruped8 --ckpt 3999 --vx  0.40 --seconds 10 -o walk_v8_forward.mp4
python khr_quad_record5.py -e khr-quadruped8 --ckpt 3999 --vx -0.25 --seconds 10 -o walk_v8_backward.mp4
python khr_quad_record5.py -e khr-quadruped8 --ckpt 3999 --vy  0.15 --seconds 10 -o walk_v8_left.mp4
python khr_quad_record5.py -e khr-quadruped8 --ckpt 3999 --vy -0.15 --seconds 10 -o walk_v8_right.mp4
python khr_quad_record5.py -e khr-quadruped8 --ckpt 3999 --wz  0.50 --seconds 10 -o walk_v8_turn_left.mp4
python khr_quad_record5.py -e khr-quadruped8 --ckpt 3999 --wz -0.50 --seconds 10 -o walk_v8_turn_right.mp4
```

## 考察

### 後退が動かないのは学習範囲外だから（バグではない）

v8 の学習コマンド範囲は `khr_train_quad8.py` で

```python
"lin_vel_x_range": [0.0, 0.4],
```

となっており、**負の vx は一度も経験していない**。撮影した後退動画は完全な
未学習領域(out-of-distribution)であり、方策は「転ばずにその場に留まる」挙動を選んでいる
（実測 −0.019 m/s ≒ ほぼ静止、転倒はしない）。資料として残すが、性能評価には使えない。

後退を実現するなら `lin_vel_x_range` を `[-0.2, 0.4]` 等に広げて再学習する必要がある。
ただし前進性能とのトレードオフが起きうるので、実機検証の後に判断するのが妥当。

### 左右非対称（左横 63% / 右横 92%）

横移動は右方向の方が明確に得意。左横では指令外の前進成分 +0.036 m/s と旋回 +0.053 rad/s が
乗っており、真横ではなく弧を描いている。原因の候補は
(a) 初期姿勢・URDF の左右非対称、(b) 横移動報酬が左右で均等に学習されていない、の2つ。
v4→v8 を通じて横方向は一貫して弱い項目であり、改善余地として残る。

### 旋回は左右とも良好

左 91% / 右 101% と、旋回は 6方向で最も指令に忠実。v7 の 85% からも改善している。
