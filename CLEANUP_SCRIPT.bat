@echo off
REM ============================================================================
REM RFxStarterKit - Workspace Cleanup Script
REM Removes unused files identified in the workspace analysis
REM ============================================================================

echo.
echo ============================================================
echo  RFxStarterKit - Workspace Cleanup
echo ============================================================
echo.
echo This script will remove unused/obsolete files.
echo A backup will be created before deletion.
echo.

set /p CONFIRM="Continue with cleanup? (yes/no): "
if /i not "%CONFIRM%"=="yes" (
    echo Cleanup cancelled.
    exit /b 0
)

echo.
echo Creating backup...
set BACKUP_DIR=backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%"

REM ============================================================================
REM 1. Remove debug/test files
REM ============================================================================
echo.
echo [1/4] Removing debug and test files...

if exist "check_html.py" (
    copy "check_html.py" "%BACKUP_DIR%\" >nul
    del "check_html.py"
    echo   - Removed: check_html.py
)

if exist "test_llm_connection.py" (
    copy "test_llm_connection.py" "%BACKUP_DIR%\" >nul
    del "test_llm_connection.py"
    echo   - Removed: test_llm_connection.py
)

if exist "initialize_git.ps1" (
    copy "initialize_git.ps1" "%BACKUP_DIR%\" >nul
    del "initialize_git.ps1"
    echo   - Removed: initialize_git.ps1
)

REM rfp-analyzer debug files
if exist "rfp-analyzer\debug_json_error_attempt_2.txt" del "rfp-analyzer\debug_json_error_attempt_2.txt" && echo   - Removed: rfp-analyzer\debug_json_error_attempt_2.txt
if exist "rfp-analyzer\debug_json_error_attempt_3.txt" del "rfp-analyzer\debug_json_error_attempt_3.txt" && echo   - Removed: rfp-analyzer\debug_json_error_attempt_3.txt
if exist "rfp-analyzer\test_both_html_exports.py" del "rfp-analyzer\test_both_html_exports.py" && echo   - Removed: rfp-analyzer\test_both_html_exports.py
if exist "rfp-analyzer\test_collapsible_html.py" del "rfp-analyzer\test_collapsible_html.py" && echo   - Removed: rfp-analyzer\test_collapsible_html.py
if exist "rfp-analyzer\test_collapsible_module.py" del "rfp-analyzer\test_collapsible_module.py" && echo   - Removed: rfp-analyzer\test_collapsible_module.py
if exist "rfp-analyzer\test_excel_export.py" del "rfp-analyzer\test_excel_export.py" && echo   - Removed: rfp-analyzer\test_excel_export.py
if exist "rfp-analyzer\test_html_export.py" del "rfp-analyzer\test_html_export.py" && echo   - Removed: rfp-analyzer\test_html_export.py
if exist "rfp-analyzer\test_viewer.html" del "rfp-analyzer\test_viewer.html" && echo   - Removed: rfp-analyzer\test_viewer.html

REM scoping-architect debug files
if exist "scoping-architect\check_routes.py" del "scoping-architect\check_routes.py" && echo   - Removed: scoping-architect\check_routes.py
if exist "scoping-architect\example_usage.py" del "scoping-architect\example_usage.py" && echo   - Removed: scoping-architect\example_usage.py
if exist "scoping-architect\test_import.py" del "scoping-architect\test_import.py" && echo   - Removed: scoping-architect\test_import.py
if exist "scoping-architect\replace_gsc.ps1" del "scoping-architect\replace_gsc.ps1" && echo   - Removed: scoping-architect\replace_gsc.ps1

REM ============================================================================
REM 2. Archive redundant documentation
REM ============================================================================
echo.
echo [2/4] Archiving redundant documentation...

mkdir "%BACKUP_DIR%\archived_docs" 2>nul

REM Root level redundant docs
for %%f in (
    AGENT_VS_SKILL_ARCHITECTURE_ANALYSIS.md
    AUTHENTICATION_FIX_COMPLETE.md
    COMPLETE_END_TO_END_ARCHITECTURE.md
    FINAL_CONFIGURATION_SUMMARY.md
    INTEGRATION_COMPLETE.md
    INTEGRATION_SUMMARY.md
    LLM_AUTHENTICATION_UNIFIED.md
    LLM_PROVIDER_GENERALIZATION.md
    PHASE0_INTEGRATION_TECHNICAL_DEEP_DIVE.md
    PHASE0_MULTI_DOCUMENT_EXPLAINED.md
    RFP_ANALYZER_REVERSE_ENGINEERING_REPORT.md
    SCOPING_ARCHITECT_INTEGRATION.md
    SYSTEM_READY_SUMMARY.md
    UNIFIED_LLM_CONFIGURATION_COMPLETE.md
) do (
    if exist "%%f" (
        move "%%f" "%BACKUP_DIR%\archived_docs\" >nul
        echo   - Archived: %%f
    )
)

