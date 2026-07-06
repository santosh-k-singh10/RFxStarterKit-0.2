# ============================================================================
# RFxStarterKit - Startup Script (PowerShell)
# Starts the RFP Analyzer service:
#   RFP Analyzer  -> http://localhost:8080
# ============================================================================

$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " RFxStarterKit - System Startup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Components:" -ForegroundColor White
Write-Host "    [1] RFP Analyzer         http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host "  Phase 0 (multi-document) is auto-loaded by RFP Analyzer." -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- Start RFP Analyzer on port 8080 ---
Write-Host "[START] Launching RFP Analyzer on port 8080..." -ForegroundColor Yellow
$analyzerDir = Join-Path $Root "rfp-analyzer"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$analyzerDir'; uvicorn web_app:app --host 0.0.0.0 --port 8080 --log-level info" -WindowStyle Normal

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Both services started in separate windows." -ForegroundColor White
Write-Host " Wait ~30-60 seconds for model preloading to finish." -ForegroundColor Gray
Write-Host ""
Write-Host " Then open: http://localhost:8080" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
