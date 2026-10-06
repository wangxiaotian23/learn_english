#!/usr/bin/env python3
"""生成 ielts/quiz.html：10 个随机词同页展示、一起提交批改的中文填空测验，数据内嵌，纯前端。"""
import json
from pathlib import Path

DIR = Path(__file__).parent

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>随机单词小测验 · 雅思3000核心词汇</title>
<style>
  :root { --primary:#2563eb; --primary-dark:#1e40af; --bg:#f8fafc; --card:#fff; --text:#1e293b; --muted:#64748b; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:"PingFang SC","Microsoft YaHei","Helvetica Neue",Arial,sans-serif; background:var(--bg); color:var(--text); line-height:1.7; }
  .container { max-width:680px; margin:0 auto; padding:16px 16px 60px; }
  nav.top { display:flex; justify-content:space-between; padding:10px 0; font-size:14px; }
  nav.top a { color:var(--primary); text-decoration:none; padding:6px 14px; border:1px solid #dbeafe; border-radius:8px; background:var(--card); }
  header.hero { background:linear-gradient(135deg,var(--primary-dark),var(--primary)); color:#fff; border-radius:16px; padding:28px 24px; margin:8px 0 24px; }
  header.hero h1 { font-size:24px; margin-bottom:6px; }
  header.hero p { opacity:.92; font-size:14px; margin-bottom:10px; }
  .card { background:var(--card); border:1px solid #e2e8f0; border-radius:14px; padding:24px; margin-bottom:16px; }
  .start-box { text-align:center; padding:40px 24px; }
  .start-box p { color:var(--muted); font-size:14px; margin-bottom:20px; }
  .btn-main { background:var(--primary); color:#fff; border:none; border-radius:12px; padding:12px 36px; font-size:16px; cursor:pointer; font-family:inherit; }
  .btn-main:hover { background:var(--primary-dark); }
  .toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; font-size:13px; color:var(--muted); }
  .btn { border:none; border-radius:10px; padding:10px 22px; font-size:14px; cursor:pointer; font-family:inherit; }
  .btn.primary { background:var(--primary); color:#fff; }
  .btn.primary:hover { background:var(--primary-dark); }
  .btn.ghost { background:#f1f5f9; color:var(--muted); }
  .btn-row { display:flex; gap:10px; margin-top:18px; }
  .q-row { padding:16px 0; border-bottom:1px solid #e2e8f0; }
  .q-row:last-child { border-bottom:none; }
  .q-head { display:flex; align-items:center; gap:12px; margin-bottom:8px; }
  .q-index { font-size:13px; color:var(--muted); width:26px; }
  .q-word { font-size:26px; color:var(--primary-dark); font-weight:700; }
  .voice-btn { background:#eff6ff; border:1px solid #bfdbfe; border-radius:50%; width:36px; height:36px; cursor:pointer; font-size:14px; }
  .voice-btn:hover { background:#dbeafe; }
  .q-tag { margin-left:auto; font-size:14px; font-weight:600; }
  .q-tag.ok { color:#047857; }
  .q-tag.close { color:#b45309; }
  .q-tag.wrong { color:#b91c1c; }
  input.answer {
    width:100%; padding:11px 14px; font-size:15px; border:2px solid #dbeafe; border-radius:10px;
    outline:none; font-family:inherit; background:#fff;
  }
  input.answer:focus { border-color:var(--primary); }
  input.answer:disabled { background:#f1f5f9; }
  .verdict { margin-top:8px; border-radius:8px; padding:8px 12px; font-size:13px; display:none; }
  .verdict.ok { background:#ecfdf5; border:1px solid #a7f3d0; color:#047857; display:block; }
  .verdict.close { background:#fffbeb; border:1px solid #fde68a; color:#b45309; display:block; }
  .verdict.wrong { background:#fef2f2; border:1px solid #fecaca; color:#b91c1c; display:block; }
  .verdict .std { color:var(--text); font-weight:600; }
  .hint { font-size:12px; color:var(--muted); margin-top:10px; }
  .score-box { text-align:center; padding:30px 24px; }
  .score-num { font-size:52px; font-weight:800; color:var(--primary); }
  .missed { text-align:left; background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:14px 18px; margin-top:18px; font-size:14px; }
  .missed li { margin:4px 0 4px 18px; }
  #voiceSelect { padding:6px 10px; border-radius:8px; border:1px solid rgba(255,255,255,.4); background:rgba(255,255,255,.15); color:#fff; font-size:12px; max-width:200px; cursor:pointer; }
  #voiceSelect option { color:#1e293b; }
</style>
</head>
<body>
<div class="container">

  <nav class="top">
    <a href="../index.html">← 英语主页</a>
    <a href="ielts_part1a.html">词汇分册 →</a>
  </nav>

  <header class="hero">
    <h1>🎲 随机单词小测验</h1>
    <p>从 3000 个雅思核心词中随机抽 10 个，填中文释义，一起提交批改，意思相近就算对。</p>
    <select id="voiceSelect" onchange="onVoicePick(this.value)" title="选择朗读语音"><option value="">🎙️ 语音：自动</option></select>
  </header>

  <div class="card start-box" id="startBox">
    <p>每轮 10 个词 · 判定规则：与释义一致 ✔ · 意思相近 ≈ 算对 · 空着不填按跳过计</p>
    <button class="btn-main" onclick="startRound()">开始一轮</button>
  </div>

  <div class="card" id="quizBox" style="display:none">
    <div class="toolbar">
      <span id="progText">10 个词 · 填完点「提交全部」</span>
      <span id="scoreText"></span>
    </div>
    <div id="questionList"></div>
    <div class="btn-row">
      <button class="btn primary" id="submitAllBtn" onclick="submitAll()">✅ 提交全部</button>
      <button class="btn ghost" onclick="startRound()">🔄 换一批</button>
    </div>
    <div class="hint">提示：Enter 键直接交卷 · 只看核心意思，多写少写义项没关系 · 交卷后每题下方显示正确释义</div>
  </div>

  <div class="card score-box" id="scoreBox" style="display:none">
    <div style="font-size:15px;color:var(--muted)">本轮成绩</div>
    <div class="score-num" id="finalScore">0 / 10</div>
    <div id="finalNote" style="font-size:14px;color:var(--muted)"></div>
    <div class="missed" id="missedList" style="display:none"></div>
    <div id="quizHistory" style="display:none;margin-top:18px;font-size:13px;color:var(--muted);text-align:left"></div>
    <button class="btn-main" style="margin-top:22px" onclick="startRound()">再来一轮</button>
  </div>

</div>
<script>
var VOCAB = __VOCAB__;

var ROUND_SIZE = 10;
var queue = [], graded = false;

var SYN_GROUPS = [
  ['天气', '气候'], ['高兴', '快乐', '开心', '愉快'], ['薪水', '工资', '薪酬', '收入'],
  ['电影', '影片'], ['老师', '教师', '导师'], ['孩子', '儿童', '小孩'], ['房子', '住宅', '房屋'],
  ['垃圾', '废物'], ['疾病', '病症'], ['聪明', '聪慧', '机智'], ['愚蠢', '愚昧', '笨'],
  ['美丽', '漂亮', '好看'], ['丑陋', '难看'], ['富有', '富裕', '有钱'], ['贫穷', '贫困', '穷'],
  ['快速', '迅速', '快'], ['缓慢', '迟缓', '慢'], ['巨大', '庞大'], ['微小', '细小'],
  ['重要', '关键', '要紧'], ['著名', '知名', '有名'], ['努力', '勤奋', '用功'], ['懒惰', '懒散'],
  ['开始', '着手', '启动'], ['结束', '终止', '完成'], ['增加', '增长', '上升'], ['减少', '降低', '下降'],
  ['保护', '守护', '维护'], ['破坏', '损坏', '毁坏'], ['帮助', '协助', '援助'], ['阻止', '防止'],
  ['选择', '挑选'], ['改变', '变更', '转变'], ['考虑', '思考', '斟酌'], ['解释', '说明', '阐明'],
  ['证明', '证实'], ['显示', '表明', '展示'], ['获得', '取得', '得到'], ['提供', '供给', '给予'],
  ['放弃', '舍弃'], ['坚持', '执意', '坚守'], ['支持', '拥护', '赞成'], ['反对', '抵制', '抗拒'],
  ['普遍', '广泛'], ['罕见', '稀少', '稀有'], ['昂贵', '贵'], ['便宜', '廉价'], ['新鲜', '新'],
  ['古老', '陈旧', '旧'], ['危险', '凶险'], ['安全', '平安'], ['健康', '健全'], ['污染', '沾污'],
  ['政府', '当局'], ['公司', '企业', '厂商'], ['学校', '院校'], ['学生', '学员'], ['工作', '职业', '职务'],
  ['旅行', '旅游'], ['需求', '需要'], ['结果', '后果', '成果'], ['原因', '起因', '缘由']
];

var SYN_MAP = {};
SYN_GROUPS.forEach(function (group) {
  group.forEach(function (word) {
    SYN_MAP[word] = group[0];
  });
});

function normalize(s) {
  return (s || '').replace(/[（）()、，。；;：:\"\"'‘’\s\-—·]/g, '');
}

function canon(s) {
  s = normalize(s);
  Object.keys(SYN_MAP).forEach(function (k) {
    s = s.split(k).join(SYN_MAP[k]);
  });
  return s;
}

function bigrams(s) {
  var set = {};
  for (var i = 0; i < s.length - 1; i++) set[s.substring(i, i + 2)] = true;
  if (s.length === 1) set[s] = true;
  return set;
}

function dice(a, b) {
  var A = bigrams(a), B = bigrams(b);
  var na = Object.keys(A).length, nb = Object.keys(B).length;
  if (!na || !nb) return 0;
  var inter = 0;
  Object.keys(A).forEach(function (g) { if (B[g]) inter++; });
  return (2 * inter) / (na + nb);
}

/* 返回 'ok' | 'close' | 'wrong' | 'english' */
function judge(input, meaning, word) {
  var a = canon(input);
  if (!a) return 'wrong';
  if (a === normalize(word)) return 'english';
  var senses = meaning.split(/[；;]/).map(canon).filter(Boolean);
  for (var i = 0; i < senses.length; i++) {
    var s = senses[i];
    if (a === s) return 'ok';
    if (s.length >= 2 && (s.indexOf(a) !== -1 || a.indexOf(s) !== -1)) return 'ok';
  }
  var best = 0;
  for (var j = 0; j < senses.length; j++) best = Math.max(best, dice(a, senses[j]));
  if (best >= 0.4) return 'close';
  return 'wrong';
}

var VOICE_PREF_KEY = 'ielts-voice';
var __voice = null;
function resolveVoice() {
  var saved = '';
  try { saved = localStorage.getItem(VOICE_PREF_KEY) || ''; } catch (e) {}
  var vs = window.speechSynthesis.getVoices() || [];
  if (saved) {
    var hit = vs.filter(function (v) { return v.name === saved; });
    if (hit.length) return hit[0];
  }
  var pref = ['Ava (Premium)', 'Ava (Enhanced)', 'Zoe (Premium)', 'Samantha', 'Google UK English Female', 'Google US English', 'Microsoft Aria'];
  for (var i = 0; i < pref.length; i++) {
    for (var j = 0; j < vs.length; j++) {
      if (vs[j].name.indexOf(pref[i]) !== -1) return vs[j];
    }
  }
  var en = vs.filter(function (v) { return (v.lang || '').toLowerCase().indexOf('en') === 0; });
  return en[0] || null;
}
function speak(text) {
  if (!('speechSynthesis' in window)) return;
  var synth = window.speechSynthesis;
  synth.cancel();
  if (!__voice) {
    __voice = resolveVoice();
    synth.onvoiceschanged = function () { __voice = resolveVoice(); fillVoiceSelect(); };
  }
  var u = new SpeechSynthesisUtterance(text);
  u.lang = 'en-US';
  u.rate = 0.85;
  if (__voice) u.voice = __voice;
  synth.speak(u);
}
function onVoicePick(name) {
  try { localStorage.setItem(VOICE_PREF_KEY, name); } catch (e) {}
  __voice = null;
}
function fillVoiceSelect() {
  var sel = document.getElementById('voiceSelect');
  if (!sel || sel.options.length > 1) return;
  var saved = '';
  try { saved = localStorage.getItem(VOICE_PREF_KEY) || ''; } catch (e) {}
  var vs = (window.speechSynthesis.getVoices() || []).filter(function (v) {
    return (v.lang || '').toLowerCase().indexOf('en') === 0;
  });
  vs.forEach(function (v) {
    var o = document.createElement('option');
    o.value = v.name;
    o.textContent = '🎙️ ' + v.name;
    if (v.name === saved) o.selected = true;
    sel.appendChild(o);
  });
}
window.addEventListener('DOMContentLoaded', fillVoiceSelect);

function shuffle(arr) {
  for (var i = arr.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
  }
  return arr;
}

function startRound() {
  queue = shuffle(VOCAB.slice()).slice(0, ROUND_SIZE);
  graded = false;
  document.getElementById('startBox').style.display = 'none';
  document.getElementById('scoreBox').style.display = 'none';
  document.getElementById('quizBox').style.display = 'block';
  document.getElementById('scoreText').textContent = '';
  var html = '';
  for (var i = 0; i < queue.length; i++) {
    var w = queue[i];
    html += '<div class="q-row" id="qrow-' + i + '">'
      + '<div class="q-head"><span class="q-index">' + (i + 1) + '</span>'
      + '<h2 class="q-word">' + w.word + '</h2>'
      + '<button class="voice-btn" onclick="speak(\'' + w.word.replace(/'/g, "\\'") + '\')">🔊</button>'
      + '<span class="q-tag" id="qtag-' + i + '"></span></div>'
      + '<input class="answer" id="answer-' + i + '" placeholder="填写中文释义…" autocomplete="off" '
      + 'onkeydown="if(event.key===\'Enter\')submitAll()">'
      + '<div class="verdict" id="verdict-' + i + '"></div>'
      + '</div>';
  }
  document.getElementById('questionList').innerHTML = html;
  document.getElementById('submitAllBtn').style.display = '';
  var first = document.getElementById('answer-0');
  if (first) first.focus();
}

function submitAll() {
  if (graded) return;
  graded = true;
  var score = 0, missed = [];
  for (var i = 0; i < queue.length; i++) {
    var w = queue[i];
    var raw = document.getElementById('answer-' + i).value.trim();
    var v = document.getElementById('verdict-' + i);
    var tag = document.getElementById('qtag-' + i);
    var result = raw ? judge(raw, w.meaning, w.word) : 'wrong';
    var skipped = !raw;

    if (result === 'english') {
      v.className = 'verdict wrong';
      v.innerHTML = '请填写<b>中文</b>释义。正确释义：<span class="std">' + w.meaning + '</span>';
      tag.textContent = '✘';
      tag.className = 'q-tag wrong';
      missed.push(w);
    } else if (result === 'ok') {
      score++;
      v.className = 'verdict ok';
      v.innerHTML = '✔ <b>正确！</b>标准释义：<span class="std">' + w.meaning + '</span>';
      tag.textContent = '✔';
      tag.className = 'q-tag ok';
    } else if (result === 'close') {
      score++;
      v.className = 'verdict close';
      v.innerHTML = '≈ <b>意思相近，算对。</b>标准释义：<span class="std">' + w.meaning + '</span>';
      tag.textContent = '≈';
      tag.className = 'q-tag close';
    } else {
      v.className = 'verdict wrong';
      v.innerHTML = (skipped ? '⏭ 未填。' : '✘ <b>不对。</b>') + '正确释义：<span class="std">' + w.meaning + '</span>';
      tag.textContent = skipped ? '⏭' : '✘';
      tag.className = 'q-tag wrong';
      missed.push(w);
    }
    document.getElementById('answer-' + i).disabled = true;
  }

  document.getElementById('submitAllBtn').style.display = 'none';
  document.getElementById('scoreText').textContent = '得分 ' + score + ' / ' + queue.length;
  document.getElementById('scoreBox').style.display = 'block';
  document.getElementById('finalScore').textContent = score + ' / ' + queue.length;
  var note = score === queue.length ? '满分！太强了 🎉'
    : score >= 7 ? '很不错，继续保持！'
    : score >= 4 ? '有进步空间，错词再看一眼。'
    : '别灰心，把这些词加进今天的复习。';
  document.getElementById('finalNote').textContent = note;
  var m = document.getElementById('missedList');
  if (missed.length) {
    m.style.display = 'block';
    m.innerHTML = '<b>本轮错词（' + missed.length + ' 个）：</b><ul>'
      + missed.map(function (w) { return '<li><b>' + w.word + '</b> — ' + w.meaning + '</li>'; }).join('')
      + '</ul>';
  } else {
    m.style.display = 'none';
  }
  document.getElementById('scoreBox').scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  /* 登录用户：上报成绩并显示最近历史 */
  fetch('/api/me', { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (me) {
    if (!me.ok) return;
    return fetch('/api/quiz/result', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        score: score, total: queue.length,
        wrong_ids: missed.map(function (w) { return VOCAB_WORD_ID[w.word]; })
      })
    }).then(function () { return fetch('/api/quiz/history', { credentials: 'same-origin' }); })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j.ok || !j.history.length) return;
        var box = document.getElementById('quizHistory');
        box.style.display = 'block';
        box.innerHTML = '<b>最近几轮成绩</b>：' + j.history.map(function (h) {
          return h.score + '/' + h.total + '（' + h.created_at + '）';
        }).join(' · ');
      });
  }).catch(function () {});
}

var VOCAB_WORD_ID = {};
(function () {
  for (var i = 0; i < VOCAB.length; i++) VOCAB_WORD_ID[VOCAB[i].word] = i + 1;
})();
</script>
</body>
</html>
"""


def main() -> None:
    words = json.loads((DIR / "vocab_3000.json").read_text(encoding="utf-8"))
    assert len(words) == 3000
    data = json.dumps(
        [{"word": w["word"], "meaning": w["meaning"]} for w in words],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    html = TEMPLATE.replace("__VOCAB__", data)
    out = DIR / "quiz.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out}: 生成完成，内嵌 {len(words)} 词，大小 {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
