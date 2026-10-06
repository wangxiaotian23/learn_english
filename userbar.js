/* 顶部用户登录条：所有根目录页面共用，依赖 <div id="userBar"> */
(function () {
  var bar = document.getElementById('userBar');
  if (!bar) return;

  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  }

  function renderLoggedOut() {
    bar.innerHTML =
      '<span>登录后学习进度按账号保存</span>'
      + '<a class="login-link main" href="login.html">登 录</a>'
      + '<a class="login-link" href="login.html">注 册</a>';
  }

  function renderLoggedIn(email) {
    bar.innerHTML =
      '<span>👋 你好，<b>' + esc(email) + '</b>（学习进度与测验成绩已按账号保存）</span>'
      + '<button class="ghost" onclick="doLogout()">退出</button>';
  }

  window.doLogout = function () {
    fetch('/api/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: '{}'
    }).then(renderLoggedOut).catch(renderLoggedOut);
  };

  fetch('/api/me', { credentials: 'same-origin' })
    .then(function (r) { return r.json(); })
    .then(function (j) {
      if (j && j.ok) renderLoggedIn(j.email);
      else renderLoggedOut();
    })
    .catch(renderLoggedOut);

  /* 今日访问人数（同一浏览器每天只计一次；后端未启动时隐藏） */
  var stat = document.getElementById('visitStat');
  if (stat) {
    fetch('/api/visit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: '{}'
    }).then(function (r) { return r.json(); })
      .then(function (j) {
        if (j && j.ok && j.today > 0) {
          stat.textContent = '👀 今日访问 ' + j.today + ' 人';
        }
      })
      .catch(function () {});
  }
})();
