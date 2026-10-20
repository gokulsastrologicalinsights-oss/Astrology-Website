@echo off
echo ========================================================
echo Starting Gokul's Astrological Insights Local Servers
echo ========================================================

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000...
start "GAI Backend API" cmd /k "cd /d "%~dp0backend" && "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Next.js Frontend on http://127.0.0.1:3001...
start "GAI Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 5 >nul

echo Opening default browser...
start http://127.0.0.1:3001

echo ========================================================
echo Both servers are running:
echo   - Frontend: http://127.0.0.1:3001
echo   - Backend:  http://127.0.0.1:8000
echo   - API Docs: http://127.0.0.1:8000/docs
echo ========================================================
pause
