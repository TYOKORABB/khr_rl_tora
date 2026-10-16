"""Markdown の表（| で区切る GitHub の表）を、文字幅をそろえた等幅テキストの表（```text のコードブロック）に直す（2026-10-16）。

ユーザーの希望: 表は GitHub で表として表示されなくてよいので、テキストのまま見やすくする（getup/DIARY.md から）。
全角（East Asian Width が W・F）は 2 桁、結合文字は 0 桁、ほかは 1 桁として数える。長いセルは --max 桁で折り返す
（切る位置は句読点・式の「 · 」・括弧・空白を優先し、閉じ括弧・句読点・中黒を行頭に置かない）。セルの ** と ` と ~~ は外す。
ファイルを上書きする。コードブロックの中の表は触らない。

  python docs/tools/md_tables_to_text.py getup/DIARY.md --max 46
"""
import re
import sys
import unicodedata

MAXW = 48


def w(ch):
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def dw(s):
    return sum(w(c) for c in s)


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, i = [], "", 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if s[i] == "|":
            cells.append(cur)
            cur = ""
        else:
            cur += s[i]
        i += 1
    cells.append(cur)
    return [clean(c) for c in cells]


def clean(c):
    c = c.strip().replace("**", "").replace("`", "").replace("~~", "")
    return re.sub(r"\s+", " ", c)


def wrap(text, width):
    """表示幅 width で折り返す。切る位置の優先: ①句読点・「 · 」（式の区切り）の後 ②閉じ括弧・」・中黒の後、開き括弧（全角）・「の前
    ③空白（数字の直後を除く）。どれも無ければその文字で切る。"""
    if dw(text) <= width:
        return [text]
    lines, cur = [], ""
    for ch in text:
        if dw(cur + ch) <= width or (ch in "）」。、，)" and cur):   # 閉じ括弧・句読点は行頭に置かない（少しはみ出す）
            cur += ch
            continue
        best = None
        for pri, test in ((1, lambda k: cur[k - 1] in "、。，；" or cur[max(0, k - 2):k] == "· "),
                          (2, lambda k: cur[k - 1] in "）」・：" or cur[k] in "（「"),
                          (3, lambda k: cur[k] == " " and not cur[k - 1].isdigit())):
            ks = [k for k in range(1, len(cur)) if test(k) and cur[k] not in "）」。、，)・" and dw(cur[:k]) >= width * 0.45]
            if ks:
                best = ks[-1]
                break
        if best is not None:
            lines.append(cur[:best].rstrip())
            cur = cur[best:].lstrip() + ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def render(rows, maxw):
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    body = rows[1:] or rows
    content = [max(dw(r[j]) for r in body) for j in range(n)]
    head = [dw(rows[0][j]) for j in range(n)]
    # 見出しが中身より長い列は、見出しを折り返して中身の幅（最低 12 桁）に合わせる
    widths = [min(maxw, max(content[j], min(head[j], max(12, content[j])))) for j in range(n)]
    wrapped = [[wrap(c, widths[j]) for j, c in enumerate(r)] for r in rows]
    widths = [max(max(dw(x) for x in cell) for cell in col) for col in zip(*wrapped)]
    n_multi = sum(max(len(c) for c in r) > 1 for r in wrapped[1:])
    multi = n_multi * 3 > max(1, len(wrapped) - 1)      # 折り返しの行が多いときだけ、行の間を 1 行あける
    out = []
    for k, r in enumerate(wrapped):
        h = max(len(c) for c in r)
        for i in range(h):
            parts = []
            for j, cell in enumerate(r):
                s = cell[i] if i < len(cell) else ""
                parts.append(s + " " * (widths[j] - dw(s)))
            out.append("  ".join(parts).rstrip())
        if k == 0:
            out.append("  ".join("-" * widths[j] for j in range(n)))
        elif multi and k < len(wrapped) - 1:
            out.append("")
    return out


def convert(text, maxw):
    lines = text.split("\n")
    out, i, n_tab = [], 0, 0
    in_code = False
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            in_code = not in_code
            out.append(ln)
            i += 1
            continue
        if (not in_code and ln.startswith("|") and i + 1 < len(lines)
                and re.match(r"^\|\s*:?-{2,}", lines[i + 1])):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            rows = [split_row(b) for b in block if not re.match(r"^\|(\s*:?-+:?\s*\|)+\s*$", b)]
            out.append("```text")
            out.extend(render(rows, maxw))
            out.append("```")
            n_tab += 1
            continue
        out.append(ln)
        i += 1
    return "\n".join(out), n_tab


if __name__ == "__main__":
    path = sys.argv[1]
    maxw = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else MAXW
    src = open(path, encoding="utf-8").read()
    dst, n = convert(src, maxw)
    open(path, "w", encoding="utf-8").write(dst)
    print(f"{path}: 表 {n} 個をテキストの表に直した")
