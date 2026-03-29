# SOP: 每日新聞 Podcast（AI 每日新聞）

- **負責人:** April (agent) + Dan (監控)
- **頻率:** 每日 JST 13:00
- **Cron Job ID:** `71c85d19-ff69-409f-b03d-9d7bed7c8268`

## 流程

### 1. 新聞蒐集
- Brave Search API 搜尋當日頭條（科技 + 時事）
- Fallback: SearXNG（當 Brave 配額耗盡）

### 2. 稿件撰寫
- 整理為口語化播報稿（中文）
- 存入 `projects/daily-world-news/summaries/YYYY-MM-DD.md`

### 3. 語音生成
- ElevenLabs TTS 生成 MP3
- 存入 `projects/daily-world-news/audio/YYYY-MM-DD.mp3`

### 4. 上傳 R2
- 腳本: `scripts/upload-r2.sh`
- Object key: `podcasts/YYYY-MM-DD.mp3`
- Bucket: `ai-podcast`

### 5. 更新 RSS Feed
- 腳本: `scripts/generate-rss.py`
- 自動加入新 episode 並上傳 `feed.xml`
- RSS URL: `https://pub-1bc6fb66c5ba4be1b405c18499c18bb0.r2.dev/feed.xml`

### 6. 通知
- 發送至 Telegram「資訊新知」頻道（topic 36）
- 含摘要文字 + 語音檔

## 平台

- **Spotify:** https://open.spotify.com/show/2a2av2AeMwZ7XXFcXdw2Od ✅
- **Apple Podcasts:** 審核中（2026-03-29 提交）

## 故障排除

- Brave API 配額耗盡 → 自動 fallback SearXNG
- ffmpeg 未安裝 → `apt install ffmpeg`
- R2 上傳失敗 → 檢查 API token 是否過期
