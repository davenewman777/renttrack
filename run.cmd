@echo off
REM Launch RentTrack using the project's virtual environment.
REM No need to activate .venv first - this calls its Python directly.
REM Double-click this file, or run "run.cmd" from any terminal.

cd /d "%~dp0"
REM "start" launches pythonw detached so this console window closes
REM immediately instead of sitting behind the app. /min keeps it out of
REM the way even during the brief startup.
start "RentTrack" /min "%~dp0..\.venv\Scripts\pythonw.exe" src\renttrack\main.py
