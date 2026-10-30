@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"

set "PYTHON_CMD="
py -3.11 --version >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3.11"

if not defined PYTHON_CMD (
    python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD goto python_missing

%PYTHON_CMD% -m pipenv --version >nul 2>nul
if errorlevel 1 (
    echo Pipenv is not installed. Installing it now...
    %PYTHON_CMD% -m pip install --user pipenv
    if errorlevel 1 goto failed
)

echo Syncing project dependencies...
%PYTHON_CMD% -m pipenv sync
if errorlevel 1 goto failed

echo Checking Playwright Chromium...
%PYTHON_CMD% -m pipenv run playwright install chromium
if errorlevel 1 goto failed

echo Starting DinkUp bot...
%PYTHON_CMD% -m pipenv run python dinkup_bot.py
set "BOT_EXIT_CODE=%ERRORLEVEL%"
if not "%BOT_EXIT_CODE%"=="0" goto failed

exit /b 0

:python_missing
echo Python 3.11 was not found. Install Python 3.11 and try again.
set "BOT_EXIT_CODE=1"
goto failed

:failed
if not defined BOT_EXIT_CODE set "BOT_EXIT_CODE=1"
if "%BOT_EXIT_CODE%"=="0" set "BOT_EXIT_CODE=1"
echo.
echo The bot setup or run failed. Check the message above.
pause
exit /b %BOT_EXIT_CODE%
