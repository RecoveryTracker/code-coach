@echo off
cd /d "%~dp0"

rem Where a crash goes.
rem
rem Both servers run in minimised windows, so when one dies its output dies
rem with it and all you see is an app that stopped working. These logs are the
rem difference between "it stopped" and knowing why.
rem
rem Each run moves the previous log aside rather than appending: after the API
rem dies and you restart it, api.log is the run you are in and api.log.prev is
rem the one that crashed. That is almost always the one you want.
set LOGS=%~dp0logs
if not exist "%LOGS%" mkdir "%LOGS%"

rem Unbuffered, or a traceback can still be sitting in Python's own buffer
rem when the process dies and never reaches the file at all.
set PYTHONUNBUFFERED=1
rem Vite colours its output, and escape codes in a log file are noise. Both
rem servers inherit this.
set NO_COLOR=1

netstat -an | findstr "127.0.0.1:8765" | findstr LISTENING >nul
if errorlevel 1 (
  echo Starting API...  logs\api.log
  if exist "%LOGS%\api.log" move /y "%LOGS%\api.log" "%LOGS%\api.log.prev" >nul 2>&1
  rem No --reload, deliberately. Uvicorn's reloader wedges on this machine: it
  rem logs "Reloading..." and then never restarts, so the API carries on
  rem serving the code it started with while looking perfectly healthy. That
  rem cost two debugging sessions before logs\api.log made it visible. Run
  rem restart-api.bat after changing anything under code_coach\.
  rem --no-use-colors because escape codes in a log file are noise.
  rem The log path is relative on purpose: it avoids nesting quotes inside the
  rem quoted command, and `start` hands the child this directory anyway.
  start "Code Coach API" /min cmd /c ".\.venv\Scripts\python.exe -m uvicorn code_coach.api.server:app --no-use-colors --host 127.0.0.1 --port 8765 > logs\api.log 2>&1"
) else (
  echo API already running.
)

netstat -an | findstr ":5173" | findstr LISTENING >nul
if errorlevel 1 (
  echo Starting UI...   logs\ui.log
  if exist "%LOGS%\ui.log" move /y "%LOGS%\ui.log" "%LOGS%\ui.log.prev" >nul 2>&1
  start "Code Coach UI" /min cmd /c "cd web && npm run dev > ..\logs\ui.log 2>&1"
  rem ping, not timeout: timeout aborts when stdin is redirected
  ping -n 6 127.0.0.1 >nul
) else (
  echo UI already running.
)

start "" "http://localhost:5173"

rem Said once, at the end, where it will actually be read. The UI reloads
rem itself; the API does not.
echo.
echo Changed something under code_coach\? Run restart-api.bat.
