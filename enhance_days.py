#!/usr/bin/env python3
"""增强 day1-7.html：重点短语高亮+点击释义、对话音频/跟读、每日课后小练习。幂等。"""
import re
from pathlib import Path

DIR = Path(__file__).parent

# ---------------- 短语词典（day → [(phrase, 中文释义)]） ----------------
PHRASES = {
    1: [
        ("kick us off", "让我们开始（第一个发言）"),
        ("No blockers on my side", "我这边没有阻塞"),
        ("blocked on", "被……卡住/阻塞"),
        ("waiting on", "在等（某人/某事）"),
        ("walk you through", "给你逐步讲解"),
        ("on the same page", "信息一致；达成共识"),
        ("by end of day", "今天下班前（EOD）"),
        ("if time permits", "如果时间允许"),
        ("turns out", "结果发现是……"),
        ("To be honest", "说实话"),
        ("behind schedule", "进度落后"),
        ("get back on track", "回到正轨、赶上进度"),
        ("raise a ticket", "提工单"),
        ("descope", "移出本期范围"),
        ("wrap it up", "收尾、完成"),
        ("Will do", "好的，照办"),
        ("sync after standup", "站会后对一下"),
        ("ping me", "喊我一声、戳我"),
    ],
    2: [
        ("running into an issue", "遇到问题"),
        ("reproduce it consistently", "每次都能复现"),
        ("walk me through", "给我逐步讲一遍"),
        ("Just to clarify", "确认一下"),
        ("on the same page", "理解一致"),
        ("play that back", "复述一遍（确认理解）"),
        ("make sense", "讲得通、清楚吗"),
        ("What's going on", "怎么回事"),
        ("staring at it", "盯着看了很久"),
        ("good point", "有道理"),
        ("band-aid", "权宜之计、创可贴式修法"),
        ("edge case", "边界情况"),
        ("must-have", "硬性要求"),
        ("nice-to-have", "有最好、没有也行"),
        ("targeting", "以……为目标"),
        ("I'm on board", "我同意、加入"),
        ("narrowing it down", "缩小范围定位"),
        ("hop on a call", "打个电话/开个短会"),
    ],
    3: [
        ("Good catch", "发现得好！"),
        ("must-fix", "必须修的（阻塞合并）"),
        ("nit", "小问题（不阻塞合并）"),
        ("Non-blocking", "不阻塞合并的"),
        ("for future reference", "供以后参考"),
        ("Might it be cleaner", "会不会更干净……（委婉建议）"),
        ("I wonder if", "我在想能不能（极委婉）"),
        ("backward-compatible", "向后兼容"),
        ("go with", "选择、采用"),
        ("back and forth", "来回拉锯"),
        ("Happy to be convinced", "乐意被说服"),
        ("LGTM", "Looks Good To Me，同意合并"),
        ("re-review", "复审"),
        ("moving fast", "推进很快"),
        ("pre-fetch", "预取、提前加载"),
        ("pay the cost", "付一次成本"),
        ("solid", "扎实的、靠谱的"),
        ("Addressed all comments", "所有意见都处理了"),
    ],
    4: [
        ("jump in", "插句话"),
        ("Sorry to interrupt", "抱歉打断一下"),
        ("Building on what", "接着（某人）说的"),
        ("flagging", "提出来（风险等）"),
        ("I see it a bit differently", "我的看法略有不同"),
        ("fair point", "有道理"),
        ("play devil's advocate", "唱个反调（对事不对人）"),
        ("middle ground", "折中方案"),
        ("take this offline", "线下再聊、会后单聊"),
        ("into the weeds", "陷入细节"),
        ("To sum up", "总结一下"),
        ("Are we aligned", "大家一致吗"),
        ("I can get behind", "我可以支持"),
        ("kick things off", "先开个头"),
        ("elaborate", "展开讲讲"),
        ("didn't quite catch", "没太听清"),
        ("short-term fix", "短期方案"),
        ("sell that to", "让……接受这个说法"),
    ],
    5: [
        ("walk you through", "带你逐步看一遍"),
        ("keep it to", "控制在（时间内）"),
        ("use case", "使用场景"),
        ("As you can see", "如你所见"),
        ("moving on to", "接下来看"),
        ("where it gets interesting", "有意思的部分来了"),
        ("To recap", "回顾一下"),
        ("Think of it like", "把它想象成……（类比）"),
        ("In simple terms", "简单来说"),
        ("The short version is", "长话短说"),
        ("key takeaway", "关键要点"),
        ("What that means for", "这对……意味着"),
        ("bear with me", "稍等一下、包容一下"),
        ("great question", "问得真好"),
        ("The short answer is", "简短回答是"),
        ("follow up with", "事后跟进（邮件/电话）"),
        ("safety net", "安全网、兜底"),
        ("green-light", "批准、放行"),
    ],
    6: [
        ("How was your weekend", "周末过得怎么样"),
        ("checked out", "去看了/试了（新店等）"),
        ("been meaning to", "一直想去（还没去）"),
        ("took it easy", "放松休息"),
        ("caught up on", "补上（睡眠/剧）"),
        ("No way", "不会吧！（惊讶）"),
        ("hits close to home", "太贴近现实了"),
        ("Same here", "我也一样"),
        ("coming along", "进展（如何）"),
        ("the good kind of busy", "良性的忙"),
        ("I should get going", "我该走了"),
        ("running into you", "碰到你（很巧）"),
        ("grab a coffee", "喝杯咖啡、约咖啡"),
        ("catch up properly", "好好聊聊"),
        ("pick your brain", "请教一下你"),
        ("Say hi to", "替我向……问好"),
        ("Nothing that fancy", "没那么复杂"),
    ],
    7: [
        ("shipped", "上线了（功能）"),
        ("closed eleven tickets", "关闭了十一个工单"),
        ("the highlight of the week", "本周亮点"),
        ("went out", "发布出去"),
        ("zero incidents", "零故障"),
        ("on track", "进度正常"),
        ("behind schedule", "进度落后"),
        ("back on track", "赶上进度"),
        ("One risk to flag", "有一个风险要提"),
        ("What went well", "做得好的地方"),
        ("didn't go so well", "不太顺利的地方"),
        ("Going forward", "往后、今后"),
        ("action item", "行动项"),
        ("cutoff", "截止点"),
        ("Good call", "好主意、说得对"),
        ("get up to speed", "快速上手"),
        ("That's a solid update", "这个汇报很扎实"),
        ("we'll revisit", "我们再回顾/重新评估"),
    ],
}

