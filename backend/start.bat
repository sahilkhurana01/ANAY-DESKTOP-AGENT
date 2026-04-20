@echo off
cd /d "%~dp0"
echo Starting ANAY Backend...
echo Install dependencies if first time:
pip install -r requirements.txt
echo.
echo Starting FastAPI server on http://localhost:8000
python main.py
pause
