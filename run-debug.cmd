@echo off
REM Launch RentTrack with the console kept open for troubleshooting.
REM Uses the project's virtual environment (no activation needed) and shows
REM any startup errors plus a pause so the window doesn't vanish.

cd /d "%~dp0"
"%~dp0..\.venv\Scripts\python.exe" src\renttrack\main.py

echo.
echo RentTrack exited with code %ERRORLEVEL%.
pause
