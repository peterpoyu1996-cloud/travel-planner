@echo off
REM Starts the Vite dev server. Also called by start-dev.bat.
cd /d "%~dp0"
call npm run dev
