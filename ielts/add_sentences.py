#!/usr/bin/env python3
"""向 10 个 ielts_partX.html 的单词卡片注入「例句 + 显示按钮」。可重复运行（幂等）。"""
import json
import re
from pathlib import Path

DIR = Path(__file__).parent
CHUNK = 300
FILES = [f"ielts_part{n}{s}.html" for n in range(1, 6) for s in "ab"]

SENT_CSS = """<!--SENT-CSS--><style>
  .sent-row { margin: 10px 16px 2px; }
  .sent-btn { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 999px; padding: 5px 14px; font-size: 12px; cursor: pointer; font-family: inherit; transition: all .15s; }
  .sent-btn:hover { background: #dbeafe; }
  .sent-box { margin-top: 8px; background: #f0f7ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 10px 14px; }
  .sent-en { font-size: 14px; color: #0f172a; line-height: 1.6; margin: 0; font-weight: 500; }
  .sent-cn { font-size: 13px; color: #64748b; margin: 4px 0 0; }
  .sent-cn .voice-btn { margin-left: 6px; }
</style><!--/SENT-CSS-->"""

SENT_JS = """<!--SENT-JS--><script>
  function toggleSent(n) {
    var box = document.getElementById('sent-box-' + n);
    var btn = document.getElementById('sent-btn-' + n);
    if (!box) return;
    if (box.style.display === 'none') {
      box.style.display = 'block';
      if (btn) btn.textContent = '📝 收起例句';
    } else {
      box.style.display = 'none';
      if (btn) btn.textContent = '📝 例句';
    }
  }
</script><!--/SENT-JS-->"""


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def js_quote(text: str) -> str:
    return esc(text).replace("'", "\\'")


def main() -> None:
    # 加载全部例句
    sentences = {}
    for i in range(1, 11):
        path = DIR / "sentences" / f"sent_{i:02d}.json"
        for item in json.loads(path.read_text(encoding="utf-8")):
            sentences[item["id"]] = (item["s"].strip(), item["c"].strip())
    print(f"例句总数: {len(sentences)}")
    assert len(sentences) == 3000, "例句不足 3000 条"

    for idx, name in enumerate(FILES):
        path = DIR / name
        content = path.read_text(encoding="utf-8")

        # 幂等：清除上次注入
        content = re.sub(r"<!--SENT-->.*?<!--/SENT-->\n?", "", content, flags=re.S)
        content = re.sub(r"<!--SENT-CSS-->.*?<!--/SENT-CSS-->\n?", "", content, flags=re.S)
        content = re.sub(r"<!--SENT-JS-->.*?<!--/SENT-JS-->\n?", "", content, flags=re.S)
        content = re.sub(r"sent-row\">.*?</div></div><!--/SENT-->", "", content)  # 兜底

        # 切分卡片
        parts = re.split(r'(?=<div class="word-card")', content)
        missing = []
        for j in range(len(parts)):
            m = re.search(r'<div class="word-card" id="card-(\d+)"', parts[j])
            if not m:
                continue
            # 最后一段可能包含最后一张卡片 + 表格视图及之后内容，先分离出卡片部分
            k = -1
            if j == len(parts) - 1:
                k = parts[j].find('<div class="table-container"')
                if k != -1:
                    tail = parts[j][k:]
                    parts[j] = parts[j][:k]
            wid = int(m.group(1))
            if wid not in sentences:
                missing.append(wid)
                continue
            s, c = sentences[wid]
            block = (
                f'<!--SENT--><div class="sent-row">'
                f'<button class="sent-btn" id="sent-btn-{wid}" onclick="toggleSent({wid})">📝 例句</button>'
                f'<div class="sent-box" id="sent-box-{wid}" style="display:none">'
                f'<p class="sent-en">{esc(s)}</p>'
                f'<p class="sent-cn">{esc(c)}'
                f'<button class="voice-btn" onclick="speak(\'{js_quote(s)}\')">🔊</button></p>'
                f'</div></div><!--/SENT-->'
            )
            part = parts[j]
            # 插到卡片内部：card-body 关闭之前（即 meaning-box 关闭之后）
            end = part.rfind('</div>\n          </div>\n        </div>')
            if end == -1:
                missing.append(wid)
                continue
            insert_at = end + len('</div>')
            parts[j] = part[:insert_at] + "\n            " + block + part[insert_at:]
            if j == len(parts) - 1 and k != -1:
                parts[j] += "\n        " + tail
        content = "".join(parts)

        # 注入 CSS 与 JS
        content = content.replace("</head>", SENT_CSS + "\n</head>")
        content = content.replace("</body>", SENT_JS + "\n</body>")
        path.write_text(content, encoding="utf-8")

        got = len(re.findall("<!--SENT-->", content))
        print(f"{name}: 注入 {got} 条例句" + (f"，缺失 id: {missing}" if missing else " ✓"))

    print("全部完成")


if __name__ == "__main__":
    main()
