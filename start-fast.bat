@echo off
rem Production mode. Use this for practising.
rem
rem start.bat runs the Vite dev server, which serves every module unbundled and
rem uses React's development build — great for editing the app, noticeably
rem heavier to interact with. This builds once and serves the result.
rem
rem Re-run it after changing anything under web\src to pick the changes up.

cd /d "%~dp0"

echo Building the UI (about 20 seconds)...
cd web
call npm run build
if errorlevel 1 (
  echo.
  echo Build failed — see the errors above. Falling back to start.bat is fine.
  pause
  exit /b 1
)
cd ..

echo Starting Code Coach...

start "Code Coach API" /min cmd /c ".\.venv\Scripts\python.exe -m uvicorn code_coach.api.server:app --host 127.0.0.1 --port 8765"
start "Code Coach UI"  /min cmd /c "cd web && npm run preview -- --port 5174"

rem ping, not timeout: timeout aborts when stdin is redirected
ping -n 5 127.0.0.1 >nul

start "" "http://localhost:5174"
