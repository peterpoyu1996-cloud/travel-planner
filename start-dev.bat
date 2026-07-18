@echo off
REM Double-click this to start local dev: opens two windows (backend + frontend)
REM and then opens the browser. Dev convenience only, not a packaged app --
REM closing the two windows stops the servers.
setlocal
cd /d "%~dp0"

echo [start-dev] starting backend (FastAPI, http://localhost:8000) ...
start "Travel Planner - Backend" cmd /k call "%~dp0backend\run-backend.bat"

echo [start-dev] starting frontend (Vite, http://localhost:5173) ...
start "Travel Planner - Frontend" cmd /k call "%~dp0frontend\run-frontend.bat"

echo [start-dev] waiting for servers, then opening browser ...
ping -n 5 127.0.0.1 >nul
start "" "http://localhost:5173"

endlocal