# ---------------- 每日课后小练习（5 道单选） ----------------
QUIZ = {
    1: [
        ("站会上汇报「昨天完成了登录接口」，最自然的是：",
         ["Yesterday I finished implementing the login API.",
          "Yesterday I am finishing the login API.",
          "Yesterday the login API finishes me.",
          "Tomorrow I finished the login API."], 0,
         "汇报昨天用过去时 finished；「be finishing」不是过去时的正确用法。"),
        ("想说「我这边没有阻塞」，应该说：",
         ["I have no blockers.",
          "No blockers on my side.",
          "I am not blocking anyone's road.",
          "There is no blocker with me."], 1,
         "站会标准句是 No blockers on my side，简洁且地道。"),
        ("被第三方沙箱卡住了，可以说 I'm ______ the third-party sandbox。",
         ["blocked on", "blocking at", "stopped in", "stuck to"], 0,
         "be blocked on sth 是描述阻塞的固定搭配。"),
        ("想让同事站会后给你讲细节，最礼貌的是：",
         ["Explain it to me now.",
          "Could we sync after standup?",
          "You must tell me details.",
          "Tell me the details after standup, OK?"], 1,
         "Could we sync after standup? 委婉且符合站会「深入讨论另约时间」的惯例。"),
        ("领导说进度落后，你给出补救方案时用：",
         ["To get back on track, we're bringing in one more engineer.",
          "For getting the track back, one more engineer comes.",
          "Back the track, we add an engineer.",
          "Getting back track needs one engineer."], 0,
         "get back on track 是「赶上进度」的地道表达。"),
    ],
    2: [
        ("向同事描述「这个问题偶发，五次里出现一次」：",
         ["It happens intermittently — maybe one in five times.",
          "It happens every time, maybe five.",
          "It never happens, one of five.",
          "It happens continuous, one in five times."], 0,
         "intermittently = 偶发地；one in five times 表示概率。"),
        ("没听清对方的解释，想请他再讲一遍：",
         ["Sorry, I didn't quite catch that — could you say it again?",
          "Sorry, I didn't take that — speak again?",
          "I caught nothing, repeat now.",
          "Your words escaped me, again please."], 0,
         "I didn't quite catch that 是没听清的地道说法。"),
        ("想确认双方理解一致，用：",
         ["Just to make sure we're on the same page —",
          "Just to make us in one page —",
          "Ensure our pages are same —",
          "Let's page each other —"], 0,
         "on the same page 固定搭配，表示理解一致。"),
        ("复述对方需求确认没理解错，开头说：",
         ["Let me play that back to you.",
          "Let me play that ball to you.",
          "Let me replay you that.",
          "Let me return your play."], 0,
         "play back 在沟通里表示「复述一遍」。"),
        ("前辈说你的修法只是权宜之计，他会说：",
         ["Increasing the timeout is a band-aid.",
          "Increasing the timeout is a band.",
          "The timeout is band-aiding you.",
          "This timeout band is aid."], 0,
         "band-aid 本义创可贴，引申为「权宜之计」。"),
    ],
    3: [
        ("评审时发现别人没注意到的 bug，开头夸一句：",
         ["Good catch!", "Good take!", "Well caught bug!", "Nice grab!"], 0,
         "Good catch! 是 code review 里最常用的称赞。"),
        ("指出一个不阻塞合并的小问题，先说：",
         ["Nit: this variable name could be more descriptive.",
          "BLOCKER: rename this variable or I quit.",
          "Must-fix: the name is wrong.",
          "Fatal: variable name issue."], 0,
         "nit 表示吹毛求疵的小点，不阻塞合并。"),
        ("委婉建议把逻辑抽成函数：",
         ["Might it be cleaner to extract this logic into a separate function?",
          "You must extract this logic now.",
          "Extracting the logic is cleaner, do it.",
          "This logic is dirty, clean it."], 0,
         "Might it be...? 是委婉提建议的经典句式。"),
        ("想表达「乐意被说服，要不要打个电话聊」：",
         ["Happy to be convinced otherwise — want to hop on a quick call?",
          "Happy to be argued — call me now!",
          "I am convincible, phone!",
          "Convince me happy on a call."], 0,
         "Happy to be convinced otherwise + hop on a call 是意见僵持时的标准话术。"),
        ("改完全部评审意见后请人复审：",
         ["Addressed all comments — could you take another look?",
          "All comments are addressed by me, look again.",
          "I did your comments, re-look please.",
          "Comments addressed fully, review again now."], 0,
         "Addressed all comments + take another look 是请求复审的固定说法。"),
    ],
    4: [
        ("会议上想插一句话，最自然的是：",
         ["Can I jump in here for a second?",
          "Can I jump this meeting?",
          "May I jump the words?",
          "Let me jump into you."], 0,
         "jump in 表示插入讨论，非常口语自然。"),
        ("委婉表达不同意见：",
         ["I see it a bit differently. My concern is the timeline.",
          "You are wrong. The timeline is bad.",
          "I see you differently. Timeline!",
          "My opinion differs from yours strongly."], 0,
         "I see it a bit differently 软化语气，对事不对人。"),
        ("故意唱个反调检查方案漏洞，先声明：",
         ["Just to play devil's advocate — what if the vendor raises prices?",
          "Let me play the devil — prices up?",
          "I will be a devil about prices.",
          "Devil says: prices up next year."], 0,
         "play devil's advocate 表示「唱反调」，避免显得针对个人。"),
        ("讨论陷入细节，提议会后单聊：",
         ["Let's take this offline — this is getting into the weeds.",
          "Let's take this to offline-land, weeds are here.",
          "Go offline with the weeds, please.",
          "This weed is offline, discuss later."], 0,
         "take it offline + into the weeds 都是会议高频表达。"),
        ("会议收尾做总结，用：",
         ["To sum up: we'll go with option B, and revisit the timeline on Friday.",
          "Summing all: B option we go, Friday timeline we see.",
          "In sum-up of B, Friday revisits us.",
          "To summary, B is going on Friday."], 0,
         "To sum up + go with + revisit 是会议收尾三件套。"),
    ],
    5: [
        ("演示开场，告诉大家你会带大家看新报表：",
         ["Today I'll walk you through the new reporting dashboard.",
          "Today I walk you and the dashboard reports.",
          "Today the dashboard walks you.",
          "I will show-walk the report dashboard."], 0,
         "walk you through 是演示开场标准句。"),
        ("用类比向非技术同事解释消息队列：",
         ["Think of it like a post office: the queue holds letters until recipients pick them up.",
          "The queue is a post office that thinks.",
          "Queues are letters mailed to offices.",
          "Imagine the queue being postal."], 0,
         "Think of it like... 是万能类比开头。"),
        ("演示中页面卡了，请听众稍等：",
         ["Looks like staging is a bit slow today — bear with me for a second.",
          "Staging is slow, bear on me a second.",
          "The staging bear is slow today.",
          "Wait here while staging suffers."], 0,
         "bear with me = 请稍等/包容，注意不是 bare。"),
        ("把技术改进翻译成业务价值：",
         ["What that means for the business is faster releases and fewer outages.",
          "The business means faster releases outaging less.",
          "Businessly, releases are faster and outages fewer.",
          "The business will mean outage fast releases."], 0,
         "What that means for... 是「翻译成业务价值」的固定句式。"),
        ("Q&A 被问到没准备的问题，得体的回应是：",
         ["That's a great question — I don't have exact numbers, but I'll follow up by email.",
          "I don't know. Next question, please.",
          "That question is not in my slides.",
          "Ask me anything easier, please."], 0,
         "承认不知道 + 给出跟进承诺，比硬编答案专业得多。"),
    ],
    6: [
        ("周一早上和同事寒暄，最自然的开场：",
         ["Morning! How was your weekend?",
          "Morning! How was your weekend going?",
          "Hello, weekend was what?",
          "Good Monday, did you weekend?"], 0,
         "How was your weekend? 是周一万能开场。"),
        ("同事问你周末干嘛了，你休息补觉去了：",
         ["I mostly took it easy — caught up on some sleep.",
          "I took easy and caught my sleep up totally.",
          "I was easy, sleeping caught me.",
          "My sleep was caught up by me easily."], 0,
         "take it easy + catch up on sleep 都是地道口语。"),
        ("朋友说要去一家你想去没去过的店：",
         ["No way! I've been meaning to try that place!",
          "No way! I am meaning that place to try!",
          "No road! That place means to me!",
          "No method! I mean trying there!"], 0,
         "No way! 表示惊讶「不会吧」；have been meaning to 表示一直想做。"),
        ("电梯里碰见想深聊的同事，要走了想留个后续：",
         ["Let's grab a coffee sometime next week and catch up properly.",
          "Let's coffee grab next week for proper catching.",
          "Coffee will be grabbed by us next week.",
          "Next week coffee catches us properly."], 0,
         "grab a coffee + catch up 是收尾留后续的标配。"),
        ("结束闲聊时表达「很高兴碰到你」：",
         ["Great running into you!", "Great run into you!", "Running into you greatly!", "The run into you is great!"], 0,
         "great running into you 是偶遇道别的固定表达。"),
    ],
    7: [
        ("周会汇报本周亮点，用：",
         ["The highlight of the week was getting the search feature into production.",
          "The high light of week was search produced.",
          "This week's light was high: search in production.",
          "The week highlighted my production search."], 0,
         "the highlight of the week 是周报亮点句。"),
        ("说明进度正常，用：",
         ["We're currently at 90% completion, and we're on track to finish by Friday.",
          "We are 90% done and on the track until Friday.",
          "Our completion is 90%, tracking Friday well.",
          "90% finished, the track is Friday."], 0,
         "on track to do 表示进度正常、有望按时。"),
        ("retro 里说「做得好的地方」，用：",
         ["What went well: the pairing sessions really sped things up.",
          "What goed well: pairing speeds.",
          "The well things went to pairing.",
          "Good went what: pairing sped."], 0,
         "What went well 是回顾会第一问的标准句式。"),
        ("认领一个行动项，用：",
         ["My action item is to document the deployment process by Wednesday.",
          "My action item documents deployment Wednesday-ly.",
          "The action item of me is documenting Wednesday.",
          "I action the item: document deployment by Wednesday."], 0,
         "action item 是回顾会认领任务的固定说法。"),
        ("提前预警上线风险，用：",
         ["One risk to flag: if the load test surfaces issues, we may need to push the launch.",
          "One risk to wave: load test issues push the launch.",
          "A flag of risk: the launch tests loading issues.",
          "Risk flagged: launch may push the test."], 0,
         "flag a risk 表示「提出风险」，push the launch 表示推迟上线。"),
    ],
}

