#!/usr/bin/env python3
"""把 ielts_part1~5.html（各 600 词）拆分为 a/b 两份各 300 词的 HTML。"""
import re
import sys
from pathlib import Path

DIR = Path(__file__).parent
CHUNK = 300

NAV_ITEMS = [
    ("ielts_part1a.html", "Part 1a", 1, 300),
    ("ielts_part1b.html", "Part 1b", 301, 600),
    ("ielts_part2a.html", "Part 2a", 601, 900),
    ("ielts_part2b.html", "Part 2b", 901, 1200),
    ("ielts_part3a.html", "Part 3a", 1201, 1500),
    ("ielts_part3b.html", "Part 3b", 1501, 1800),
    ("ielts_part4a.html", "Part 4a", 1801, 2100),
    ("ielts_part4b.html", "Part 4b", 2101, 2400),
    ("ielts_part5a.html", "Part 5a", 2401, 2700),
    ("ielts_part5b.html", "Part 5b", 2701, 3000),
]


def build_nav(active_href: str) -> str:
    links = ['<a href="../index.html">← 英语主页</a>']
    for href, label, start, end in NAV_ITEMS:
        cls = ' class="active"' if href == active_href else ""
        links.append(f'<a href="{href}"{cls}>{label} ({start:04d} - {end:04d})</a>')
    return '<nav class="nav-tabs">\n      ' + "".join(links) + "\n    </nav>"


def split_blocks(segment: str, marker: str, expect: int) -> list[str]:
    """按块起始标记切分，返回 expect 个块（保留块内缩进与前导空白语义）。"""
    starts = [m.start() for m in re.finditer(re.escape(marker), segment)]
    if len(starts) != expect:
        raise SystemExit(f"预期 {expect} 个 {marker!r} 块，实际 {len(starts)} 个")
    blocks = [segment[s:e] for s, e in zip(starts, starts[1:] + [len(segment)])]
    return blocks


def fix_head(head: str, part_label: str, theme: str, start: int, end: int,
             first_word: str, last_word: str, active_href: str) -> str:
    rng = f"({start:04d} - {end:04d})"
    head = re.sub(r"<title>[^<]*</title>",
                  f"<title>{part_label}: {theme} {rng} · 雅思3000核心词汇</title>", head)
    head = re.sub(r"<h1>[^<]*</h1>", f"<h1>{part_label}: {theme} {rng}</h1>", head)
    span = f"{first_word[0].upper()} ~ {last_word[0].upper()} 字母段"
    if first_word[0].upper() == last_word[0].upper():
        span = f"{first_word[0].upper()} 字母段"
    head = re.sub(r"<p>([^<]*?)（[A-Za-z] ~ [A-Za-z] 字母段）</p>",
                  f"<p>\\1（{span}）</p>", head)
    head = head.replace("0 / 600", f"0 / {CHUNK}")
    head = re.sub(r'<nav class="nav-tabs">.*?</nav>', build_nav(active_href), head, flags=re.S)
    return head


def main() -> None:
    for no in range(1, 6):
        src = DIR / f"ielts_part{no}.html"
        content = src.read_text(encoding="utf-8")

        i_card = content.index('<div class="word-card"')
        i_table = content.index('<div class="table-container"')
        i_tbody = content.index('<tbody id="tableBody">')
        i_tbody_end = content.index("</tbody>")

        head = content[:i_card]
        cards = split_blocks(content[i_card:i_table], '<div class="word-card"', 600)
        table_open = content[i_table:i_tbody + len('<tbody id="tableBody">')]
        rows = split_blocks(content[i_tbody + len('<tbody id="tableBody">'):i_tbody_end],
                            '<tr class="word-row"', 600)
        footer = content[i_tbody_end:]

        m = re.search(r'<h1>(Part \d+): ([^(]+)\(', head)
        if not m:
            raise SystemExit(f"{src.name}: 未找到 h1 标题")
        base_label, theme = m.group(1), m.group(2).strip()
        offset = int(re.search(r'data-id="(\d+)"', cards[0]).group(1)) - 1
        print(f"{src.name}: 主题={theme!r} 起始编号={offset + 1}")

        for half, suffix in enumerate("ab"):
            lo, hi = half * CHUNK, (half + 1) * CHUNK
            part_cards, part_rows = cards[lo:hi], rows[lo:hi]
            first_word = re.search(r'data-w="([^"]+)"', part_cards[0]).group(1)
            last_word = re.search(r'data-w="([^"]+)"', part_cards[-1]).group(1)
            start, end = offset + lo + 1, offset + hi
            href = f"ielts_part{no}{suffix}.html"
            out = (fix_head(head, f"Part {no}{suffix}", theme, start, end,
                            first_word, last_word, href)
                   + "".join(part_cards) + table_open
                   + "".join(part_rows) + footer)
            (DIR / href).write_text(out, encoding="utf-8")

            # 自检
            got_cards = len(re.findall('<div class="word-card"', out))
            got_rows = len(re.findall('<tr class="word-row"', out))
            ids = [int(x) for x in re.findall(r'<div class="word-card" id="card-(\d+)"', out)]
            assert got_cards == CHUNK and got_rows == CHUNK, f"{href}: 数量不符"
            assert ids == list(range(start, end + 1)), f"{href}: 编号不连续"
            w1 = re.search(r'data-w="([^"]+)"', part_cards[0]).group(1)
            w2 = re.search(r'data-w="([^"]+)"', part_cards[-1]).group(1)
            print(f"  -> {href}: {CHUNK} 卡 / {CHUNK} 行, 词号 {start}~{end} ({w1} → {w2}) ✓")

    print("全部拆分完成并通过自检")


if __name__ == "__main__":
    main()
