import os
import re
import html
import json

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
VOCAB_FILE = os.path.join(WORKSPACE, "vocab_3000.json")

# Load the 3000 words database
with open(VOCAB_FILE, "r", encoding="utf-8") as f:
    vocab_db = json.load(f)

all_words = [(item["word"], item["meaning"]) for item in vocab_db]
print(f"Total vocabulary words loaded: {len(all_words)}")
assert len(all_words) == 3000, f"Expected 3000 words, got {len(all_words)}"

# Function to parse POS, Band, Tag
def classify_word(idx, word, meaning_str):
    # Extract POS
    pos_match = re.match(r"^([a-z\./\s]+)\.\s*(.*)$", meaning_str)
    if pos_match:
        pos = pos_match.group(1).strip() + "."
        meaning = pos_match.group(2).strip()
    else:
        pos = "n."
        meaning = meaning_str

    # Categorize Scene Tag
    m_lower = meaning.lower()
    if any(k in m_lower for k in ["学术", "论证", "分析", "理论", "推导", "方法", "研究", "定义"]):
        tag = "学术词汇"
    elif any(k in m_lower for k in ["导致", "促进", "阻碍", "显著", "观点", "主张", "表明", "相反", "此外", "因此"]):
        tag = "写作高分"
    elif any(k in m_lower for k in ["生态", "环境", "地质", "历史", "文明", "心理", "科学", "物种", "化石", "演变"]):
        tag = "阅读核心"
    elif any(k in m_lower for k in ["住宿", "租房", "机场", "预约", "校园", "设施", "活动", "旅游", "表格"]):
        tag = "听力高频"
    else:
        tag = "口语常用"

    # Assign Band
    length = len(word)
    if length <= 5:
        band = "6.0"
    elif length <= 7:
        band = "6.5"
    elif length <= 9:
        band = "7.0"
    elif length <= 11:
        band = "7.5"
    else:
        band = "8.0+"

    return pos, meaning, tag, band

# Build 5 parts (600 words each)
PARTS_INFO = [
    {
        "filename": "ielts_part1.html",
        "title": "Part 1: 学术研究与逻辑论证核心词 (0001 - 0600)",
        "subtitle": "涵盖 AWL 学术词汇、论证逻辑、实验方法与基础考点词汇（A ~ C 字母段）",
        "range_text": "0001 - 0600",
        "start": 0,
        "end": 600,
        "prev": None,
        "next": ("ielts_part2.html", "前往 Part 2: 教育与生态 (0601-1200) →")
    },
    {
        "filename": "ielts_part2.html",
        "title": "Part 2: 教育学习与自然地理生态 (0601 - 1200)",
        "subtitle": "涵盖大学校园、教学科研、考核评估、气候地理与生态环保高频场景（C ~ E 字母段）",
        "range_text": "0601 - 1200",
        "start": 600,
        "end": 1200,
        "prev": ("ielts_part1.html", "← 返回 Part 1: 学术与逻辑 (0001-0600)"),
        "next": ("ielts_part3.html", "前往 Part 3: 科技与社会 (1201-1800) →")
    },
    {
        "filename": "ielts_part3.html",
        "title": "Part 3: 科技工程、建筑与社会文化 (1201 - 1800)",
        "subtitle": "涵盖信息科技、人工智能、工程制造、建筑空间与多元文化习俗（E ~ I 字母段）",
        "range_text": "1201 - 1800",
        "start": 1200,
        "end": 1800,
        "prev": ("ielts_part2.html", "← 返回 Part 2: 教育与生态 (0601-1200)"),
        "next": ("ielts_part4.html", "前往 Part 4: 经管与法律 (1801-2400) →")
    },
    {
        "filename": "ielts_part4.html",
        "title": "Part 4: 经济商业、职业发展与政府法律 (1801 - 2400)",
        "subtitle": "聚焦宏观经济、国际贸易、企业管理、求职招聘与法律政策（I ~ P 字母段）",
        "range_text": "1801 - 2400",
        "start": 1800,
        "end": 2400,
        "prev": ("ielts_part3.html", "← 返回 Part 3: 科技与社会 (1201-1800)"),
        "next": ("ielts_part5.html", "前往 Part 5: 医艺与高分 (2401-3000) →")
    },
    {
        "filename": "ielts_part5.html",
        "title": "Part 5: 医药健康、艺术传媒与真题核心替换 (2401 - 3000)",
        "subtitle": "精选生理心理、大众传媒、艺术审美以及写作高分替换与阅读同义词（P ~ Z 字母段）",
        "range_text": "2401 - 3000",
        "start": 2400,
        "end": 3000,
        "prev": ("ielts_part4.html", "← 返回 Part 4: 经管与法律 (1801-2400)"),
        "next": None
    }
]

