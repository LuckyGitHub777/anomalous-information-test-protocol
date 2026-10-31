@echo off
setlocal
cd /d "%~dp0"
python run_site.py
if errorlevel 1 (
  echo.
  echo AITP public web preview did not start successfully.
  pause
)
endlocal
