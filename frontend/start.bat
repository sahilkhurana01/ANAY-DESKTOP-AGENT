@echo off
REM ANAY Frontend Startup Script

echo Starting ANAY Frontend...

REM Check if node_modules exists, install if not
if not exist "node_modules" (
    echo node_modules not found. Installing dependencies...
    call npm install
)

REM Start the dev server
echo Starting Vite server...
call npm run dev
