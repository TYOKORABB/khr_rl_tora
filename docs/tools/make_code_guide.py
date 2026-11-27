"""プログラムの解説（docs/CodeGuide/）を、解説の元のファイル（docs/CodeGuide/_spec/*.txt）から作る（2026-11-27）。

本人の依頼（11/27）:「ゼミで、プログラムの解説をできる様にしておいた方がいいとのこと。特に重要なところは一行ごとに解説できる状態に」。
コードの引用と行番号は、手で写すと誤りが入るので、このスクリプトが実際のファイルから取り出す。

  python docs/tools/make_code_guide.py            # 全部の章を作り直す（解説の抜けがあれば警告）
  python docs/tools/make_code_guide.py --strict   # 警告があれば失敗にする（コードが変わって行がずれたのを見つける）

元のファイルの書き方:
  ふつうの行                       … そのまま Markdown として出す
  @code <パス> <範囲> <見出し>     … コードの引用を始める。範囲は 466-475 や 124-125,132-139（飛ばした所は ⋮）
  <行>: <解説>  /  <行>-<行>: <解説> … 引用の中の行の解説（@code のあとに続ける）
  @end                             … 引用の終わり（次の @code やふつうの行の前に書く）
  @inventory <ディレクトリ> ...    … 全ファイル一覧の表（各ファイルの先頭の説明文から）。_spec/inventory_override.txt で書き換えられる
引用の中で、空行とコメントだけの行は解説がなくてよい。それ以外の行に解説がないと警告を出す。
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC_DIR = REPO / "docs" / "CodeGuide" / "_spec"
OUT_DIR = REPO / "docs" / "CodeGuide"
LANG = {".py": "python", ".sh": "bash", ".patch": "cpp", ".h": "cpp", ".cpp": "cpp"}


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:
        return "?"


def parse_ranges(text: str) -> list[tuple[int, int]]:
    out = []
    for part in text.split(","):
        a, _, b = part.partition("-")
        out.append((int(a), int(b or a)))
    return out


def is_comment_or_blank(line: str, suffix: str) -> bool:
    s = line.strip()
    if suffix == ".patch":
        s = s[1:].strip() if s[:1] in "+- " else s
    if not s:
        return True
    if suffix in (".py", ".sh"):
        return s.startswith("#")
    return s.startswith("//") or s.startswith("/*") or s.startswith("*")


def render_code(path: str, ranges: list[tuple[int, int]], title: str, notes: dict[tuple[int, int], list[str]],
                warn: list[str]) -> str:
    p = REPO / path
    lines = p.read_text(encoding="utf-8").splitlines()
    suffix = p.suffix
    shown: list[int] = []
    body = []
    for k, (a, b) in enumerate(ranges):
        if b > len(lines):
            warn.append(f"{path}: 範囲 {a}-{b} がファイルの行数 {len(lines)} を超える")
            b = len(lines)
        if k > 0:
            body.append("   ⋮")
        for n in range(a, b + 1):
            text = lines[n - 1]
            if suffix == ".patch" and text[:1] == "+":
                text = text[1:]
            body.append(f"{n:>4}  {text}")
            shown.append(n)
    covered = set()
    for (a, b) in notes:
        for n in range(a, b + 1):
            if n not in shown:
                warn.append(f"{path}: 解説の行 {a}-{b} が引用の範囲 {ranges} の外")
                break
            covered.add(n)
    for n in shown:
        if n not in covered and not is_comment_or_blank(lines[n - 1], suffix):
            warn.append(f"{path}:{n}: 解説がない行: {lines[n - 1].strip()[:70]}")
    rng = ", ".join(f"L{a}" if a == b else f"L{a}–{b}" for a, b in ranges)
    out = [f"#### {title}", "", f"`{path}` {rng}", "", f"```{LANG.get(suffix, '')}", *body, "```", ""]
    for (a, b), texts in sorted(notes.items()):
        label = f"L{a}" if a == b else f"L{a}–{b}"
        for t in texts:
            out.append(f"- **{label}** {t}")
    out.append("")
    return "\n".join(out)


def first_doc_line(p: Path) -> str:
    t = p.read_text(errors="replace")
    if p.suffix == ".py":
        try:
            d = ast.get_docstring(ast.parse(t))
        except Exception:
            d = None
        if d:
            for ln in d.splitlines():
                if ln.strip():
                    return ln.strip()
        for ln in t.splitlines():
            s = ln.strip()
            if s.startswith("#") and not s.startswith("#!") and len(s) > 3:
                return s.lstrip("# ").strip()
        return ""
    for ln in t.splitlines()[:15]:
        s = ln.strip()
        if s.startswith("#") and not s.startswith("#!") and "set -" not in s and len(s) > 3:
            return s.lstrip("# ").strip()
    return ""


def load_overrides() -> dict[str, str]:
    p = SPEC_DIR / "inventory_override.txt"
    out = {}
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip() and not ln.startswith("%%"):
                k, _, v = ln.partition("\t")
                out[k.strip()] = v.strip()
    return out


def render_inventory(dirs: list[str], warn: list[str]) -> str:
    tracked = subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True).split()
    ov = load_overrides()
    out = []
    for d in dirs:
        files = sorted(f for f in tracked if f.startswith(d + "/") and f.endswith((".py", ".sh", ".patch"))
                       and "archive_v1_v15" not in f and "/_work/" not in f and not f.endswith("__init__.py"))
        out += [f"### {d}/（{len(files)} 本）", "", "| ファイル | 行数 | 何をするか |", "|---|---|---|"]
        for f in files:
            n = sum(1 for _ in open(REPO / f, errors="replace"))
            s = ov.get(f) or first_doc_line(REPO / f)
            s = re.sub(r"\s+", " ", s.replace("|", "／").replace("`", ""))
            if len(s) > 120:
                s = s[:118] + "…"
            out.append(f"| `{f}` | {n} | {s} |")
        out.append("")
    return "\n".join(out)


def build(spec: Path, warn: list[str], head: str) -> str:
    out: list[str] = []
    cur = None          # (path, ranges, title, notes)
    for raw in spec.read_text(encoding="utf-8").splitlines():
        if raw.startswith("%%"):
            continue
        m = re.match(r"^@code\s+(\S+)\s+(\S+)\s+(.*)$", raw)
        if m:
            if cur:
                out.append(render_code(*cur, warn))
            cur = (m.group(1), parse_ranges(m.group(2)), m.group(3).strip(), {})
            continue
        if raw.strip() == "@end":
            if cur:
                out.append(render_code(*cur, warn))
                cur = None
            continue
        m = re.match(r"^@inventory\s+(.*)$", raw)
        if m:
            out.append(render_inventory(m.group(1).split(), warn))
            continue
        if cur:
            m = re.match(r"^(\d+)(?:-(\d+))?:\s*(.*)$", raw)
            if m:
                a = int(m.group(1))
                b = int(m.group(2) or a)
                cur[3].setdefault((a, b), []).append(m.group(3))
                continue
            if raw.strip() == "":
                continue
            warn.append(f"{spec.name}: @code の中の読めない行: {raw[:60]}")
            continue
        out.append(raw.replace("{HEAD}", head))
    if cur:
        out.append(render_code(*cur, warn))
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    head = git_head()
    warn: list[str] = []
    for spec in sorted(SPEC_DIR.glob("*.txt")):
        if spec.name == "inventory_override.txt":
            continue
        md = build(spec, warn, head)
        (OUT_DIR / (spec.stem + ".md")).write_text(md, encoding="utf-8")
        print(f"[ok  ] {spec.stem}.md（{md.count(chr(10))} 行）")
    for w in warn:
        print(f"[warn] {w}")
    print(f"[info] 警告 {len(warn)} 件")
    return 1 if (a.strict and warn) else 0


if __name__ == "__main__":
    sys.exit(main())