# Generate each HTML file
for p_idx, part in enumerate(PARTS_INFO):
    slice_words = all_words[part["start"]:part["end"]]
    part_id = f"part{p_idx + 1}"

    # Generate Cards and Rows HTML
    cards_html = []
    rows_html = []

    for i, (word, meaning_str) in enumerate(slice_words):
        global_id = part["start"] + i + 1
        pos, meaning, tag, band = classify_word(global_id, word, meaning_str)

        card_snippet = f"""
        <div class="word-card" id="card-{global_id}" data-id="{global_id}" data-w="{html.escape(word)}" data-m="{html.escape(meaning)}" data-b="{band}" data-t="{tag}">
          <div class="card-head">
            <div class="word-badge-row">
              <span class="w-id">#{global_id:04d}</span>
              <span class="badge pos">{html.escape(pos)}</span>
              <span class="badge band">Band {band}</span>
              <span class="badge tag">{tag}</span>
            </div>
            <label class="chk-wrap" title="标记已掌握">
              <input type="checkbox" class="chk-card" onchange="toggleMaster({global_id})">
              <span class="chk-custom"></span>
            </label>
          </div>
          <div class="card-body">
            <div class="word-voice-row">
              <div class="word-title-group">
                <h3 class="word-title">{html.escape(word)}</h3>
                <button class="voice-btn" onclick="speak('{html.escape(word)}')" title="点击朗读">🔊</button>
                <label class="reveal-ctrl" id="lbl-card-{global_id}" title="点击单选框显示/隐藏此单词释义">
                  <input type="checkbox" class="chk-reveal" id="reveal-card-{global_id}" onchange="toggleWordReveal({global_id}, this.checked)">
                  <span class="reveal-radio-circle"></span>
                  <span class="reveal-txt">显示释义</span>
                </label>
              </div>
            </div>
            <div class="meaning-box" id="meaning-card-{global_id}" onclick="clickMeaningBox({global_id})">
              <span class="cn-text">{html.escape(meaning)}</span>
              <span class="quiz-tip">（已遮盖 · 点击左侧单选框显示）</span>
            </div>
          </div>
        </div>
        """
        cards_html.append(card_snippet)

        row_snippet = f"""
        <tr class="word-row" id="row-{global_id}" data-id="{global_id}" data-w="{html.escape(word)}" data-m="{html.escape(meaning)}" data-b="{band}" data-t="{tag}">
          <td class="col-chk">
            <input type="checkbox" class="chk-table" onchange="toggleMaster({global_id})" title="标记已掌握">
          </td>
          <td class="col-num">#{global_id:04d}</td>
          <td class="col-word">
            <div class="table-word-cell">
              <strong>{html.escape(word)}</strong>
              <button class="voice-btn-sm" onclick="speak('{html.escape(word)}')" title="点击朗读">🔊</button>
              <label class="reveal-ctrl-sm" id="lbl-row-{global_id}" title="点击单选框显示此单词释义">
                <input type="checkbox" class="chk-reveal-tbl" id="reveal-row-{global_id}" onchange="toggleWordReveal({global_id}, this.checked)">
                <span class="reveal-radio-circle-sm"></span>
                <span class="reveal-txt-sm">显示释义</span>
              </label>
            </div>
          </td>
          <td class="col-pos"><span class="badge pos">{html.escape(pos)}</span></td>
          <td class="col-meaning" id="meaning-row-{global_id}" onclick="clickMeaningBox({global_id})">
            <span class="cn-text">{html.escape(meaning)}</span>
            <span class="quiz-tip">（已遮盖 · 点击左侧单选框显示）</span>
          </td>
          <td class="col-band"><span class="badge band">Band {band}</span></td>
          <td class="col-tag"><span class="badge tag">{tag}</span></td>
        </tr>
        """
        rows_html.append(row_snippet)

    # Nav links
    nav_links_html = []
    nav_links_html.append('<a href="../index.html">← 英语主页</a>')
    for idx_tab, ptab in enumerate(PARTS_INFO):
        is_cur = "active" if idx_tab == p_idx else ""
        nav_links_html.append(f'<a href="{ptab["filename"]}" class="{is_cur}">Part {idx_tab + 1} ({ptab["range_text"]})</a>')

    # Bottom links
    bottom_links = []
    if part["prev"]:
        bottom_links.append(f'<a href="{part["prev"][0]}" class="btn-bottom">{part["prev"][1]}</a>')
    bottom_links.append('<a href="#top" class="btn-bottom btn-top">↑ 返回顶部</a>')
    if part["next"]:
        bottom_links.append(f'<a href="{part["next"][0]}" class="btn-bottom">{part["next"][1]}</a>')

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{part["title"]} · 雅思3000核心词汇</title>
<style>
  :root {{
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --primary-light: #eff6ff;
    --accent: #f59e0b;
    --success: #10b981;
    --bg: #f8fafc;
    --card: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --border: #e2e8f0;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding-bottom: 80px;
  }}
  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px 16px;
  }}
  /* Header */
  header.hero {{
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #3b82f6 100%);
    color: #fff;
    border-radius: 16px;
    padding: 28px 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(37,99,235,0.25);
  }}
  .nav-tabs {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
  }}
  .nav-tabs a {{
    text-decoration: none;
    color: #fff;
    font-size: 13px;
    font-weight: 500;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.18);
    backdrop-filter: blur(4px);
    transition: all 0.2s;
  }}
  .nav-tabs a:hover {{
    background: rgba(255,255,255,0.3);
    transform: translateY(-1px);
  }}
  .nav-tabs a.active {{
    background: #ffffff;
    color: #1e3a8a;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }}
  .hero-body {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 16px;
  }}
  .hero h1 {{
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 6px;
  }}
  .hero p {{
    font-size: 14px;
    opacity: 0.92;
    max-width: 720px;
  }}
  .progress-box {{
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 12px;
    padding: 12px 18px;
    min-width: 220px;
    backdrop-filter: blur(6px);
  }}
  .progress-head {{
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 6px;
  }}
  .progress-bar-bg {{
    height: 8px;
    background: rgba(0,0,0,0.2);
    border-radius: 999px;
    overflow: hidden;
  }}
  .progress-bar-fill {{
    height: 100%;
    width: 0%;
    background: #10b981;
    border-radius: 999px;
    transition: width 0.3s ease;
  }}
  .progress-actions {{
    display: flex;
    gap: 10px;
    margin-top: 8px;
  }}
  .progress-actions button {{
    background: none;
    border: none;
    color: rgba(255,255,255,0.85);
    font-size: 11px;
    text-decoration: underline;
    cursor: pointer;
  }}
  .progress-actions button:hover {{
    color: #fff;
  }}

  /* Controls Panel */
  .control-panel {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    position: sticky;
    top: 10px;
    z-index: 100;
    backdrop-filter: blur(8px);
  }}
  .search-row {{
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }}
  .search-box {{
    flex: 1;
    min-width: 260px;
    position: relative;
  }}
  .search-box input {{
    width: 100%;
    padding: 10px 14px 10px 38px;
    border: 1px solid var(--border);
    border-radius: 10px;
    font-size: 14px;
    outline: none;
    transition: border 0.2s, box-shadow 0.2s;
  }}
  .search-box input:focus {{
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
  }}
  .search-icon {{
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 15px;
    color: var(--muted);
  }}
  .mode-switch {{
    display: flex;
    background: #f1f5f9;
    border-radius: 8px;
    padding: 2px;
    gap: 2px;
  }}
  .mode-switch button {{
    border: none;
    background: transparent;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.15s;
  }}
  .mode-switch button.active {{
    background: #fff;
    color: var(--primary);
    font-weight: 600;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }}
  .filter-row {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    font-size: 13px;
  }}
  .filter-group {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }}
  .filter-label {{
    color: var(--muted);
    font-weight: 600;
    font-size: 12px;
  }}
  .chip {{
    border: 1px solid var(--border);
    background: #fff;
    padding: 4px 10px;
    border-radius: 999px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.15s;
    user-select: none;
  }}
  .chip:hover {{
    background: #f8fafc;
    border-color: #cbd5e1;
  }}
  .chip.active {{
    background: var(--primary);
    border-color: var(--primary);
    color: #fff;
    font-weight: 600;
  }}

  /* Word Grid View */
  .words-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 16px;
  }}
  .word-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
    transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .word-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.04);
    border-color: #cbd5e1;
  }}
  .word-card.mastered {{
    background: #f0fdf4;
    border-color: #86efac;
  }}
  .card-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }}
  .word-badge-row {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }}
  .w-id {{
    font-size: 11px;
    font-family: monospace;
    color: var(--muted);
    font-weight: 600;
  }}
  .badge {{
    font-size: 11px;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 600;
  }}
  .badge.pos {{
    background: #e0f2fe;
    color: #0369a1;
  }}
  .badge.band {{
    background: #fef3c7;
    color: #b45309;
  }}
  .badge.tag {{
    background: #f1f5f9;
    color: #475569;
  }}
  .chk-wrap {{
    position: relative;
    cursor: pointer;
    display: flex;
    align-items: center;
  }}
  .chk-card, .chk-table {{
    cursor: pointer;
    width: 17px;
    height: 17px;
    accent-color: #10b981;
  }}
  .word-voice-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .word-title-group {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .word-title {{
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.2px;
  }}
  .voice-btn, .voice-btn-sm {{
    background: #f1f5f9;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    padding: 4px 8px;
    font-size: 14px;
    transition: background 0.15s, transform 0.1s;
  }}
  .voice-btn:hover, .voice-btn-sm:hover {{
    background: #e2e8f0;
    transform: scale(1.05);
  }}
  .voice-btn:active, .voice-btn-sm:active {{
    transform: scale(0.95);
  }}

  /* Reveal Radio Button next to word */
  .reveal-ctrl {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #f1f5f9;
    border: 1px solid var(--border);
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    color: var(--muted);
    cursor: pointer;
    user-select: none;
    transition: all 0.15s ease;
  }}
  .reveal-ctrl:hover {{
    background: #e2e8f0;
    color: var(--text);
  }}
  .reveal-ctrl.active {{
    background: #eff6ff;
    border-color: #93c5fd;
    color: var(--primary);
    font-weight: 600;
  }}
  .reveal-radio-circle {{
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid #94a3b8;
    border-radius: 50%;
    position: relative;
    background: #fff;
    transition: all 0.15s;
    flex-shrink: 0;
  }}
  .chk-reveal {{
    display: none;
  }}
  .chk-reveal:checked + .reveal-radio-circle {{
    border-color: var(--primary);
    background: var(--primary);
    box-shadow: inset 0 0 0 2.5px #fff;
  }}
  .reveal-ctrl-sm {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #f1f5f9;
    border: 1px solid var(--border);
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 11px;
    color: var(--muted);
    cursor: pointer;
    margin-left: 6px;
    user-select: none;
    transition: all 0.15s ease;
  }}
  .reveal-ctrl-sm:hover {{
    background: #e2e8f0;
    color: var(--text);
  }}
  .reveal-ctrl-sm.active {{
    background: #eff6ff;
    border-color: #93c5fd;
    color: var(--primary);
    font-weight: 600;
  }}
  .reveal-radio-circle-sm {{
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid #94a3b8;
    border-radius: 50%;
    position: relative;
    background: #fff;
    transition: all 0.15s;
    flex-shrink: 0;
  }}
  .chk-reveal-tbl {{
    display: none;
  }}
  .chk-reveal-tbl:checked + .reveal-radio-circle-sm {{
    border-color: var(--primary);
    background: var(--primary);
    box-shadow: inset 0 0 0 2px #fff;
  }}

  .meaning-box {{
    background: #f8fafc;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    color: #334155;
    margin-top: 6px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.15s;
  }}
  .meaning-box:hover {{
    border-color: #cbd5e1;
  }}
  .quiz-tip {{
    display: none;
    color: #94a3b8;
    font-size: 12px;
    font-style: italic;
  }}

  /* Word-hidden state (when user toggles off reveal) */
  .meaning-box.word-hidden .cn-text,
  td.col-meaning.word-hidden .cn-text {{
    display: none !important;
  }}
  .meaning-box.word-hidden .quiz-tip,
  td.col-meaning.word-hidden .quiz-tip {{
    display: inline-block !important;
  }}

  /* Table View */
  .table-container {{
    display: none;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow-x: auto;
  }}
  table.words-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }}
  table.words-table th, table.words-table td {{
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  table.words-table th {{
    background: #f8fafc;
    color: var(--muted);
    font-weight: 600;
    font-size: 12px;
  }}
  table.words-table tr:hover td {{
    background: #f8fafc;
  }}
  table.words-table tr.mastered td {{
    background: #f0fdf4;
  }}
  .table-word-cell {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }}

  /* Quiz Mode Styles */
  body.quiz-mode .cn-text {{
    display: none;
  }}
  body.quiz-mode .quiz-tip {{
    display: inline-block;
  }}
  body.quiz-mode .meaning-box.revealed .cn-text,
  body.quiz-mode td.col-meaning.revealed .cn-text {{
    display: inline !important;
    color: #1e3a8a;
    font-weight: 600;
  }}
  body.quiz-mode .meaning-box.revealed .quiz-tip,
  body.quiz-mode td.col-meaning.revealed .quiz-tip {{
    display: none !important;
  }}
  body.quiz-mode .meaning-box.revealed {{
    background: #eff6ff;
    border-color: #bfdbfe;
  }}
  body.quiz-mode td.col-meaning.revealed {{
    background: #eff6ff;
  }}

  /* Bottom Nav */
  .bottom-nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 36px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
  }}
  .btn-bottom {{
    text-decoration: none;
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--primary);
    transition: all 0.15s;
  }}
  .btn-bottom:hover {{
    background: var(--primary-light);
    border-color: var(--primary);
  }}
  .btn-top {{
    color: var(--muted);
  }}

  /* Empty state */
  .empty-state {{
    display: none;
    text-align: center;
    padding: 60px 20px;
    color: var(--muted);
  }}
  .empty-state h3 {{
    font-size: 18px;
    margin-bottom: 6px;
    color: var(--text);
  }}
