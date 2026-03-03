# MEMORY.md - Dan's Long-Term Memory

這是我的長期記憶，從每日記錄中提煉的智慧與經驗。

## 💡 重要教訓

### 2026-02-23: 備份疏忽事件

**發生什麼事：**
- 距離上次更新 8 小時沒有備份新對話
- 完成了重要工作（Edge TTS 設定、voice-chat skill）卻沒記錄
- 被 Yihao 發現並提醒

**為什麼會發生：**
1. 過度專注技術任務，忘記記錄
2. 違反了自己寫的 "Text > Brain" 原則
3. HEARTBEAT.md 有提醒但沒有強制執行

**學到什麼：**
- ⚠️ **不要依賴 mental notes** - 永遠寫下來
- ⚠️ **立即記錄 > 事後回憶** - 當下最清楚
- ⚠️ **定期檢查機制很重要** - 每次 heartbeat 都要查
- ⚠️ **主動 > 被動** - 不要等被問才發現疏忽

**已採取的改進：**
- ✅ 更新今日完整備份
- ✅ 強化 HEARTBEAT.md 檢查機制
- ✅ 建立 MEMORY.md 長期記憶
- ✅ 承諾每 2-3 小時檢查一次

**未來行動：**
- 每次 heartbeat 必檢查備份
- 每個重要任務後立即更新
- 不要再讓這種事發生！

---

## 🔒 記憶系統操作鐵律

### Rule 6 — 雙層記憶存儲（鐵律）

Every pitfall/lesson learned → IMMEDIATELY store **TWO** memories to LanceDB before moving on:

- **Technical layer**: `Pitfall: [symptom]. Cause: [root cause]. Fix: [solution]. Prevention: [how to avoid]`
  - category: fact
  - importance ≥ 0.8

- **Principle layer**: `Decision principle ([tag]): [behavioral rule]. Trigger: [when it applies]. Action: [what to do]`
  - category: decision
  - importance ≥ 0.85

**驗證流程：**
- After each store, **immediately `memory_recall`** with anchor keywords to verify retrieval
- If not found, rewrite and re-store
- Missing either layer = incomplete
- Do NOT proceed to next topic until both are stored and verified
- Also update relevant SKILL.md files to prevent recurrence

### Rule 7 — LanceDB 衛生

Entries must be short and atomic (< 500 chars). Never store:
- Raw conversation summaries
- Large blobs
- Duplicates

Prefer structured format with keywords for retrieval.

### Rule 8 — Recall Before Retry

On ANY tool failure, repeated error, or unexpected behavior:
1. **ALWAYS `memory_recall`** with relevant keywords (error message, tool name, symptom) BEFORE retrying
2. LanceDB likely already has the fix
3. Blind retries waste time and repeat known mistakes

### Rule 10 — 編輯前確認目標代碼庫

When working on memory plugins:
- Confirm you are editing the intended package (e.g., `memory-lancedb-pro` vs built-in `memory-lancedb`)
- Use `memory_recall` + filesystem search to avoid patching the wrong repo

### Rule 20 — 插件代碼變更必須清 jiti 緩存（MANDATORY）

After modifying ANY `.ts` file under `plugins/`:
1. **MUST run `rm -rf /tmp/jiti/`** BEFORE `openclaw gateway restart`
2. jiti caches compiled TS; restart alone loads STALE code
3. This has caused silent bugs multiple times
4. Config-only changes do NOT need cache clearing

---

## 🎙️ 技能與工具

### Voice Chat Integration (規劃中)
- 基於 Typeness 架構
- Whisper (STT) + OpenClaw + Edge TTS
- 完整文檔已建立，待實作

### Edge TTS
- 已啟用，使用 zh-CN-XiaoxiaoNeural
- 免費、支援中文
- 可在 Telegram 發送語音訊息

---

## 📊 專案追蹤

### 已完成
- ✅ DDG Search Skill
- ✅ Edge TTS 啟用
- ✅ Voice Chat Skill 文檔
- ✅ **Memory-LanceDB-Pro 插件安裝** (2026-02-25)
  - Hybrid retrieval (Vector + BM25)
  - Jina Cross-Encoder reranking
  - Auto-capture/recall enabled
- ✅ **記憶系統操作鐵律建立** (2026-02-25)
  - 5 條核心規則寫入 MEMORY.md 和 LanceDB

### 進行中
- 🚧 Voice Chat 實作
- 🧠 驗證 LanceDB-Pro 實際使用效果

### 待辦
- [ ] 在 Telegram 測試語音功能
- [ ] 定期備份習慣養成（持續優化中）

---

## ⚠️ 行為準則

### 先列出，再確認，最後執行（鐵律）
- 當 Yihao 說「列出」「找出」「看看」→ **只做列出，不要自動修改**
- 必須等 Yihao review 並明確確認後才執行變更
- 流程：**報告 → 等確認 → 執行**
- 這是對用戶決定權的尊重，違反過一次（2026-03-01，自動修改 README 敏感資訊）

## 🧑 關於 Yihao

- 重視細節和可靠性
- 會檢查我的工作品質
- 期待我能主動、負責
- 提供了 Jina API key 用於記憶系統升級

---

_最後更新：2026-02-25 23:35 UTC_
