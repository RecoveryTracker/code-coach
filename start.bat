@echo off
cd /d "%~dp0"

netstat -an | findstr "127.0.0.1:8765" | findstr LISTENING >nul
if errorlevel 1 (
  echo Starting API...
  rem --reload so editing Python restarts the API, like Vite does for the UI
  start "Code Coach API" /min cmd /c ".\.venv\Scripts\python.exe -m uvicorn code_coach.api.server:app --reload --host 127.0.0.1 --port 8765"
) else (
  echo API already running.
)

netstat -an | findstr ":5173" | findstr LISTENING >nul
if errorlevel 1 (
  echo Starting UI...
  start "Code Coach UI" /min cmd /c "cd web && npm run dev"
  rem ping, not timeout: timeout aborts when stdin is redirected
  ping -n 6 127.0.0.1 >nul
) else (
  echo UI already running.
)

start "" "http://localhost:5173"
