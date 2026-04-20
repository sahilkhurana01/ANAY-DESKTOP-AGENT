@echo off
setlocal

echo Starting ANAY Desktop...
echo.

if not exist package.json (
  echo Run this script from the repo root.
  pause
  exit /b 1
)

start "ANAY Desktop" cmd /k "npm run dev"

echo Electron + frontend + backend are starting in one desktop session.
echo Frontend: http://127.0.0.1:5173
echo Backend:  http://127.0.0.1:8000
echo Hotkey:   Ctrl+Space
echo.
pause
