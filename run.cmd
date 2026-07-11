@echo off
REM Launch RentTrack using the project's virtual environment.
REM No need to activate .venv first - this calls its Python directly.
REM Double-click this file, or run "run.cmd" from any terminal.

cd /d "%~dp0"
"%~dp0..\.venv\Scripts\pythonw.exe" src\renttrack\main.py