</style>
</head>
<body id="top" class="quiz-mode">

<div class="container">

  <!-- Hero Header -->
  <header class="hero">
    <nav class="nav-tabs">
      {"".join(nav_links_html)}
    </nav>
    <div class="hero-body">
      <div>
        <h1>{part["title"]}</h1>
        <p>{part["subtitle"]}</p>
      </div>
      <div class="progress-box">
        <div class="progress-head">
          <span>掌握进度</span>
          <span id="progCount">0 / 600 (0%)</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" id="progBar"></div>
        </div>
        <div class="progress-actions">
          <button onclick="markAllMastered(true)">全部标记掌握</button>
          <button onclick="markAllMastered(false)">重置进度</button>
        </div>
      </div>
    </div>
  </header>

  <!-- Sticky Controls Panel -->
  <div class="control-panel">
    <div class="search-row">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="filterInput" placeholder="快速搜索英文单词、中文释义..." oninput="doSearch()">
      </div>
      <div class="mode-switch">
        <button id="btnCard" class="active" onclick="switchView('card')">🗂️ 卡片模式</button>
        <button id="btnTable" onclick="switchView('table')">📋 表格模式</button>
        <button id="btnQuiz" class="active" onclick="toggleQuiz()">🧠 刷词自测(遮盖)</button>
      </div>
    </div>
    <div class="filter-row">
      <div class="filter-group" id="bandGroup">
        <span class="filter-label">目标分数:</span>
        <span class="chip active" onclick="setBand('all', this)">全部</span>
        <span class="chip" onclick="setBand('6.0', this)">6.0</span>
        <span class="chip" onclick="setBand('6.5', this)">6.5</span>
        <span class="chip" onclick="setBand('7.0', this)">7.0</span>
        <span class="chip" onclick="setBand('7.5', this)">7.5</span>
        <span class="chip" onclick="setBand('8.0+', this)">8.0+</span>
      </div>
      <div class="filter-group" id="tagGroup">
        <span class="filter-label">场景分类:</span>
        <span class="chip active" onclick="setCat('all', this)">全部</span>
        <span class="chip" onclick="setCat('学术词汇', this)">学术词汇</span>
        <span class="chip" onclick="setCat('写作高分', this)">写作高分</span>
        <span class="chip" onclick="setCat('阅读核心', this)">阅读核心</span>
        <span class="chip" onclick="setCat('听力高频', this)">听力高频</span>
        <span class="chip" onclick="setCat('口语常用', this)">口语常用</span>
      </div>
      <div class="filter-group" id="revealGroup">
        <span class="filter-label">释义显示:</span>
        <span class="chip active" id="chipHide" onclick="batchSetReveal(false)">🙈 默认遮盖</span>
        <span class="chip" id="chipShow" onclick="batchSetReveal(true)">👁️ 全部展开</span>
      </div>
    </div>
  </div>

  <!-- Words Card Grid -->
  <div class="words-grid" id="gridCards">
    {"".join(cards_html)}
  </div>

  <!-- Words Table View -->
  <div class="table-container" id="tableContainer">
    <table class="words-table">
      <thead>
        <tr>
          <th style="width: 40px;">掌握</th>
          <th style="width: 70px;">编号</th>
          <th style="width: 220px;">英文单词</th>
          <th style="width: 90px;">词性</th>
          <th>中文核心释义</th>
          <th style="width: 100px;">目标分数</th>
          <th style="width: 110px;">场景</th>
        </tr>
      </thead>
      <tbody id="tableBody">
        {"".join(rows_html)}
      </tbody>
    </table>
  </div>

  <!-- Empty Search Result -->
  <div class="empty-state" id="emptyBox">
    <h3>未找到匹配单词</h3>
    <p>请尝试其他搜索关键词或重置筛选条件</p>
  </div>

  <!-- Bottom Navigation -->
  <div class="bottom-nav">
    {"".join(bottom_links)}
  </div>

