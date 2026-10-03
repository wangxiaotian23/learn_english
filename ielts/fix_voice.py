#!/usr/bin/env python3
"""升级朗读：优先 macOS Premium/Enhanced 高自然度语音 + 页面语音选择器（记住偏好）。幂等。"""
import re
from pathlib import Path

DIR = Path(__file__).parent
FILES = [f"ielts_part{n}{s}.html" for n in range(1, 6) for s in "ab"]

JS_BLOCK = re.compile(
    r"  var __voice = null;.*?synth\.speak\(u\);\n  \}\n",
    re.S,
)

NEW_FUNC = """  var __voice = null;
  function pickVoice() {
    var vs = window.speechSynthesis.getVoices() || [];
    if (!vs.length) return null;
    var pref = ['Ava (Premium)', 'Ava (Enhanced)', 'Zoe (Premium)', 'Zoe (Enhanced)',
                'Allison (Premium)', 'Allison (Enhanced)', 'Susan (Enhanced)', 'Nicky (Premium)',
                'Samantha', 'Google UK English Female', 'Google US English',
                'Microsoft Aria', 'Microsoft Jenny', 'Daniel', 'Karen', 'Alex'];
    for (var i = 0; i < pref.length; i++) {
      for (var j = 0; j < vs.length; j++) {
        if (vs[j].name.indexOf(pref[i]) !== -1) return vs[j];
      }
    }
    var en = vs.filter(function (v) { return (v.lang || '').toLowerCase().indexOf('en') === 0; });
    return en.filter(function (v) { return v.lang === 'en-US'; })[0] || en[0] || null;
  }
  function savedVoiceName() {
    try { return localStorage.getItem('ielts-voice') || ''; } catch (e) { return ''; }
  }
  function resolveVoice() {
    var saved = savedVoiceName();
    if (saved) {
      var hit = (window.speechSynthesis.getVoices() || []).filter(function (v) { return v.name === saved; });
      if (hit.length) return hit[0];
    }
    return pickVoice();
  }
  function speak(text) {
    if (!('speechSynthesis' in window)) {
      alert('您的浏览器不支持语音朗读功能');
      return;
    }
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
    try { localStorage.setItem('ielts-voice', name); } catch (e) {}
    __voice = null;
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  }
  function fillVoiceSelect() {
    var sel = document.getElementById('voiceSelect');
    if (!sel || document.getElementById('voiceSelect').options.length > 1) return;
    var saved = savedVoiceName();
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
"""

VOICE_CSS = """<!--VOICE-CSS--><style>
  #voiceSelect { padding: 8px 10px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; color: #0f172a; font-size: 12px; max-width: 200px; cursor: pointer; }
  #voiceSelect:hover { border-color: #2563eb; }
</style><!--/VOICE-CSS-->"""


def main() -> None:
    for name in FILES:
        path = DIR / name
        content = path.read_text(encoding="utf-8")

        content, n = JS_BLOCK.subn(NEW_FUNC, content)
        assert n == 1, f"{name}: speak 区块替换 {n} 处"

        # 注入语音下拉框（幂等：已存在则跳过）
        if 'id="voiceSelect"' not in content:
            assert '刷词自测(遮盖)</button>' in content, f"{name}: 找不到工具栏锚点"
            content = content.replace(
                '刷词自测(遮盖)</button>', '刷词自测(遮盖)</button>'
                '<select id="voiceSelect" onchange="onVoicePick(this.value)" '
                'title="选择朗读语音，偏好会保存在本机"><option value="">🎙️ 语音：自动</option></select>',
                1,
            )

        # 注入样式（幂等）
        if "<!--VOICE-CSS-->" not in content:
            content = content.replace("</head>", VOICE_CSS + "\n</head>", 1)

        path.write_text(content, encoding="utf-8")
        print(f"{name}: speak() 已升级 + 语音选择器 ✓")
    print("全部完成")


if __name__ == "__main__":
    main()
