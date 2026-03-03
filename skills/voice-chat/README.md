# 🎙️ OpenClaw Voice Chat

基於 [Typeness](https://github.com/yurenju/typeness) 架構的雙向語音對話系統

## ✨ 功能

- 🎤 **語音輸入** - Whisper large-v3-turbo 本地語音識別
- 🤖 **AI 對話** - OpenClaw AI 處理（Claude Sonnet 4.5）
- 🗣️ **語音輸出** - Edge TTS 免費語音合成
- 🌏 **支援中文** - 繁體/簡體中文、英文等
- 💻 **完全本地** - 所有處理都在本機（除了 LLM API 和 Edge TTS）
- 🔄 **循環對話** - 連續多輪對話

## 🎯 工作流程

```
你說話 🎤
  ↓
Whisper (語音→文字) 🗣️
  ↓
OpenClaw AI (Claude) 🤖
  ↓
Edge TTS (文字→語音) 🎵
  ↓
播放回覆 🔊
  ↓
重複 🔄
```

## 🚀 快速開始

### 方法 1：自動安裝（推薦）

```bash
cd ~/.openclaw/workspace/skills/voice-chat
./quick-start.sh
```

### 方法 2：手動安裝

詳見 [SETUP.md](./SETUP.md)

## 📋 系統需求

### 必要：
- ✅ Python 3.12+
- ✅ OpenClaw Gateway (已安裝)
- ✅ 麥克風
- ✅ 喇叭/耳機

### 可選（效能優化）：
- NVIDIA GPU + CUDA (Whisper 加速 10x)
- 16GB+ RAM

## 📊 效能

| 組件 | 延遲 (GPU) | 延遲 (CPU) |
|------|------------|------------|
| Whisper STT | 1-2秒 | 5-10秒 |
| OpenClaw AI | 2-5秒 | 2-5秒 |
| Edge TTS | 1-2秒 | 1-2秒 |
| **總計** | **4-9秒** | **8-17秒** |

## 🎮 使用範例

```bash
# 啟動語音對話
cd ~/.openclaw/workspace/skills/voice-chat/typeness
uv run python openclaw_voice.py

# 基本流程
按 Enter → 說話 (5秒) → 等待 AI 回覆 → 聽語音 → 重複
```

## 🔧 配置選項

### 切換 TTS 語音

在 `openclaw.json` 中修改：

```json
{
  "messages": {
    "tts": {
      "edge": {
        "voice": "zh-CN-XiaoxiaoNeural"  // 女聲
        // "voice": "zh-CN-YunxiNeural"   // 男聲
        // "voice": "zh-TW-HsiaoChenNeural" // 台灣女聲
      }
    }
  }
}
```

### 切換 Whisper 模型

```python
# 在 openclaw_voice.py 中
model='openai/whisper-base'          # 快速，準確度稍低
model='openai/whisper-medium'        # 平衡
model='openai/whisper-large-v3-turbo' # 最準確（預設）
```

## 📁 檔案結構

```
voice-chat/
├── README.md           # 本檔案
├── SKILL.md            # OpenClaw skill 定義
├── SETUP.md            # 詳細安裝指南
├── quick-start.sh      # 自動安裝腳本
└── typeness/           # Typeness 原始碼（git clone）
    ├── openclaw_voice.py  # 整合腳本（你要建立的）
    └── ...
```

## 🎯 進階功能（規劃中）

- [ ] VAD（Voice Activity Detection）- 自動停止錄音
- [ ] 全局熱鍵 - 像 Typeness 一樣按 Shift+Win+A
- [ ] Web UI - 瀏覽器介面
- [ ] 喚醒詞 - "Hey Dan" 啟動
- [ ] 串流 TTS - 降低延遲
- [ ] 多輪對話 - 保持上下文

## 🆚 對比 Typeness

| 功能 | Typeness | OpenClaw Voice Chat |
|------|----------|---------------------|
| 語音輸入 | ✅ Whisper | ✅ Whisper |
| AI 處理 | Qwen3 (文字優化) | OpenClaw AI (完整對話) |
| 語音輸出 | ❌ | ✅ Edge TTS |
| 輸出方式 | 貼上文字 | 播放語音 |
| 用途 | 語音輸入法 | AI 語音助理 |

## 🐛 故障排除

### Whisper 模型下載失敗
```bash
# 手動下載
huggingface-cli download openai/whisper-large-v3-turbo
```

### 找不到麥克風
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### OpenClaw 連接失敗
```bash
openclaw status
curl http://127.0.0.1:18789/api/status
```

## 📚 參考資料

- **Typeness**: https://github.com/yurenju/typeness
- **Whisper**: https://github.com/openai/whisper
- **OpenClaw TTS**: `/usr/local/lib/node_modules/openclaw/docs/tts.md`
- **Edge TTS**: https://github.com/rany2/edge-tts

## 🤝 貢獻

這是實驗性專案！歡迎改進：

1. 降低延遲
2. 改善錯誤處理
3. 加入 Web UI
4. 支援更多語言
5. 優化模型選擇

## 📄 授權

基於 Typeness (MIT License) 修改
OpenClaw 整合部分遵循 OpenClaw 授權

---

**Made with ❤️ by Dan (OpenClaw Assistant)**
