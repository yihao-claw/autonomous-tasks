# Voice Chat Setup Guide

基於 Typeness 建立 OpenClaw 雙向語音對話系統

## 🎯 目標

實現完整的語音對話循環：
```
你說話 → Whisper → OpenClaw AI → Edge TTS → 播放回覆
```

## 📋 系統需求

### 必要：
- Python 3.12+
- 麥克風
- 喇叭/耳機
- OpenClaw Gateway (已安裝 ✅)

### 可選（效能優化）：
- NVIDIA GPU + CUDA (Whisper 加速)
- 16GB+ RAM

### Linux/macOS/Windows 都支援

## 🚀 快速開始

### Step 1: 安裝依賴

```bash
# 安裝 uv (Python 套件管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或用 pip
pip install uv

# 驗證安裝
uv --version
```

### Step 2: Clone Typeness

```bash
cd ~/.openclaw/workspace/skills/voice-chat
git clone https://github.com/yurenju/typeness.git
cd typeness
```

### Step 3: 安裝 Python 依賴

```bash
# 建立虛擬環境並安裝依賴
uv sync

# 額外安裝 OpenClaw 整合需要的套件
uv pip install requests playsound
```

### Step 4: 下載模型（首次運行自動下載）

```bash
# 測試 Whisper（會自動下載模型 ~3.5GB）
uv run python -c "
from transformers import pipeline
pipe = pipeline('automatic-speech-recognition', 
                model='openai/whisper-large-v3-turbo',
                device='cuda' if torch.cuda.is_available() else 'cpu')
print('Whisper ready!')
"
```

### Step 5: 建立整合腳本

建立 `openclaw_voice.py`：

```python
#!/usr/bin/env python3
"""
OpenClaw Voice Chat Integration
Based on Typeness architecture
"""

import sys
import json
import requests
import sounddevice as sd
import numpy as np
from transformers import pipeline
from pathlib import Path

# Config
OPENCLAW_URL = "http://127.0.0.1:18789"
SAMPLE_RATE = 16000
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize Whisper
print("Loading Whisper model...")
whisper_pipe = pipeline(
    'automatic-speech-recognition',
    model='openai/whisper-large-v3-turbo',
    device=DEVICE
)
print("✓ Whisper ready")

def record_audio(duration=5):
    """Record audio from microphone"""
    print(f"🎤 Recording for {duration}s...")
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    print("✓ Recording complete")
    return audio.squeeze()

def transcribe(audio):
    """Whisper STT"""
    print("🗣️ Transcribing...")
    result = whisper_pipe(audio, return_timestamps=False)
    text = result['text'].strip()
    print(f"You: {text}")
    return text

def send_to_openclaw(text):
    """Send to OpenClaw and get response"""
    print("🤖 Sending to OpenClaw...")
    try:
        response = requests.post(
            f"{OPENCLAW_URL}/api/message",
            json={"message": text, "agent": "main"},
            timeout=30
        )
        reply = response.json().get('reply', '')
        print(f"Dan: {reply}")
        return reply
    except Exception as e:
        print(f"❌ OpenClaw error: {e}")
        return None

def generate_tts(text):
    """Generate TTS using OpenClaw"""
    print("🎵 Generating TTS...")
    try:
        response = requests.post(
            f"{OPENCLAW_URL}/api/tts",
            json={"text": text, "voice": "zh-CN-XiaoxiaoNeural"},
            timeout=30
        )
        audio_path = response.json().get('path')
        print(f"✓ TTS saved to {audio_path}")
        return audio_path
    except Exception as e:
        print(f"❌ TTS error: {e}")
        return None

def play_audio(file_path):
    """Play audio file"""
    print("🔊 Playing audio...")
    from playsound import playsound
    playsound(file_path)
    print("✓ Playback complete")

def main():
    print("🎙️ OpenClaw Voice Chat")
    print("=" * 50)
    print("Press Ctrl+C to exit\n")
    
    while True:
        try:
            input("Press Enter to start recording...")
            
            # 1. Record
            audio = record_audio(duration=5)
            
            # 2. Transcribe
            text = transcribe(audio)
            if not text:
                continue
            
            # 3. Send to OpenClaw
            reply = send_to_openclaw(text)
            if not reply:
                continue
            
            # 4. Generate TTS
            audio_path = generate_tts(reply)
            if not audio_path:
                continue
            
            # 5. Play
            play_audio(audio_path)
            
            print("\n" + "=" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
```

### Step 6: 運行！

```bash
cd ~/.openclaw/workspace/skills/voice-chat/typeness
uv run python openclaw_voice.py
```

## 🎮 使用方式

1. 運行程式
2. 按 Enter 開始錄音（5秒）
3. 說話（中文或英文）
4. 等待處理
5. 聽 OpenClaw 的語音回覆
6. 重複！

## 🔧 進階配置

### 使用 VAD（語音活動檢測）

不用固定時間錄音，自動檢測何時停止說話：

```bash
uv pip install webrtcvad
```

### 使用熱鍵（像原版 Typeness）

```python
from pynput import keyboard

# 按 Shift+Win+A 開始/停止錄音
# 參考 typeness/hotkey.py
```

### 調整 Whisper 模型

```python
# 更快但準確度稍低
model='openai/whisper-base'

# 平衡
model='openai/whisper-medium'

# 最準確（已使用）
model='openai/whisper-large-v3-turbo'
```

## 📊 預期效能

| 組件 | CPU | GPU (CUDA) |
|------|-----|------------|
| Whisper | 5-10s | 1-2s |
| OpenClaw | 2-5s | 2-5s |
| Edge TTS | 1-2s | 1-2s |
| **總計** | **8-17s** | **4-9s** |

## 🐛 故障排除

### Whisper 下載失敗
```bash
# 手動下載
huggingface-cli download openai/whisper-large-v3-turbo
```

### 找不到麥克風
```bash
# 列出音訊設備
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### CUDA 不可用
```bash
# 檢查 PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### OpenClaw API 連接失敗
```bash
# 檢查 Gateway 狀態
openclaw status

# 測試 API
curl http://127.0.0.1:18789/api/status
```

## 🎯 下一步

- [ ] 加入 VAD 自動停止錄音
- [ ] 加入全局熱鍵支援
- [ ] 建立 Web UI 版本
- [ ] 支援多輪對話（保持上下文）
- [ ] 加入喚醒詞（"Hey Dan"）
- [ ] 優化延遲（串流 TTS）

## 📚 參考資料

- Typeness: https://github.com/yurenju/typeness
- Whisper: https://github.com/openai/whisper
- OpenClaw TTS: `openclaw tts --help`