# ---------------- 注入内容 ----------------

CSS = """<!--DAY-ENHANCE-CSS--><style>
  .phrase { background: #eff6ff; border-bottom: 2px dotted #2563eb; cursor: pointer; border-radius: 3px; padding: 0 2px; }
  .phrase:hover { background: #dbeafe; }
  #phrasePop { position: absolute; display: none; z-index: 99; background: #1e293b; color: #fff;
    border-radius: 10px; padding: 10px 14px; font-size: 13px; max-width: 300px; box-shadow: 0 8px 20px rgba(0,0,0,.25); }
  #phrasePop .p-en { font-weight: 700; color: #93c5fd; margin-bottom: 2px; }
  #phrasePop .p-voice { background: #334155; border: none; color: #fff; border-radius: 50%; width: 26px; height: 26px; cursor: pointer; margin-top: 6px; }
  .dlg-audio { display: inline-flex; gap: 8px; margin-left: 10px; }
  .dlg-audio button { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 999px;
    padding: 3px 12px; font-size: 12px; cursor: pointer; font-family: inherit; }
  .dlg-audio button:hover { background: #dbeafe; }
  .dlg-audio button.playing { background: #1d4ed8; color: #fff; }
  .line { position: relative; }
  .line .line-voice { background: none; border: none; cursor: pointer; font-size: 12px; padding: 0 4px; opacity: .55; }
  .line .line-voice:hover { opacity: 1; }
  .line.speaking .en { background: #fef3c7 !important; }
  .shadow-tip { font-size: 12px; color: #b45309; background: #fffbeb; border-radius: 6px; padding: 2px 8px; display: none; margin-left: 8px; }
  .quiz-q { border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; margin: 12px 0; background: #fff; }
  .quiz-q .q-title { font-size: 15px; font-weight: 600; margin-bottom: 10px; }
  .quiz-q label { display: block; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px; margin: 6px 0;
    cursor: pointer; font-size: 14px; }
  .quiz-q label:hover { border-color: var(--primary); }
  .quiz-q label.correct { background: #ecfdf5; border-color: #a7f3d0; color: #047857; }
  .quiz-q label.wrong { background: #fef2f2; border-color: #fecaca; color: #b91c1c; }
  .quiz-q label.disabled { cursor: default; opacity: .75; }
  .quiz-q .explain { display: none; margin-top: 8px; font-size: 13px; color: var(--muted); background: #f8fafc; border-radius: 6px; padding: 6px 10px; }
  .quiz-q.done .explain { display: block; }
  .quiz-score { font-size: 15px; font-weight: 600; color: var(--primary-dark); margin-top: 8px; }
</style><!--/DAY-ENHANCE-CSS-->"""

