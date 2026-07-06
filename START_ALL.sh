#!/usr/bin/env bash
# ============================================================================
# RFxStarterKit - Unified Startup Script (Linux/Mac)
# Starts the RFP Analyzer service:
#   RFP Analyzer  → http://localhost:${RFP_ANALYZER_PORT:-8080}
#
# Phase 0 (multi-document) is auto-loaded by the RFP Analyzer.
# ============================================================================

set -euo pipefail

# Resolve the directory this script lives in, so it works regardless of cwd
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load ports from common/.env if present, otherwise fall back to defaults
ENV_FILE="${SCRIPT_DIR}/common/.env"
RFP_ANALYZER_PORT="${RFP_ANALYZER_PORT:-8080}"
if [ -f "$ENV_FILE" ]; then
  # Safely source only KEY=VALUE lines — strips inline comments so set -e
  # does not trip on lines like:  CACHE_TTL=300  # seconds
  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue   # skip comment lines
    [[ -z "${line// }" ]]           && continue   # skip blank lines
    # Strip inline comment, then export
    export "${line%%#*}" 2>/dev/null || true
  done < "$ENV_FILE"
  RFP_ANALYZER_PORT="${RFP_ANALYZER_PORT:-8080}"
fi

echo
echo "============================================================"
echo " RFxStarterKit - System Startup"
echo "============================================================"
echo
echo " Components:"
echo "   [1] RFP Analyzer         http://localhost:${RFP_ANALYZER_PORT}"
echo
echo " Phase 0 (multi-document):"
echo "   document-consolidator/phase0_router (auto-loaded)"
echo
echo "============================================================"
echo

if [ ! -f "$ENV_FILE" ]; then
  echo "[WARN] No .env file found at common/.env"
  echo "       Run: cp common/.env.template common/.env   and fill in your API key first."
  echo
fi

# --- Start RFP Analyzer on its configured port ---
echo "[START] Launching RFP Analyzer on port ${RFP_ANALYZER_PORT}..."
(cd rfp-analyzer && uvicorn web_app:app --host 0.0.0.0 --port "${RFP_ANALYZER_PORT}" --log-level info) \
  > "${SCRIPT_DIR}/logs_rfp-analyzer.log" 2>&1 &
RFP_PID=$!

echo
echo "============================================================"
echo " Service starting in the background."
echo " Wait ~30-60 seconds for model preloading to finish."
echo
echo " Logs:"
echo "   tail -f logs_rfp-analyzer.log"
echo
echo " Then open: http://localhost:${RFP_ANALYZER_PORT}"
echo
echo " To stop:"
echo "   kill ${RFP_PID}"
echo "============================================================"
echo

# Ctrl+C in this terminal stops the background service cleanly
trap 'echo; echo "Stopping..."; kill ${RFP_PID} 2>/dev/null || true' INT TERM
wait ${RFP_PID}
