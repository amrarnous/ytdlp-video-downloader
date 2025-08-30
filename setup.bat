@echo off
REM Video Downloader Setup Script for Windows

echo 🎥 Video Downloader Setup
echo =========================

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create directories
echo 📁 Creating directories...
if not exist downloads mkdir downloads
if not exist logs mkdir logs

echo ✅ Setup complete!
echo.
echo To get started:
echo 1. Activate the virtual environment:
echo    .venv\Scripts\activate.bat
echo 2. Run the example:
echo    python example.py
echo 3. Or start the API server:
echo    python -m uvicorn src.api:app --reload
echo.
echo 🐳 For Docker:
echo    docker-compose up -d

pause