JS_TEMPLATE = r"""<!--DAY-ENHANCE-JS--><script>
var DAY_PHRASES = __PHRASES__;
var DAY_QUIZ = __QUIZ__;
var DAY_NO = __DAY__;

/* ---------- 语音（与词汇页共用偏好） ---------- */
var __voice = null;
function resolveVoice() {
  var vs = window.speechSynthesis.getVoices() || [];
  var saved = '';
  try { saved = localStorage.getItem('ielts-voice') || ''; } catch (e) {}
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
function speakText(text, onend) {
  if (!('speechSynthesis' in window)) return;
  var synth = window.speechSynthesis;
  synth.cancel();
  if (!__voice) {
    __voice = resolveVoice();
    synth.onvoiceschanged = function () { __voice = resolveVoice(); };
  }
  var u = new SpeechSynthesisUtterance(text);
  u.lang = 'en-US';
  u.rate = 0.9;
  if (__voice) u.voice = __voice;
  if (onend) u.onend = onend;
  synth.speak(u);
}

/* ---------- 对话音频 + 跟读 ---------- */
var playState = null; /* {dialog, lines, idx, shadow, timer} */

function collectLines(dialog) {
  return Array.prototype.map.call(dialog.querySelectorAll('.line'), function (line) {
    return { el: line, text: (line.querySelector('.en') || {}).textContent || '' };
  }).filter(function (l) { return l.text.trim(); });
}

function stopPlayback() {
  if (!playState) return;
  if (playState.timer) clearTimeout(playState.timer);
  window.speechSynthesis.cancel();
  playState.lines.forEach(function (l) {
    l.el.classList.remove('speaking');
    var b = l.el.querySelector('.line-voice');
    if (b) b.textContent = '🔊';
  });
  var btns = playState.dialog.querySelectorAll('.dlg-audio button');
  btns.forEach(function (b) { b.classList.remove('playing'); });
  var tip = playState.dialog.querySelector('.shadow-tip');
  if (tip) tip.style.display = 'none';
  playState = null;
}

function playFrom(dialog, startIdx, shadow) {
  stopPlayback();
  playState = { dialog: dialog, lines: collectLines(dialog), idx: startIdx, shadow: shadow, timer: null };
  var btns = dialog.querySelectorAll('.dlg-audio button');
  if (btns[shadow ? 1 : 0]) btns[shadow ? 1 : 0].classList.add('playing');
  var tip = dialog.querySelector('.shadow-tip');
  if (shadow && tip) tip.style.display = '';
  playNextLine();
}

function playNextLine() {
  if (!playState) return;
  var s = playState;
  if (s.idx >= s.lines.length) { stopPlayback(); return; }
  var line = s.lines[s.idx];
  line.el.classList.add('speaking');
  var vb = line.el.querySelector('.line-voice');
  if (vb) vb.textContent = '🔈';
  line.el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  speakText(line.text, function () {
    if (!playState) return;
    if (vb) vb.textContent = '🔊';
    var wait = s.shadow ? 4000 : 350;
    s.timer = setTimeout(function () {
      if (!playState) return;
      line.el.classList.remove('speaking');
      s.idx++;
      playNextLine();
    }, wait);
  });
}

function togglePlay(dialog, shadow, btn) {
  if (playState && playState.dialog === dialog && playState.shadow === shadow) { stopPlayback(); return; }
  playFrom(dialog, 0, shadow);
}

function injectAudio() {
  document.querySelectorAll('.dialog').forEach(function (dialog, di) {
    var h3 = dialog.querySelector('h3');
    if (!h3) return;
    var wrap = document.createElement('span');
    wrap.className = 'dlg-audio';
    wrap.innerHTML =
      '<button onclick="togglePlay(this.closest(\'.dialog\'), false, this)">▶️ 播放对话</button>' +
      '<button onclick="togglePlay(this.closest(\'.dialog\'), true, this)">🎧 跟读模式</button>' +
      '<span class="shadow-tip">跟读中：每句读完请大声复述</span>';
    h3.appendChild(wrap);
    dialog.querySelectorAll('.line').forEach(function (line) {
      var en = line.querySelector('.en');
      if (!en) return;
      var b = document.createElement('button');
      b.className = 'line-voice';
      b.textContent = '🔊';
      b.title = '播放这句';
      b.onclick = function () {
        var wasPlaying = playState && playState.dialog === dialog;
        stopPlayback();
        if (wasPlaying) return;
        line.classList.add('speaking');
        b.textContent = '🔈';
        speakText(en.textContent, function () {
          line.classList.remove('speaking');
          b.textContent = '🔊';
        });
      };
      en.appendChild(b);
    });
  });
}

/* ---------- 短语高亮 + 释义气泡 ---------- */
var DAY_PHRASES_DICT = {};
function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
function highlightPhrases() {
  var phrases = DAY_PHRASES.map(function (p) { return p[0]; });
  phrases.sort(function (a, b) { return b.length - a.length; });
  DAY_PHRASES.forEach(function (p) { DAY_PHRASES_DICT[p[0].toLowerCase()] = p[1]; });
  document.querySelectorAll('.dialog .line .en, .sent .en').forEach(function (el) {
    var html = el.innerHTML;
    if (html.indexOf('class="phrase"') !== -1) return;
    phrases.forEach(function (phrase) {
      if (html.indexOf('class="phrase"') !== -1) return;
      var re = new RegExp(escapeRegExp(phrase).replace(/ /g, '(?:\\s|&nbsp;)+'), 'gi');
      html = html.replace(re, function (m) {
        return '<span class="phrase" data-ph="' + phrase.toLowerCase() + '">' + m + '</span>';
      });
    });
    el.innerHTML = html;
  });
}

function setupPhrasePop() {
  var pop = document.createElement('div');
  pop.id = 'phrasePop';
  document.body.appendChild(pop);
  document.addEventListener('click', function (e) {
    var voiceBtn = e.target.closest('.p-voice');
    if (voiceBtn) {
      speakText(voiceBtn.getAttribute('data-say'));
      e.stopPropagation();
      return;
    }
    var ph = e.target.closest('.phrase');
    if (ph) {
      var key = ph.getAttribute('data-ph');
      pop.innerHTML = '<div class="p-en">' + key + '</div><div>' + (DAY_PHRASES_DICT[key] || '') + '</div>' +
        '<button class="p-voice" data-say="' + key + '">🔊</button>';
      var r = ph.getBoundingClientRect();
      pop.style.display = 'block';
      var top = r.bottom + window.scrollY + 8;
      var left = Math.min(r.left + window.scrollX, window.scrollX + window.innerWidth - 320);
      pop.style.top = top + 'px';
      pop.style.left = Math.max(8, left) + 'px';
      e.stopPropagation();
      return;
    }
    pop.style.display = 'none';
  });
}

/* ---------- 课后小练习 ---------- */
function renderQuiz() {
  var host = document.getElementById('dayQuiz');
  if (!host) return;
  var items = DAY_QUIZ;
  var html = '';
  items.forEach(function (q, qi) {
    html += '<div class="quiz-q" data-answer="' + q[2] + '"><div class="q-title">' + (qi + 1) + '. ' + q[0] + '</div>';
    q[1].forEach(function (opt, oi) {
      html += '<label data-oi="' + oi + '"><input type="radio" name="q' + qi + '" style="margin-right:8px" onclick="answerQuiz(this)">' + opt + '</label>';
    });
    html += '<div class="explain">💡 ' + q[3] + '</div></div>';
  });
  html += '<div class="quiz-score" id="quizScore"></div><button class="btn ghost" onclick="renderQuiz()" style="margin-top:10px">🔄 重做</button>';
  host.innerHTML = html;
}

function answerQuiz(input) {
  var qdiv = input.closest('.quiz-q');
  if (qdiv.classList.contains('done')) return;
  qdiv.classList.add('done');
  var answer = parseInt(qdiv.getAttribute('data-answer'), 10);
  qdiv.querySelectorAll('label').forEach(function (label) {
    var oi = parseInt(label.getAttribute('data-oi'), 10);
    label.classList.add('disabled');
    if (oi === answer) label.classList.add('correct');
    else if (label.querySelector('input').checked) label.classList.add('wrong');
  });
  var done = document.querySelectorAll('.quiz-q.done').length;
  var right = 0;
  document.querySelectorAll('.quiz-q').forEach(function (q) {
    if (q.classList.contains('done') && q.querySelector('label.correct input').checked) right++;
  });
  document.getElementById('quizScore').textContent = '已完成 ' + done + '/' + DAY_QUIZ.length + ' 题 · 答对 ' + right + ' 题';
}

document.addEventListener('DOMContentLoaded', function () {
  injectAudio();
  highlightPhrases();
  setupPhrasePop();
  renderQuiz();
});
</script><!--/DAY-ENHANCE-JS-->"""


