@echo off
REM ============================================================================
REM RFxStarterKit - Unified Startup Script (Windows)
REM Starts all 3 integrated components:
REM   1. Scoping Architect  → http://localhost:8001
REM   2. RFP Analyzer       → http://localhost:8080
REM ============================================================================

echo.
echo ============================================================
echo  RFxStarterKit - Integrated System Startup
echo ============================================================
echo.
echo  Components:
echo    [1] Scoping Architect    http://localhost:8001
echo    [2] RFP Analyzer         http://localhost:8080
echo.
echo  Phase 0 (multi-document):
echo    document-consolidator/phase0_router (auto-loaded)
echo.
echo ============================================================
echo.

REM --- Start Scoping Architect on port 8001 ---
echo [START] Launching Scoping Architect on port 8001...
start "Scoping Architect (port 8001)" cmd /k "cd /d %~dp0scoping-architect && python run.py"

REM Give it a moment to bind before starting RFP Analyzer
timeout /t 3 /nobreak > nul

REM --- Start RFP Analyzer on port 8080 ---
echo [START] Launching RFP Analyzer on port 8080...
start "RFP Analyzer (port 8080)" cmd /k "cd /d %~dp0rfp-analyzer && uvicorn web_app:app --host 0.0.0.0 --port 8080 --log-level info"

echo.
echo ============================================================
echo  Both services starting in separate windows.
echo  Wait ~30-60 seconds for model preloading to finish.
echo.
echo  Then open: http://localhost:8080
echo ============================================================
echo.
pause
