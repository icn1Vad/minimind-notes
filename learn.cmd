@echo off
rem Use the project Python from any working directory, without activating venv.
if not exist "%~dp0venv\Scripts\python.exe" (
    echo Project venv is missing. See WINDOWS_SETUP.md.
    exit /b 1
)
"%~dp0venv\Scripts\python.exe" -X utf8 %*
exit /b %errorlevel%
