# YouTube Channel Tracker

## 追蹤頻道清單（9 個）

### AI / 科技
| 頻道 | Handle | Channel ID | 追蹤方式 |
|------|--------|-----------|----------|
| 最佳拍档 | @bestpartners | UCGWYKICLOE8Wxy7q3eYXmPA | 每小時即時通知 |

### 投資 / 財經
| 頻道 | Handle | Channel ID | 類型 |
|------|--------|-----------|------|
| 金點子 | @thuyang6963 | UCVWyAAEdSe8y8BQkYir6iqQ | 黃金/大宗商品 |
| D的財富鏈 | @DWealthChain | UCVGYz_TsbJRiDykog88EFQg | 美股分析 |
| 在美理財 | @usfinance | UCDT7QFSo2znU9BXryYECATg | 美國投資/稅務 |
| StayRich | @stayrich_ustv | UCv496KjsTSTpJ4sGfHZ8_Qw | 台股/美股/總經 |
| 投資嗨什麼 | @hi2inv | UC99pEneQfxE8Tg3uNa9QXEw | ETF/股票/債券 |
| SHIN LI | @shinli | UCK-qc_POQZwWrMg-Pr-oYtg | 個人理財/被動收入 |
| 硅谷101 | @SiliconValley101 | UCd5AYYgeVHSO8eafpnkix6A | 科技投資/創投 |
| 劉瑆 | @liuliuxing | UC_ZgKNywKxWY3bTydtotTUA | 新手理財/投資心法 |

## Cron Jobs

1. **yt-bestpartners-hourly** — 每小時檢查最佳拍档新影片，即時通知
2. **yt-daily-investment-digest** — 每天 JST 21:00 統整所有投資頻道新影片，發送詳細摘要

## 通知方式
- 目標：Telegram General (-1003767828002)
- 投資統整包含完整字幕摘要（使用 playwright-cli 抓取 transcript）
