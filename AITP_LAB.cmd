@echo off
setlocal
cd /d "%~dp0"
echo.
echo WAIT -- AITP LABORATORY
echo Local-first browser experience. No cloud. No telemetry.
echo.
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 run_lab.py
) else (
  python run_lab.py
)
if errorlevel 1 (
  echo.
  echo STOP -- AITP Laboratory did not start successfully.
  echo Keep this window open and review the message above.
  pause
)
endlocal
