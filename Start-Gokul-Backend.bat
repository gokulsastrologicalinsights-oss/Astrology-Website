@echo off
cd /d "E:\GAI\Astrology Website\backend"
"E:\GAI\Astrology Website\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
