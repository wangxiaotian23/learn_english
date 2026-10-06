# learn_english

个人英语学习站点:「英语学习中心」门户 + 两大学习模块 —— 「IT 职场英语口语一周教程」和「雅思核心 3000 词」,支持登录注册、按用户隔离的学习进度与测验成绩云同步。

## 功能

### 门户首页
- [index.html](index.html) 为学习中心首页,两张卡片分别进入 IT 职场口语与雅思词汇模块。
- [userbar.js](userbar.js) 提供全站共用的顶部登录条:未登录显示登录/注册入口,登录后显示账号与退出按钮。

### IT 职场英语口语一周教程
- 入口 [it.html](it.html),[day1.html](day1.html) ~ [day7.html](day7.html) 对应周一到周日,覆盖每日站会、技术讨论、代码评审、会议、Demo、社交、周会复盘七大职场场景。
- 90+ 个可直接套用的职场句型,多轮双语情景对话,每日 50 个高频 IT 单词。
- day 页面增强:重点短语高亮 + 点击查看释义、对话发音/跟读、每课 5 题随堂小测。

### 雅思核心 3000 词
- 入口 [ielts.html](ielts.html),3000 个高频词按主题分成 5 个 Part,每个 Part 拆为 a/b 两册(每册 300 词),即 [ielts/ielts_part1a.html](ielts/ielts_part1a.html) ~ [ielts/ielts_part5b.html](ielts/ielts_part5b.html)。
- 每个词条带音标、例句与一键发音(数据来自 `ielts/wordlists/` 与 `ielts/sentences/` 下的 JSON)。
- 支持勾选「已掌握」和「刷词自测」(隐藏中文测主动提取),每册进度独立存储在 localStorage。
- [ielts/quiz.html](ielts/quiz.html) 随机 10 词每日一测,错词自动汇总。

### 账号与进度同步(需启动后端)
- [login.html](login.html) 登录/注册页,邮箱 + 密码(PBKDF2 加盐哈希,Flask session 会话)。
- 登录后服务端进度与本地进度自动合并,勾选/取消「已掌握」实时同步到服务端;测验成绩(最近 5 次)按用户保存并回显。
- 纯静态托管(nginx / EdgeOne 等)时页面自动静默降级为仅本地进度。

## 目录结构

```
├── index.html                    # 学习中心门户
├── userbar.js                    # 全站顶部登录条
├── login.html                    # 登录 / 注册页
├── it.html / day1~7.html         # IT 职场英语口语一周教程
├── ielts.html                    # 雅思词汇模块入口
├── ielts/                        # 雅思词汇模块
│   ├── ielts_part1a~5b.html      # 10 册词汇分页
│   ├── quiz.html                 # 随机测验
│   ├── vocab_3000.json           # 3000 词数据
│   ├── wordlists/ sentences/     # 分片词表与例句
│   └── *.py                      # 数据生成/维护脚本(见下)
├── app.py                        # Flask 后端:认证 + 进度/成绩 API + 静态托管
├── users.db                      # SQLite 数据库(自动创建,已被 gitignore)
├── Dockerfile / nginx.conf       # Docker 部署(nginx:alpine + gzip,纯静态)
```

## 本地运行

### 方式一:带后端(支持登录与进度同步)

```bash
pip install flask
python3 app.py
# 打开 http://127.0.0.1:5000
```

首次启动会自动创建 `users.db` 和 `.secret_key`。

### 方式二:纯静态

直接用浏览器打开 `index.html`,或用任意静态服务器托管(如 `python3 -m http.server`)。此时登录/进度同步功能不可用,勾选状态只保存在本地。

### Docker 部署(纯静态)

```bash
docker build -t learn_english .
docker run -d -p 80:80 learn_english
```

注意:Dockerfile 目前未收录 `it.html`、`ielts.html`、`login.html`、`userbar.js` 等新文件,部署前需在 Dockerfile 的 COPY 列表中补充。

## API 一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/register` | 注册(邮箱 + 密码 ≥ 6 位),成功即登录 |
| POST | `/api/login` | 登录 |
| POST | `/api/logout` | 退出登录 |
| GET | `/api/me` | 当前登录用户 |
| GET | `/api/progress` | 获取已掌握单词 id 列表 |
| POST | `/api/progress` | 批量增/删已掌握单词(`{"add": [], "remove": []}`) |
| GET | `/api/quiz/history` | 最近 5 次测验成绩 |
| POST | `/api/quiz/result` | 上报测验成绩(含错题 id) |

## 维护脚本

根目录:
- `enhance_days.py`:增强 day1-7 页面(短语高亮 + 点击释义、对话音频/跟读、课后小练习),幂等。

ielts/:
- `sync_user.py`:向 10 个词汇页注入登录态感知与进度同步 JS(幂等)。
- `fix_storage_keys.py`:修复 a/b 两册共用 localStorage 键导致进度混串的问题,每册独立键并迁移旧数据(幂等)。
- `gen_quiz.py`:生成/更新测验页面。
- `split_parts.py` / `generate_final_5_ielts.py`:拆分与生成分页页面。
- `add_sentences.py`:补全例句数据。
- `fix_nav_links.py` / `fix_voice.py`:批量修复导航链接与发音。
