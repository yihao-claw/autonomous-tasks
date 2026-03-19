# 🎯 Opportunity Radar — 商機雷達系統

yh jp 商機探測系統。系統化掃描台灣 + 日本市場，找出有數據支持的 APP/SaaS 機會。

## 設計理念

參考 Connor 方法論：
1. **先驗證需求** — 有人在抱怨 = 有需求
2. **先驗證付費意願** — 有競品在賺錢 = 有人付費
3. **先找分發** — 有 KOL 可合作 = 有通路

## 資料來源 & 腳本

### Phase 1: 需求探測（Pain Point Scanner）

| 來源 | 方法 | 目標 |
|------|------|------|
| PTT | 爬熱門板（Lifeismoney, Salary, Tech_Job, iOS, Android）| 高頻抱怨、求推薦 |
| Dcard | 爬工作板、理財板、生活板 | 年輕族群痛點 |
| Reddit | r/japanlife, r/movingtojapan, r/japanfinance | 在日外國人痛點 |
| X/Twitter | 關鍵字監控（「好想有一個app」「為什麼沒有」「超不方便」）| 即時需求信號 |

### Phase 2: 市場驗證（Market Validator）

| 來源 | 方法 | 目標 |
|------|------|------|
| App Store Top Grossing | 爬台灣/日本各類別 Top 100 | 哪些品類有人付費 |
| App Store Reviews | 爬競品 1-3 星評論 | 未被滿足的需求 |
| Google Trends | 搜尋量趨勢比較 | 需求成長/衰退 |
| SimilarWeb/Sensor Tower | 估算下載量和營收 | 市場規模驗證 |

### Phase 3: 機會評分（Opportunity Scorer）

每個機會按以下維度評分（1-10）：

- **Pain Level** — 痛點有多痛？（抱怨頻率 & 情緒強度）
- **Market Size** — 潛在用戶有多少？
- **Willingness to Pay** — 有人為類似方案付費嗎？
- **Competition** — 現有方案品質如何？（差 = 好機會）
- **Build Complexity** — 我們能多快做出 MVP？
- **Distribution** — 有可用的分發渠道嗎？

總分 = 加權平均，閾值 > 7.0 進入深入研究。

### Phase 4: 報告輸出

- 每週產出「商機週報」
- Top 5 機會附完整分析
- 推送到 Telegram 給 Yihao 審閱

## 技術架構

```
opportunity-radar/
├── scripts/
│   ├── scan_ptt.py          # PTT 爬蟲
│   ├── scan_dcard.py         # Dcard 爬蟲
│   ├── scan_reddit.py        # Reddit 爬蟲
│   ├── scan_appstore.py      # App Store 排名 + 評論爬蟲
│   ├── scan_trends.py        # Google Trends 查詢
│   ├── scorer.py             # 機會評分引擎
│   └── report.py             # 週報生成
├── data/
│   ├── raw/                  # 原始爬取資料
│   ├── processed/            # 處理後資料
│   └── reports/              # 週報輸出
├── config/
│   ├── keywords_tw.json      # 台灣關鍵字清單
│   ├── keywords_jp.json      # 日本關鍵字清單
│   └── categories.json       # App Store 類別設定
└── README.md
```

## 執行排程

- **每日**：PTT/Dcard/Reddit 掃描（增量）
- **每週**：App Store 排名更新 + 機會評分 + 週報
- **每月**：Google Trends 趨勢分析 + 策略調整

## 負責人

- **Dan**（總經理）— 方向把關、機會判斷、報告審閱
- **Vince**（工程）— 建置爬蟲腳本、自動化排程
