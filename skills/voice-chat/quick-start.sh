#!/bin/bash
# OpenClaw Voice Chat - Quick Start Script

set -e

echo "🎙️ OpenClaw Voice Chat - Quick Setup"
echo "======================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.12+"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# uv package manager
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo "✓ uv found: $(uv --version)"

# OpenClaw Gateway
echo ""
echo "🔍 Checking OpenClaw Gateway..."
if curl -s http://127.0.0.1:18789/api/status &> /dev/null; then
    echo "✓ OpenClaw Gateway is running"
else
    echo "❌ OpenClaw Gateway not reachable at http://127.0.0.1:18789"
    echo "   Please start OpenClaw first: openclaw start"
    exit 1
fi

# Create workspace
WORKSPACE="$HOME/.openclaw/workspace/skills/voice-chat"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

echo ""
echo "📥 Setting up Typeness..."

# Clone Typeness if not exists
if [ ! -d "typeness" ]; then
    echo "Cloning Typeness repository..."
    git clone https://github.com/yurenju/typeness.git
fi

cd typeness

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
uv sync

# Install additional packages
echo "Installing OpenClaw integration packages..."
uv pip install requests sounddevice numpy

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo ""
echo "1. Test Whisper installation:"
echo "   cd $WORKSPACE/typeness"
echo "   uv run python -c 'from transformers import pipeline; print(\"Whisper OK\")'"
echo ""
echo "2. Create the integration script (openclaw_voice.py) following SETUP.md"
echo ""
echo "3. Run voice chat:"
echo "   uv run python openclaw_voice.py"
echo ""
echo "📖 Full guide: $WORKSPACE/SETUP.md"
