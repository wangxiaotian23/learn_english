"""Fix bottom-nav links after splitting ielts_part1-5.html into a/b halves."""
import re
from pathlib import Path

PARTS = {
    1: ("学术与逻辑", 1, 600),
    2: ("教育与生态", 601, 1200),
    3: ("科技与社会", 1201, 1800),
    4: ("经管与法律", 1801, 2400),
    5: ("医艺与高分", 2401, 3000),
}

def label(num, half):
    lo = PARTS[num][1] + (0 if half == "a" else 300)
    hi = PARTS[num][1] + 299 if half == "a" else PARTS[num][2]
    return f"Part {num}{half} ({lo:04d}-{hi:04d})"

def nav_line(num, half):
    prev = f'<a href="ielts_part{num-1}b.html" class="btn-bottom">← 返回 {label(num-1, "b")}</a>' if half == "a" and num > 1 else \
           f'<a href="ielts_part{num}a.html" class="btn-bottom">← 返回 {label(num, "a")}</a>' if half == "b" else None
    nxt = f'<a href="ielts_part{num}b.html" class="btn-bottom">前往 {label(num, "b")} →</a>' if half == "a" else \
          f'<a href="ielts_part{num+1}a.html" class="btn-bottom">前往 {label(num+1, "a")} →</a>' if num < 5 else None
    links = [prev, '<a href="#top" class="btn-bottom btn-top">↑ 返回顶部</a>', nxt, '<a href="../index.html" class="btn-bottom">← 返回目录</a>']
    return "    " + "".join(l for l in links if l)

for num in PARTS:
    for half in "ab":
        p = Path(f"ielts_part{num}{half}.html")
        text = p.read_text(encoding="utf-8")
        new_line = nav_line(num, half)
        text, n = re.subn(r'^    <a [^>]*btn-bottom btn-top[^>]*>.*$', new_line, text, count=1, flags=re.M)
        print(p, "->", "OK" if n else "NOT FOUND")
        p.write_text(text, encoding="utf-8")
