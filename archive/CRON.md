# CRON.md - 定时任务配置

## 📅 Daily RSS Digest

**Task**: 每天早上6点（日本时间 UTC+9）自动生成RSS摘要并发送到Telegram

**配置**:
- **时间**: 6:00 AM JST (UTC+9) = UTC 21:00 前一天
- **频率**: 每天
- **脚本**: `/home/node/.openclaw/workspace/scripts/daily-rss-digest.sh`
- **订阅源**: `/home/node/.openclaw/workspace/subscriptions.opml`
- **输出**: 发送到 Telegram General (-1003767828002)

**Crontab 条目**:
```
# Daily RSS digest at 6 AM JST (UTC+9)
0 21 * * * TZ='Asia/Tokyo' /home/node/.openclaw/workspace/scripts/daily-rss-digest.sh >> /home/node/.openclaw/workspace/logs/rss-digest.log 2>&1
```

**状态**: 待设置 ⏳

---

## 🧬 Capability Evolver

**Task**: 每 6 小時自動運行一次進化循環，分析歷史記錄並優化 AI。

**配置**:
- **頻率**: 每 6 小時 (`0 */6 * * *`)
- **腳本**: `/Users/yihao.wang/.openclaw/workspace/skills/evolver/index.js`
- **命令**: `node [腳本] run`

**Crontab 條目**:
```
# Capability Evolver evolution cycle every 6 hours
0 */6 * * * /opt/homebrew/opt/node@22/bin/node /Users/yihao.wang/.openclaw/workspace/skills/evolver/index.js run >> /Users/yihao.wang/.openclaw/workspace/logs/evolver.log 2>&1
```

**状态**: 已設置 ✅

---

## 设置步骤

1. 编辑 crontab: `crontab -e`
2. 添加上面的条目
3. 保存并验证: `crontab -l`
4. 检查日志: `tail -f /home/node/.openclaw/workspace/logs/rss-digest.log`

---

_最后更新: 2026-02-23 12:30 UTC_