def wrap_phrases(html: str, day: int) -> str:
    """在对话与句型卡的英文文本中包裹重点短语。"""
    phrases = sorted(PHRASES[day], key=lambda p: -len(p[0]))
    # 只处理 .dialog .line .en 与 .sent .en 的内容
    zones = re.split(r'(?=<div class="(?:line|sent)"|<h2 class="section")', html)
    phrase_res = []
    for phrase, _def in phrases:
        pattern_src = re.escape(phrase).replace('\\ ', ' ').replace(' ', r'(?:\s|&nbsp;)+')
        pattern = re.compile(r'\b(?:' + pattern_src + r')\b', re.I)
        phrase_res.append((phrase, pattern))
    out = []
    for zone in zones:
        if '<div class="line"' in zone or '<div class="sent"' in zone:
            for phrase, pattern in phrase_res:
                def repl(m):
                    return '<span class="phrase" data-ph="' + phrase.lower() + '">' + m.group(0) + '</span>'
                # 避免重复包裹与嵌套
                if 'class="phrase"' in zone and phrase.lower() in zone:
                    continue
                zone = pattern.sub(repl, zone, count=2)
        out.append(zone)
    return "".join(out)


def main() -> None:
    for day in range(1, 8):
        path = DIR / f"day{day}.html"
        content = path.read_text(encoding="utf-8")

        # 幂等清理
        content = re.sub(r"<!--DAY-ENHANCE-CSS-->.*?<!--/DAY-ENHANCE-CSS-->\n?", "", content, flags=re.S)
        content = re.sub(r"<!--DAY-ENHANCE-JS-->.*?<!--/DAY-ENHANCE-JS-->\n?", "", content, flags=re.S)

        # 短语高亮（静态）
        content = wrap_phrases(content, day)

        # 注入 CSS / JS / 测验板块
        quiz_html = '<h2 class="section">📝 课后小练习</h2><div class="card" id="dayQuiz"></div>'
        js = (JS_TEMPLATE
              .replace("__PHRASES__", json_dumps(PHRASES[day]))
              .replace("__QUIZ__", json_dumps(QUIZ[day]))
              .replace("__DAY__", str(day)))
        content = content.replace("</head>", CSS + "\n</head>", 1)
        content = content.replace('<nav class="bottom">', quiz_html + '\n  <nav class="bottom">', 1)
        content = content.replace("</body>", js + "\n</body>", 1)

        path.write_text(content, encoding="utf-8")
        n = content.count('class="phrase"')
        print(f"day{day}.html: 高亮短语 {n} 处 · 测验 {len(QUIZ[day])} 题 ✓")
    print("全部完成")


def json_dumps(data) -> str:
    import json
    return json.dumps(data, ensure_ascii=False)


if __name__ == "__main__":
    main()
