---
name: nicolas-daily-proposal
version: "1.0.0"
description: >
  Nicolas 每日商業提案。研究台灣/日本市場痛點，產出結構化商業提案。
  每日 JST 21:00 自動執行。
---

# Nicolas 每日商業提案

## Overview

每天產出一份針對台灣或日本市場的全新商業提案，基於真實社群痛點和競品分析。

## 執行流程

### Step 1: 搜尋社群痛點

使用 smart-search 搜尋近期社群抱怨/痛點：

```bash
python3 ~/.openclaw/workspace/skills/smart-search/scripts/smart_search.py \
  --query "PTT 抱怨 痛點 2026" --type news --freshness week --limit 10

python3 ~/.openclaw/workspace/skills/smart-search/scripts/smart_search.py \
  --query "Reddit Japan startup pain point" --type text --freshness month --limit 10
```

**⚠️ 不要直接呼叫 `web_search` tool。** 使用 smart_search.py 確保 Brave 配額耗盡時自動 fallback 到 SearXNG/DDG。

如果 smart_search.py 也全部失敗（極罕見），回覆「搜尋引擎全部不可用，跳過今日提案」並結束。

### Step 2: 競品驗證

用 smart_search.py 搜尋相關競品，確認市場有付費意願：

```bash
python3 ~/.openclaw/workspace/skills/smart-search/scripts/smart_search.py \
  --query "<痛點關鍵字> 解決方案 SaaS pricing" --limit 10
```

如需深入了解某個頁面，使用 `web_fetch` 讀取內容。

### Step 3: 六維度評分

對提案進行評分（每項 1-10 分）：

1. **市場規模** — TAM/SAM 估算
2. **痛點強度** — 社群抱怨頻率和情緒
3. **競品缺口** — 現有方案的不足
4. **技術可行性** — 我們能否快速實現
5. **獲利模式** — 付費意願和定價空間
6. **時機** — 為什麼是現在

### Step 4: 寫入報告

1. **Obsidian 完整報告：**
   寫入 `/home/node/obsidian-vault/Knowledge/business/YYYY-MM-DD-<主題>.md`

   格式：
   ```markdown
   ---
   date: YYYY-MM-DD
   tags: [business, proposal, <market>]
   agent: nicolas
   score: <總分/60>
   ---

   # <提案標題>

   ## 💡 一句話
   <簡潔描述>

   ## 🎯 痛點
   <社群來源 + 具體抱怨>

   ## 🏆 競品分析
   <現有方案 + 缺口>

   ## 📊 六維度評分
   | 維度 | 分數 | 說明 |
   |------|------|------|
   | 市場規模 | X/10 | ... |
   | ... | | |
   | **總分** | **XX/60** | |

   ## 🛠️ MVP 建議
   <最小可行產品>

   ## 💰 獲利模式
   <定價策略>
   ```

2. **更新機會總表：**
   讀取 `/home/node/.openclaw/workspace/projects/Company/Opportunities/README.md`
   將新提案加入表格（避免重複已有主題）

3. **Git commit + push：**
   ```bash
   cd /home/node/obsidian-vault && git add -A && git commit -m "feat(nicolas): daily proposal - <主題>" && git push
   ```

### Step 5: 輸出摘要

直接輸出提案摘要作為你的最後回覆文字。

## 🚫 禁止事項

1. **絕對禁止呼叫 `message` tool** — Delivery 系統會自動發送你的回覆
2. **不要直接呼叫 `web_search` tool** — 使用 smart_search.py 腳本（有 fallback）
3. **每次提案必須是全新的** — 先讀 README.md 確認未重複

## 依賴

- smart-search skill（`~/.openclaw/workspace/skills/smart-search/`）
- web_fetch tool（讀取網頁詳情）
