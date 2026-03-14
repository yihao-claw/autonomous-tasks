---
name: voice-chat
description: Local voice conversation using Whisper (STT) and Edge TTS (integrated with OpenClaw)
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"bins": ["python3"]}, "homepage": "https://github.com/yurenju/typeness"}}
---

# Voice Chat Skill

雙向語音對話系統，基於 Typeness 架構整合到 OpenClaw。

## Architecture (基於 Typeness)

```
🎤 Microphone Input
  ↓ (sounddevice - 16kHz mono)
🗣️ Whisper large-v3-turbo (STT)
  ↓ (speech → text)
🚀 OpenClaw Gateway API
  ↓ (AI processing)
🎵 Edge TTS (text → speech)
  ↓
🔊 Audio Playback
```

## Components from Typeness

### 1. Audio Recording (`audio.py`)
- Uses `sounddevice` for microphone capture
- 16kHz, mono, float32 format
- VAD (Voice Activity Detection) optional

### 2. Speech-to-Text (`transcribe.py`)
- Whisper large-v3-turbo
- FP16 inference (~3.5GB VRAM)
- CJK text normalization
- HuggingFace transformers

### 3. Text Post-processing
- **Original**: Qwen3-1.7B for text cleanup
- **Modified**: Send to OpenClaw instead
- Remove Qwen3 dependency, use OpenClaw AI

### 4. Hotkey Management (`hotkey.py`)
- Global keyboard listener (pynput)
- Default: Shift+Win+A to toggle recording
- Customizable hotkey

### 5. Output
- **Original**: Clipboard paste
- **Modified**: TTS playback + optional paste

## Installation

### Prerequisites
- Python 3.12
- NVIDIA GPU with CUDA (optional but recommended)
- uv package manager: `pip install uv`

### Setup
```bash
cd {baseDir}
git clone https://github.com/yurenju/typeness.git
cd typeness

# Install dependencies
uv sync

# Modify for OpenClaw integration
cp {baseDir}/patches/* .
```

### Dependencies
```toml
[dependencies]
torch = "^2.6.0+cu130"
transformers = "^4.49.0"
sounddevice = "^0.5.1"
pynput = "^1.7.7"
pyperclip = "^1.9.0"
requests = "^2.32.3"  # for OpenClaw API
playsound = "^1.3.0"  # for audio playback
```

## Configuration

Create `config.json`:
```json
{
  "openclaw": {
    "gateway_url": "http://127.0.0.1:18789",
    "agent": "main"
  },
  "whisper": {
    "model": "openai/whisper-large-v3-turbo",
    "device": "cuda",
    "fp16": true
  },
  "tts": {
    "enabled": true,
    "provider": "edge",
    "voice": "zh-CN-XiaoxiaoNeural"
  },
  "hotkey": {
    "start_stop": "shift+win+a",
    "mute": "shift+win+m"
  },
  "audio": {
    "sample_rate": 16000,
    "channels": 1
  }
}
```

## Usage

### Start voice chat
```bash
cd {baseDir}/typeness
uv run python -m voice_chat
```

### Controls
- `Shift+Win+A`: Start/Stop recording
- `Shift+Win+M`: Mute TTS output
- `Ctrl+C`: Exit

### Debug mode
```bash
uv run python -m voice_chat --debug
# Saves recordings to debug/ folder
```

## Modified Files (Patches)

### 1. `main.py` - Add OpenClaw integration
```python
import requests

OPENCLAW_API = "http://127.0.0.1:18789/api/v1"

def send_to_openclaw(text: str) -> str:
    """Send transcribed text to OpenClaw and get response"""
    response = requests.post(
        f"{OPENCLAW_API}/agents/main/message",
        json={"message": text}
    )
    return response.json()["reply"]

def process_audio(audio_data):
    # 1. Whisper transcription
    text = transcribe(audio_data)
    print(f"You said: {text}")
    
    # 2. Send to OpenClaw (replace Qwen3)
    reply = send_to_openclaw(text)
    print(f"OpenClaw: {reply}")
    
    # 3. TTS playback
    if config["tts"]["enabled"]:
        audio_file = generate_tts(reply)
        play_audio(audio_file)
    
    return reply
```

### 2. `tts.py` - Add TTS module
```python
import requests

def generate_tts(text: str) -> str:
    """Generate TTS using OpenClaw's TTS API"""
    response = requests.post(
        f"{OPENCLAW_API}/tts/convert",
        json={
            "text": text,
            "provider": "edge",
            "voice": "zh-CN-XiaoxiaoNeural"
        }
    )
    return response.json()["audio_path"]

def play_audio(file_path: str):
    """Play audio file"""
    from playsound import playsound
    playsound(file_path)
```

## Integration with OpenClaw

### Option 1: Standalone Application
Run as separate Python app that communicates with OpenClaw Gateway via HTTP API.

### Option 2: OpenClaw Skill
Package as an OpenClaw skill with Node.js wrapper:
```javascript
// {baseDir}/bin/voice-chat
const { spawn } = require('child_process');
const path = require('path');

const python = spawn('uv', ['run', 'python', '-m', 'voice_chat'], {
  cwd: path.join(__dirname, '../typeness')
});

python.stdout.on('data', (data) => {
  console.log(data.toString());
});
```

## Advantages over Original Typeness

1. **Full AI conversation** - Not just transcription cleanup
2. **Voice output** - Hear the AI response
3. **OpenClaw integration** - Access to all OpenClaw tools and skills
4. **Multi-language** - OpenClaw supports many languages
5. **Customizable** - Use different TTS voices and models

## Performance

- **Whisper latency**: ~1-2s (GPU), ~5-10s (CPU)
- **OpenClaw processing**: ~2-5s (depends on model)
- **TTS latency**: ~1-2s (Edge TTS)
- **Total round-trip**: ~5-10s

## TODO

- [ ] Clone and patch Typeness
- [ ] Add OpenClaw API client
- [ ] Implement TTS playback
- [ ] Add VAD for better silence detection
- [ ] Web UI version (browser-based)
- [ ] Mobile app version

## References

- Original Typeness: https://github.com/yurenju/typeness
- OpenClaw TTS: /usr/local/lib/node_modules/openclaw/docs/tts.md
- Whisper: https://github.com/openai/whisper
