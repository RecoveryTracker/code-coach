@echo off
rem Stop the API and start a fresh one.
rem
rem Needed because start.bat no longer passes --reload: uvicorn's reloader
rem wedged on this machine, logging "Reloading..." and then never restarting,
rem so the app quietly served old code for half an hour. A restart you have to
rem ask for is slower than one that works and much faster than one that lies.
rem
rem Run this after changing anything under code_coach\. The UI is left alone —
rem Vite's own reloading is fine.

cd /d "%~dp0"
set LOGS=%~dp0logs
if not exist "%LOGS%" mkdir "%LOGS%"
set PYTHONUNBUFFERED=1
set NO_COLOR=1

echo Stopping the API...

rem Kill by port AND by command line. The two are not the same: when a
rem reloader dies it leaves its worker holding the socket, and netstat then
rem reports the dead parent's id — so killing only what netstat names leaves
rem the live worker running and the port occupied. That orphan is what made
rem "API already running" attach to a server nobody was supervising.
powershell -NoProfile -Command ^
  "$ErrorActionPreference='SilentlyContinue';" ^
  "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*uvicorn*' -or $_.CommandLine -like '*multiprocessing-fork*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force };" ^
  "(netstat -ano | Select-String '127.0.0.1:8765' | Select-String 'LISTENING' | ForEach-Object { ($_ -split '\s+')[-1] } | Sort-Object -Unique) | ForEach-Object { Stop-Process -Id $_ -Force }"

rem Wait for the socket to actually clear before rebinding it.
ping -n 4 127.0.0.1 >nul

netstat -an | findstr "127.0.0.1:8765" | findstr LISTENING >nul
if not errorlevel 1 (
  echo.
  echo Port 8765 is still held. Something is running that this could not stop.
  pause
  exit /b 1
)

echo Starting the API...  logs\api.log
if exist "%LOGS%\api.log" move /y "%LOGS%\api.log" "%LOGS%\api.log.prev" >nul 2>&1
start "Code Coach API" /min cmd /c ".\.venv\Scripts\python.exe -m uvicorn code_coach.api.server:app --no-use-colors --host 127.0.0.1 --port 8765 > logs\api.log 2>&1"

ping -n 5 127.0.0.1 >nul
netstat -an | findstr "127.0.0.1:8765" | findstr LISTENING >nul
if errorlevel 1 (
  echo.
  echo The API did not come up. logs\api.log will say why.
  pause
  exit /b 1
)

echo API restarted. Reload the page in your browser.
