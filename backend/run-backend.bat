@echo off
REM Starts the FastAPI backend. Also called by start-dev.bat.
REM PYTHONPATH must point at the repo root because itinerary.py imports
REM common/geo/, which lives outside backend/.
cd /d "%~dp0"
set "PYTHONPATH=%~dp0.."
"%~dp0..\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload
