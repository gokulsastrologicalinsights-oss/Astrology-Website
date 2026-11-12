@echo off
cd /d "%~dp0"
echo ===================================================
echo Pushing committed changes to GitHub repository...
echo Branch: feature/remedy-foundation
echo ===================================================
"C:\Users\Gokul Murugan\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe" push origin feature/remedy-foundation
echo.
pause
