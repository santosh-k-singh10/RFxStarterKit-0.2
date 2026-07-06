@echo off
REM ============================================================================
REM RFxStarterKit - Startup Script (Windows)
REM Starts the RFP Analyzer service:
REM   RFP Analyzer  → http://localhost:8080
REM ============================================================================

echo.
echo ============================================================
echo  RFxStarterKit - System Startup
echo ============================================================
echo.
echo  Components:
echo    [1] RFP Analyzer         http://localhost:8080
echo.
echo  Phase 0 (multi-document):
echo    document-consolidator/phase0_router (auto-loaded)
echo.
echo ============================================================
echo.

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
