#!/bin/bash
# Daily RSS Digest Generator
# Runs at 6 AM JST (UTC+9)

set -e

WORKSPACE="/home/node/.openclaw/workspace"
SUBSCRIPTIONS="$WORKSPACE/subscriptions.opml"
LOG_FILE="$WORKSPACE/memory/rss-digest-$(date +%Y-%m-%d).md"

# Create memory directory if it doesn't exist
mkdir -p "$WORKSPACE/memory"

# Spawn subagent to generate digest
openclaw sessions spawn \
  --task "你是一个RSS摘要助手。任务：
1. 读取文件 $SUBSCRIPTIONS
2. 从这个OPML订阅列表中提取所有RSS feed URLs
3. 尝试抓取最近的内容（从各个feed获取最新文章标题和摘要）
4. 分析内容并筛选出以下几类你认为Yihao可能感兴趣的内容：
   - AI/机器学习相关
   - 系统设计/编程相关
   - 技术新闻
   - 安全相关
   - 其他值得注意的内容
5. 生成一个格式清晰的每日摘要，包括：
   - 各类别的热点文章（3-5条最重要的）
   - 简短的摘要（中英文混合，偏向中文）
   - 原始链接

要求：
- 尽可能多地抓取真实内容
- 如果某个feed无法访问，继续处理其他的
- 生成的摘要要有判断力，不要列出所有内容，只要精选的
- 格式美观，适合发送到Telegram群组" \
  --label "Daily RSS Digest $(date +%Y-%m-%d)" \
  --mode run
