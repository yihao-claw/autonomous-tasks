---
name: linear-workflow
description: >
  Linear issue 工作流程管理。所有任務（工程、資訊、維運）都必須遵循此流程。
  Use when: 建立新任務、規劃執行方案、更新任務狀態、完成任務回報、處理返工。
  Also use when: 收到 Human 指派工作、自主發現問題需建 issue、完成工作後需更新 Linear。
  NOT for: 查詢 Linear API 細節（見 linear skill）。
---

# Linear Workflow — 四階段任務管理

> **Linear 是 Source of Truth。**
> 所有資訊（規劃、決策、執行結果）都必須寫回 Linear。
> 任何人只看 Linear 就能完整了解每個 issue 的來龍去脈。

## 流程總覽

```
發想 ──→ 規劃 ──→ 執行 ──→ 完成
Backlog   Todo   In Progress  Done
建 issue  寫計畫  做事+記錄   寫結果
         ↑                    │
         └── 返工 ←───────────┘
```

## 指令速查

```bash
SKILL_DIR="skills/linear"

# 建立 issue
bash $SKILL_DIR/scripts/linear.sh create "標題" "描述" <priority> "<Label>"

# 更新狀態
bash $SKILL_DIR/scripts/linear.sh update YIH-XX state "Todo"
bash $SKILL_DIR/scripts/linear.sh update YIH-XX state "In Progress"
bash $SKILL_DIR/scripts/linear.sh update YIH-XX state "Done"

# 更新 description
bash $SKILL_DIR/scripts/linear.sh update YIH-XX description "完整內容"

# 查詢
bash $SKILL_DIR/scripts/linear.sh list todo
bash $SKILL_DIR/scripts/linear.sh list inprogress
bash $SKILL_DIR/scripts/linear.sh search "關鍵字"
```

Priority: 1=Urgent 2=High 3=Medium 4=Low
Labels: `Horse` / `Dan` / `Bird`

---

## 階段 1：發想（Ideation）

**狀態：** `Backlog`
**觸發：** Human 指派、cron 發現、系統事件、自主識別

**必做：**
1. 建立 Linear issue
2. Description 寫初步描述（最低要求）

**Description 最低內容：**
```markdown
## 問題
一句話描述問題是什麼。

## 動機
為什麼需要做（影響/價值）。
```

---

## 階段 2：規劃（Planning）

**狀態：** `Todo`
**⛔ Gate：沒完成規劃，不能進入執行。**

**必做：**
1. 分析問題根因
2. 設計解決方案
3. 更新 Linear description（用模板）
4. 更新狀態為 `Todo`

**Description 模板：**
```markdown
## 問題描述
- 現狀：（目前怎樣）
- 預期：（應該怎樣）

## 根因分析
- （為什麼會這樣）

## 執行計畫
1. （步驟一）
2. （步驟二）
3. （步驟三）

## 完成標準
- [ ] （具體可驗證的標準）
- [ ] （第二個標準）

## 風險與注意事項
- （可能出問題的地方）
```

---

## 階段 3：執行（Execution）

**狀態：** `In Progress`

**必做：**
1. 開工前先更新狀態
2. 按照規劃步驟逐一執行

**執行中規則：**
- 遇到重大偏差 → **立即更新 description**，記錄原計畫 vs 實際 + 為什麼改變
- 需要人工決策 → 暫停並回報，不要自己猜

---

## 階段 4：完成（Completion）

**狀態：** `Done`

**必做：**
1. 驗證所有完成標準達成
2. 更新 Linear description，附上執行結果
3. 更新狀態為 `Done`
4. 發送完成報告

**結果區塊（附在 description 最後）：**
```markdown
---
## 執行結果（YYYY-MM-DD）

### 實際變更
- （具體做了什麼）

### Before / After
- Before：（改之前）
- After：（改之後）

### 涉及檔案
- `path/to/file` — 改了什麼

### 已知限制 / 後續待辦
- （如果有的話）
```

---

## 返工（Rework）

**觸發：** Yihao 在已完成 issue 留 comment 並改回 `In Progress`

**流程：**
1. 讀 Linear 上的 comment，了解反饋
2. 根據反饋調整方案，更新 description
3. 重新執行
4. 完成後再次更新結果，改回 `Done`

> 每次開始任務前，先檢查是否有被退回的 issue（In Progress + 自己的 label）。

---

## 每階段 Checklist

| 階段 | 狀態 | 必須更新的 Linear 內容 |
|------|------|----------------------|
| 發想 | Backlog | 建 issue + 問題描述 |
| 規劃 | Todo | description 完整計畫 |
| 執行 | In Progress | 偏差時更新 description |
| 完成 | Done | description 附執行結果 |
| 返工 | In Progress | 讀 comment，重做後更新 |
