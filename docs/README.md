# docs/ — 文書

| ファイル | 中身 |
|---|---|
| `DevelopmentDiary_v2.md` | **開発日誌（再構築版、2026-10-14〜）**。旧日誌を読み直し、今の状態（URDF 是正後の 3 seed の数値・実機・起き上がり・基盤）と照らし合わせて組み立て直したもの。**まずこれを読む** |
| `DevelopmentDiary.md` | 開発日誌（旧版、2026-07-24〜10-14 の一次記録）。細かい表や途中経過はこちら。対応は再構築版の付録 G |
| `GetUpSim2RealPlan.md` | 起き上がりと Sim2Real の計画書（版ごとの改訂履歴つき） |
| `GetUpOverview.md` | **起き上がりのまとめ（2026-10-30）**。課題・学習の手法・報酬の式と版ごとの重み・評価の方法・v1〜v5 の結果と分析・先輩の方法との比較・実機の準備 |
| `ResearchPlan.md` | 研究方針と論文の主張の候補 |
| `ThesisOutline.md` | 論文の章立ての骨組み（案、2026-10-21）。卒論の本文は `../soturon_ban/`（git 外）で、章立てはテンプレートに従う |
| `ThesisClaims.md` | **論文の主張の置き方の整理（2026-10-23）**。候補 A・B・C の是正後の証拠・弱いところ・構成の案・教授と決めること |
| `RewardReference.md` | 四脚歩行の報酬の説明と、ablation の実測（一部は `quad/update_reward_reference.py` が自動生成） |
| `RealRobotVerification.md` | 実機の動作確認の手順書（v1〜v8 のころのもの。今の実機の手順は `real/README.md`） |

起き上がりの全体（手法・報酬・各版の結果）は `GetUpOverview.md`、版ごとの記録は `getup/DIARY.md`、実機の現状は `real/ROBOT_STATUS.md`。