</div>

<script>
  const STORAGE_KEY = 'ielts_mastered_{part_id}';
  let curBand = 'all';
  let curCat = 'all';
  let isQuiz = true;

  function speak(text) {{
    if ('speechSynthesis' in window) {{
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'en-US';
      u.rate = 0.9;
      window.speechSynthesis.speak(u);
    }} else {{
      alert('您的浏览器不支持语音朗读功能');
    }}
  }}

  function getSet() {{
    try {{
      const d = localStorage.getItem(STORAGE_KEY);
      return d ? new Set(JSON.parse(d)) : new Set();
    }} catch (e) {{
      return new Set();
    }}
  }}

  function saveSet(s) {{
    try {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...s]));
    }} catch (e) {{}}
  }}

  function toggleMaster(wid) {{
    const s = getSet();
    if (s.has(wid)) {{
      s.delete(wid);
      setRowMastered(wid, false);
    }} else {{
      s.add(wid);
      setRowMastered(wid, true);
    }}
    saveSet(s);
    renderProg();
  }}

  function setRowMastered(wid, state) {{
    const c = document.getElementById('card-' + wid);
    if (c) {{
      c.classList.toggle('mastered', state);
      const box = c.querySelector('.chk-card');
      if (box) box.checked = state;
    }}
    const r = document.getElementById('row-' + wid);
    if (r) {{
      r.classList.toggle('mastered', state);
      const box = r.querySelector('.chk-table');
      if (box) box.checked = state;
    }}
  }}

  function markAllMastered(isAll) {{
    const s = getSet();
    const cards = document.querySelectorAll('.word-card');
    cards.forEach(card => {{
      const wid = parseInt(card.getAttribute('data-id'), 10);
      if (isAll) s.add(wid);
      else s.delete(wid);
      setRowMastered(wid, isAll);
    }});
    saveSet(s);
    renderProg();
  }}

  function renderProg() {{
    const s = getSet();
    const all = document.querySelectorAll('.word-card').length || 600;
    const cnt = s.size;
    const pct = Math.round((cnt / all) * 100);
    document.getElementById('progCount').textContent = `${{cnt}} / ${{all}} (${{pct}}%)`;
    document.getElementById('progBar').style.width = pct + '%';
  }}

  function switchView(mode) {{
    const g = document.getElementById('gridCards');
    const t = document.getElementById('tableContainer');
    const bC = document.getElementById('btnCard');
    const bT = document.getElementById('btnTable');
    if (mode === 'card') {{
      g.style.display = 'grid';
      t.style.display = 'none';
      bC.classList.add('active');
      bT.classList.remove('active');
    }} else {{
      g.style.display = 'none';
      t.style.display = 'block';
      bC.classList.remove('active');
      bT.classList.add('active');
    }}
  }}

  // Toggle reveal for single word
  function toggleWordReveal(wid, show) {{
    const cardM = document.getElementById('meaning-card-' + wid);
    const rowM = document.getElementById('meaning-row-' + wid);
    const cardC = document.getElementById('reveal-card-' + wid);
    const rowC = document.getElementById('reveal-row-' + wid);
    const cardL = document.getElementById('lbl-card-' + wid);
    const rowL = document.getElementById('lbl-row-' + wid);

    if (show) {{
      if (cardM) {{ cardM.classList.add('revealed'); cardM.classList.remove('word-hidden'); }}
      if (rowM) {{ rowM.classList.add('revealed'); rowM.classList.remove('word-hidden'); }}
      if (cardC) cardC.checked = true;
      if (rowC) rowC.checked = true;
      if (cardL) cardL.classList.add('active');
      if (rowL) rowL.classList.add('active');
    }} else {{
      if (cardM) {{ cardM.classList.remove('revealed'); cardM.classList.add('word-hidden'); }}
      if (rowM) {{ rowM.classList.remove('revealed'); rowM.classList.add('word-hidden'); }}
      if (cardC) cardC.checked = false;
      if (rowC) rowC.checked = false;
      if (cardL) cardL.classList.remove('active');
      if (rowL) rowL.classList.remove('active');
    }}
  }}

  function clickMeaningBox(wid) {{
    const cardC = document.getElementById('reveal-card-' + wid);
    const cur = cardC ? cardC.checked : false;
    toggleWordReveal(wid, !cur);
  }}

  function batchSetReveal(show) {{
    const cards = document.querySelectorAll('.word-card');
    cards.forEach(card => {{
      const wid = parseInt(card.getAttribute('data-id'), 10);
      toggleWordReveal(wid, show);
    }});
    const chipHide = document.getElementById('chipHide');
    const chipShow = document.getElementById('chipShow');
    if (show) {{
      document.body.classList.remove('quiz-mode');
      isQuiz = false;
      if (chipShow) chipShow.classList.add('active');
      if (chipHide) chipHide.classList.remove('active');
      const btn = document.getElementById('btnQuiz');
      if (btn) {{ btn.classList.remove('active'); btn.textContent = '🧠 刷词自测(遮盖)'; }}
    }} else {{
      document.body.classList.add('quiz-mode');
      isQuiz = true;
      if (chipHide) chipHide.classList.add('active');
      if (chipShow) chipShow.classList.remove('active');
      const btn = document.getElementById('btnQuiz');
      if (btn) {{ btn.classList.add('active'); btn.textContent = '👁️ 全部展开释义'; }}
    }}
  }}

  function toggleQuiz() {{
    batchSetReveal(isQuiz ? true : false);
  }}

  function setBand(val, btn) {{
    curBand = val;
    btn.parentNode.querySelectorAll('.chip').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    doSearch();
  }}

  function setCat(val, btn) {{
    curCat = val;
    btn.parentNode.querySelectorAll('.chip').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    doSearch();
  }}

  function doSearch() {{
    const q = document.getElementById('filterInput').value.trim().toLowerCase();
    const cards = document.querySelectorAll('.word-card');
    let visible = 0;

    cards.forEach(card => {{
      const w = card.getAttribute('data-w').toLowerCase();
      const m = card.getAttribute('data-m').toLowerCase();
      const b = card.getAttribute('data-b');
      const cat = card.getAttribute('data-t');
      const wid = card.getAttribute('data-id');
      const row = document.getElementById('row-' + wid);

      let textOk = !q || w.includes(q) || m.includes(q);
      let bandOk = (curBand === 'all') || (b === curBand);
      let catOk = (curCat === 'all') || cat.includes(curCat);

      if (textOk && bandOk && catOk) {{
        card.style.display = 'flex';
        if (row) row.style.display = '';
        visible++;
      }} else {{
        card.style.display = 'none';
        if (row) row.style.display = 'none';
      }}
    }});

    const empty = document.getElementById('emptyBox');
    if (visible === 0) empty.style.display = 'block';
    else empty.style.display = 'none';
  }}

  window.addEventListener('DOMContentLoaded', () => {{
    const s = getSet();
    s.forEach(wid => {{
      setRowMastered(wid, true);
    }});
    // Default: do not show meanings. Radios are unchecked by default.
    document.querySelectorAll('.chk-reveal, .chk-reveal-tbl').forEach(cb => cb.checked = false);
    document.querySelectorAll('.reveal-ctrl, .reveal-ctrl-sm').forEach(lbl => lbl.classList.remove('active'));
    renderProg();
  }});
</script>
</body>
</html>
"""
    out_file = os.path.join(WORKSPACE, part["filename"])
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Generated {out_file} with {len(slice_words)} words.")

print("All 5 IELTS parts generated successfully!")
