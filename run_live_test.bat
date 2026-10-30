@echo off
setlocal
cd /d "%~dp0"

set "TARGET_DAY_OFFSETS=5,6"
set "RUN_IMMEDIATELY=1"
call "%~dp0run_bot.bat"
exit /b %ERRORLEVEL%
