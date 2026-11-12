@echo off
cd /d "%~dp0"
start "Gokul Astrology Backend" cmd /k call "%~dp0Start-Gokul-Backend.bat"
timeout /t 3 /nobreak >nul
start "Gokul Astrology Frontend" cmd /k call "%~dp0Start-Gokul-Frontend.bat"
timeout /t 8 /nobreak >nul
start "" "http://127.0.0.1:3001"
