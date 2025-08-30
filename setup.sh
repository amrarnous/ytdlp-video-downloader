#!/bin/bash

# Video Downloader Setup Script

echo "🎥 Video Downloader Setup"
echo "========================="

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p downloads
mkdir -p logs

echo "✅ Setup complete!"
echo ""
echo "To get started:"
echo "1. Activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   source .venv/Scripts/activate"
else
    echo "   source .venv/bin/activate"
fi
echo "2. Run the example:"
echo "   python example.py"
echo "3. Or start the API server:"
echo "   python -m uvicorn src.api:app --reload"
echo ""
echo "🐳 For Docker:"
echo "   docker-compose up -d"
