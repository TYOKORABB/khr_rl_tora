"""学習を始めたときのコードの状態を、学習の出力先に残す（Genesis 非依存、標準ライブラリだけ）。

  from khr_common.run_record import save_code_state
  info["code_state"] = save_code_state(log_dir)        # log_dir/code_state/ に書く

なぜ必要か: 2026-10-14 時点で、experiments/ の学習記録 177 本のうち 173 本が「未コミットの変更あり」で学習していた。
コミットの番号だけでは、どのコードで学習したかを再現できない。rsl-rl の `add_git_repo_to_log` は追跡中のファイルの
差分しか残さないので、まだ git に入れていない新しいファイル（新しい版の学習スクリプトなど）の中身も残す。

書くもの（リポジトリごと。既定は khr_rl_tora と、編集可能モードで入れている ../Genesis）:
  <名前>.txt                コミット・ブランチ・git status・`git diff HEAD`（追跡中のファイルの、まだコミットしていない変更）
  <名前>_untracked.tar.gz   git に入っていないコードファイル（.py .sh .yaml .yml .toml、1 ファイル 1 MB まで）の中身
"""

from __future__ import annotations

import subprocess
import tarfile
from pathlib import Path

from khr_common.paths import REPO_ROOT

CODE_SUFFIXES = {".py", ".sh", ".yaml", ".yml", ".toml"}
MAX_BYTES = 1 << 20


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


def save_code_state(log_dir: str | Path, repos: list[Path] | None = None) -> dict:
    """log_dir/code_state/ にコードの状態を書き、要約（run_info.json に入れる用）を返す。失敗しても学習は止めない。"""
    out = Path(log_dir) / "code_state"
    out.mkdir(parents=True, exist_ok=True)
    if repos is None:
        repos = [REPO_ROOT] + [p for p in (REPO_ROOT.parent / "Genesis",) if (p / ".git").exists()]
    summary = {}
    for repo in repos:
        name = repo.resolve().name
        try:
            commit = _git(repo, "rev-parse", "HEAD").strip()
            branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
            status = _git(repo, "status", "--porcelain=v1")
            diff = _git(repo, "diff", "HEAD")
            untracked = [f for f in _git(repo, "ls-files", "--others", "--exclude-standard").splitlines()
                         if Path(f).suffix in CODE_SUFFIXES and (repo / f).stat().st_size <= MAX_BYTES]
            (out / f"{name}.txt").write_text(
                f"--- commit ---\n{commit}\n\n--- branch ---\n{branch}\n\n--- git status --porcelain ---\n{status}\n"
                f"--- git diff HEAD ---\n{diff}", encoding="utf-8")
            if untracked:
                with tarfile.open(out / f"{name}_untracked.tar.gz", "w:gz") as tar:
                    for f in untracked:
                        tar.add(repo / f, arcname=f)
            summary[name] = {"commit": commit[:12], "dirty": bool(diff.strip()), "untracked_code_files": len(untracked)}
        except Exception as e:  # git が無い・リポジトリでない等。記録できなかったことだけ残す
            summary[name] = {"error": f"{type(e).__name__}: {e}"[:200]}
    return summary
