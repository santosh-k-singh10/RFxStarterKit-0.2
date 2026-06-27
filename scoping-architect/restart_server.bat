@echo off
echo Stopping all Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Starting server...
python run.py

@REM Made with Bob
