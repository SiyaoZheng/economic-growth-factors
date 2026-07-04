# Git 自动版本管理

本项目使用本地自动快照来保护论文写作和数据分析过程中的增量成果。

## 运行方式

macOS `launchd` 每 15 分钟运行一次：

```bash
python3 scripts/auto_git_snapshot.py
```

脚本只在工作区存在真实 Git 改动时提交。推送功能已关闭（local-only），不会上传任何数据到远端。

提交信息格式：

```text
autosnapshot: YYYY-MM-DD HH:MM
```

## 安全规则

自动快照会在以下情况下停止，不会提交：

- 当前分支处于 detached HEAD。
- 存在 merge conflict。
- 远端分支领先本地分支。
- 已经存在手动暂存的改动，避免覆盖人工 staging。
- 将要提交 `data/raw/`、`data/interim/`、`data/processed/` 中的生成数据。
- 将要提交 `.env`、私钥、证书等敏感文件名。
- 单个待提交文件超过 50 MB。
- 小型文本文件中出现明显 secret token 标记。

## 日志

自动化日志写入 Git 目录，不纳入版本库：

```bash
tail -n 20 .git/autosnapshot/events.jsonl
tail -n 50 .git/autosnapshot/launchd.err.log
```

## 手动运行

```bash
python3 scripts/auto_git_snapshot.py
```

只提交但不推送（默认 state）：

```bash
AUTOGIT_PUSH=0 python3 scripts/auto_git_snapshot.py
```

临时调整最大文件大小：

```bash
AUTOGIT_MAX_FILE_MB=100 python3 scripts/auto_git_snapshot.py
```

## 启停自动化

查看状态：

```bash
launchctl print gui/$(id -u)/com.siyaozheng.economic-growth-factors.git-autosnapshot
```

停用：

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.siyaozheng.economic-growth-factors.git-autosnapshot.plist
```

启用：

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.siyaozheng.economic-growth-factors.git-autosnapshot.plist
launchctl enable gui/$(id -u)/com.siyaozheng.economic-growth-factors.git-autosnapshot
```
