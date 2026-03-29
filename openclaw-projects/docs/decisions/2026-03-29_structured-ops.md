# Decision: 結構化營運制度

- **Date:** 2026-03-29
- **Author:** Yihao + Dan
- **Status:** Approved

## 背景

公司運作日趨複雜（多個 agent、cron job、每日新聞 podcast 等），需要更結構化的管理方式。

## 決定

1. **所有任務、維運與結果記錄在 Obsidian**（知識庫 + 每日紀錄）
2. **每日營運報告**（cron job，JST 22:00，發送至 Telegram）供 Yihao 審查回饋
3. **任務管理用 Linear**，Obsidian 做知識沉澱，兩邊不重複
4. **所有文件上 GitHub**（docs/decisions, docs/sops, docs/reports）
5. **決策日誌**記錄每個重要決策的背景、選項、結論
6. **SOP 文件化**重複性流程

## 分工

- **GitHub (openclaw-projects/docs/)**：SOP、決策日誌、報告模板、程式碼 — source of truth
- **Obsidian**：每日工作紀錄、知識筆記、個人反思 — 私有

## 優先順序

1. 🔴 每日報告機制
2. 🔴 Linear 任務流程紀律
3. 🟡 決策日誌
4. 🟡 SOP 文件化
5. 🟢 週報/月報
6. 🟢 成本儀表板
