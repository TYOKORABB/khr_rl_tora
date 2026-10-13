# real/ — 実機側（Meridian 経由の Sim2Real）

`GetUpSim2RealPlan.md` §4.1・§5.2 の実機側のコード。実行はリポジトリのルートから `python -m real.<名前>`。

| パス | 内容 |
|---|---|
| `firmware_patches/` | ESP32 ファーム（梶田研の Meridian_LITE）への改造パッチ `khr-getup.1`: IMU の重力ベクトル送信と通信監視による脱力。詳細は同フォルダの README |
| `fw_check.py` | 改造ファームの実機確認ツール（状態表示・IMU の 6 姿勢記録と取り付け回転の推定・通信監視の試験）。サーボに電源を入れる指令は送らない |
| `calib/` | 実機で測った IMU の取り付け回転など（`fw_check pose` / `solve` が書く） |

PC 側の共通コードは `khr_common/`（`gravity.py`: IMU 信号 → base 座標の重力ベクトル）。

## 出所とライセンス

- `firmware_patches/khr-getup.1.patch` は `s-kajita/Meridian_LITE`（公開 fork）のコミット `85a62d1` に対する差分で、
  差分の文脈として元のコードを数行ずつ含む。上流は `Ninagawa123/Meridian_LITE`
  — MIT License, Copyright (c) 2021 Ninagawa123 (GitHub) and Project Meridian Team。
- 四脚デプロイヤ（`Meridian_consoleS_quad.py`・`khr_quad_env_no_gs.py`）は研究室の手元にだけある版なので、
  梶田先生の了承を得るまでこのリポジトリには入れない（計画書 §4.1）。
- Wi-Fi の設定（`keys.h`）・`board_ip.txt`・生ログ（`data/raw/`）はコミットしない（`.gitignore`）。
