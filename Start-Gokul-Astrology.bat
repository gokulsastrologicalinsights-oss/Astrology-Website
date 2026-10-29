@echo off
cd /d "E:\GAI\Astrology Website"
start "Gokul Astrology Backend" cmd /k call "E:\GAI\Astrology Website\Start-Gokul-Backend.bat"
timeout /t 3 /nobreak >nul
start "Gokul Astrology Frontend" cmd /k call "E:\GAI\Astrology Website\Start-Gokul-Frontend.bat"
timeout /t 8 /nobreak >nul
start "" "http://127.0.0.1:3001"
