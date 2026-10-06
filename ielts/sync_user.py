#!/usr/bin/env python3
"""向 10 个词汇页注入登录态感知与「已掌握」进度同步（幂等）。"""
import re
from pathlib import Path

DIR = Path(__file__).parent
FILES = [f"ielts_part{n}{s}.html" for n in range(1, 6) for s in "ab"]

SYNC_JS = """<!--USER-SYNC--><script>
(function () {
  function api(path, body) {
    return fetch(path, {
      method: body ? 'POST' : 'GET',
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      credentials: 'same-origin',
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) { return r.json(); });
  }

  /* 登录时：服务端进度 ∪ 本地进度，合并渲染 */
  api('/api/me').then(function (me) {
    if (!me.ok) return null;
    return api('/api/progress');
  }).then(function (j) {
    if (!j || !j.ok) return;
    var server = new Set(j.mastered);
    var local = getSet();
    var changed = false;
    local.forEach(function (wid) {
      if (!server.has(wid)) { server.add(wid); changed = true; }
    });
    server.forEach(function (wid) { setRowMastered(wid, true); });
    renderProg();
    if (changed) {
      api('/api/progress', { add: Array.from(local) });
    }
  }).catch(function () {});

  /* 勾选/取消勾选时同步到服务端（静默降级） */
  var origToggle = window.toggleMaster;
  window.toggleMaster = function (wid) {
    origToggle(wid);
    var add = getSet().has(wid);
    api('/api/progress', add ? { add: [wid] } : { remove: [wid] }).catch(function () {});
  };
})();
</script><!--/USER-SYNC-->"""


def main() -> None:
    for name in FILES:
        path = DIR / name
        content = path.read_text(encoding="utf-8")
        content = re.sub(r"<!--USER-SYNC-->.*?<!--/USER-SYNC-->\n?", "", content, flags=re.S)
        assert "</body>" in content
        content = content.replace("</body>", SYNC_JS + "\n</body>", 1)
        path.write_text(content, encoding="utf-8")
        print(f"{name}: 进度同步已注入 ✓")
    print("全部完成")


if __name__ == "__main__":
    main()
