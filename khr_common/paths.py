"""リポジトリ内のパス解決（Genesis 非依存）。

GetUpSim2RealPlan.md §4.1 の方針:
  - パスは `__file__` から解決する（作業ディレクトリに依存しない）
  - アセットは環境変数 KHR_ASSETS で上書きできる
  - 四脚歩行のモジュール（`quad/`。`../assets/...` を作業ディレクトリ基準で読む
    khr_quad_env21.py など）のために `chdir_repo_root()` を用意する
  - `quad/` のモジュールは名前で import される（`import khr_quad_env21`）ので、
    このモジュールを import した時点で `quad/` と v1〜v15 の退避先を sys.path に入れる

実機側（Genesis が入っていない PC）からも import できるよう、
このモジュールは標準ライブラリだけを使う。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

#: このリポジトリのルート（khr_common/ の親）
REPO_ROOT = Path(__file__).resolve().parent.parent

#: URDF とメッシュの置き場。既定はリポジトリの兄弟 `../assets`。
#: 意図的にリポジトリ外（別マシンでは別の場所）なので環境変数で上書きできる。
ASSET_DIR = Path(os.environ.get("KHR_ASSETS", REPO_ROOT.parent / "assets")).resolve()

#: 学習成果物（gitignore 済み）
LOG_ROOT = REPO_ROOT / "logs"

#: 実験記録（git 管理）
EXPERIMENT_ROOT = REPO_ROOT / "experiments"

#: 四脚歩行（v16〜v31 の環境・学習・測定）。v1〜v15 は quad/archive_v1_v15/
QUAD_DIR = REPO_ROOT / "quad"
for _d in (QUAD_DIR / "archive_v1_v15" / "train", QUAD_DIR / "archive_v1_v15" / "envs", QUAD_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

#: 四足歩行 v30/v31 が使う左右対称化した URDF
URDF_SYMHIP = ASSET_DIR / "khr3hv" / "urdf" / "khr3hv_symhip.urdf"

#: 上流のオリジナル URDF（r_hip_pitch の可動域が鏡像で誤っている版）。
#: experiments/urdf_hip_pitch_bug.md 参照。比較用にのみ使う。
URDF_ORIGINAL = ASSET_DIR / "khr3hv" / "urdf" / "khr3hv.urdf"


def chdir_repo_root() -> Path:
    """作業ディレクトリをリポジトリのルートへ移し、元のディレクトリを返す。

    `quad/` の四脚歩行のモジュールは URDF を相対パス `../assets/...` で読むため、
    `python -m getup.xxx` をどこから起動してもよいようにする。
    """
    prev = Path.cwd()
    os.chdir(REPO_ROOT)
    return prev


def require(path: Path, what: str) -> Path:
    """存在しなければ、直し方がわかるメッセージで落とす。"""
    if not path.exists():
        raise FileNotFoundError(
            f"{what} が見つかりません: {path}\n"
            f"  アセットは意図的にリポジトリ外にあります。別の場所にある場合は\n"
            f"  環境変数 KHR_ASSETS でディレクトリを指定してください（現在: {ASSET_DIR}）。"
        )
    return path
