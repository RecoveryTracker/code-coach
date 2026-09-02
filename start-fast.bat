@echo off
rem Production mode. Use this for practising.
rem
rem start.bat runs the Vite dev server, which serves every module unbundled and
rem uses React's development build — great for editing the app, noticeably
rem heavier to interact with. This builds once and serves the result.
rem
rem Re-run it after changing anything under web\src to pick the changes up.

cd /d "%~dp0"

rem Same logging as start.bat: both servers run minimised, so without this a
rem crash leaves nothing behind. api.log is the current run, api.log.prev the
rem one before it — which is the one that died.
set LOGS=%~dp0logs
if not exist "%LOGS%" mkdir "%LOGS%"
set PYTHONUNBUFFERED=1
set NO_COLOR=1

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

echo Starting Code Coach...  logs\api.log, logs\ui.log

if exist "%LOGS%\api.log" move /y "%LOGS%\api.log" "%LOGS%\api.log.prev" >nul 2>&1
if exist "%LOGS%\ui.log" move /y "%LOGS%\ui.log" "%LOGS%\ui.log.prev" >nul 2>&1

start "Code Coach API" /min cmd /c ".\.venv\Scripts\python.exe -m uvicorn code_coach.api.server:app --no-use-colors --host 127.0.0.1 --port 8765 > logs\api.log 2>&1"
start "Code Coach UI"  /min cmd /c "cd web && npm run preview -- --port 5174 > ..\logs\ui.log 2>&1"

rem ping, not timeout: timeout aborts when stdin is redirected
ping -n 5 127.0.0.1 >nul

start "" "http://localhost:5174"