REM ============================================================================
REM 3. Remove duplicate HTML files
REM ============================================================================
echo.
echo [3/4] Removing duplicate HTML files...

if exist "scoping-architect\RFP_to_GSC_Bridge_v2.html" (
    move "scoping-architect\RFP_to_GSC_Bridge_v2.html" "%BACKUP_DIR%\" >nul
    echo   - Removed: scoping-architect\RFP_to_GSC_Bridge_v2.html (keeping v3)
)

if exist "scoping-architect\RFP_to_GSE_Bridge_v2.html" (
    move "scoping-architect\RFP_to_GSE_Bridge_v2.html" "%BACKUP_DIR%\" >nul
    echo   - Removed: scoping-architect\RFP_to_GSE_Bridge_v2.html (keeping v3)
)

REM ============================================================================
REM 4. Clean up module-specific redundant docs
REM ============================================================================
echo.
echo [4/4] Cleaning module documentation...

mkdir "%BACKUP_DIR%\rfp-analyzer_docs" 2>nul
mkdir "%BACKUP_DIR%\scoping-architect_docs" 2>nul

REM rfp-analyzer redundant docs
for %%f in (
    CREATE_COLLAPSIBLE_HTML.md
    ENHANCED_WEB_APP_README.md
    HTML_GROUPING_GUIDE.md
    HTML_PREVIEW_IMPLEMENTATION.md
    HTML_VIEWER_IMPLEMENTATION_GUIDE.md
    QUICK_REFERENCE.md
    QUICK_START_ENHANCED_APP.md
    REMOTE_CONTEXT_GUIDE.md
    START_SAP_ANALYZER.md
    WEB_INTERFACE_GUIDE.md
) do (
    if exist "rfp-analyzer\%%f" (
        move "rfp-analyzer\%%f" "%BACKUP_DIR%\rfp-analyzer_docs\" >nul
        echo   - Archived: rfp-analyzer\%%f
    )
)

REM scoping-architect redundant docs (keeping only README, HOW_TO_USE, GSC_USAGE_GUIDE, PIPELINE)
for %%f in (
    AUTO_ENRICHMENT.md
    CURRENT_ISSUES.md
    ENRICHMENT_IMPROVEMENT_PLAN.md
    ENRICHMENT_IMPROVEMENT_RESULTS.md
    GAP_ANALYSIS.md
    GSC_AUTOFILL_DEBUG.md
    GSC_FIELD_MAPPING_ACTUAL.md
    GSC_FIELD_MAPPING.md
    GSC_INTEGRATION_SUMMARY.md
    GSC_INTEGRATION_TEST.md
    IMPLEMENTATION_COMPLETE.md
    IMPROVEMENTS_SUMMARY.md
    INTEGRATION_SUMMARY.md
    JSON_TRUNCATION_FIX.md
    JSON_TRUNCATION_SOLUTION.md
    LOGGING_SUMMARY.md
    RFP_GSC_BRIDGE_USAGE.md
    RFP_VS_GSC_GAP_ANALYSIS.md
    SAP_MODULE_IMPLEMENTATION.md
    SCOPING_METADATA_EXTRACTOR_EXPLAINED.md
    SERVER_RESTART_REQUIRED.md
    SETUP_COMPLETE.md
    UI_INTEGRATION_COMPLETE.md
) do (
    if exist "scoping-architect\%%f" (
        move "scoping-architect\%%f" "%BACKUP_DIR%\scoping-architect_docs\" >nul
        echo   - Archived: scoping-architect\%%f
    )
)

REM ============================================================================
REM Summary
REM ============================================================================
echo.
echo ============================================================
echo  Cleanup Complete!
echo ============================================================
echo.
echo Backup location: %BACKUP_DIR%
echo.
echo Files removed:
echo   - Debug/test scripts
echo   - Duplicate HTML files
echo   - Redundant documentation
echo.
echo Main documentation preserved:
echo   - README.md (to be renamed from README_INTEGRATED.md)
echo   - QUICK_START.md (to be renamed from QUICK_START_INTEGRATED.md)
echo   - START_APPLICATION.md
echo   - INTEGRATED_SYSTEM_GUIDE.md
echo.
echo Next steps:
echo   1. Review the backup folder
echo   2. Run: ren README_INTEGRATED.md README.md
echo   3. Run: ren QUICK_START_INTEGRATED.md QUICK_START.md
echo   4. Review RELEASE_READINESS_CHECKLIST.md for improvements
echo.
pause