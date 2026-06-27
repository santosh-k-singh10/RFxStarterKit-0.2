# Git Initialization Script for RFP Analyzer
# Run this after confirming the system is working

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git Repository Initialization" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Git is installed" -ForegroundColor Green

# Check if already a git repository
if (Test-Path ".git") {
    Write-Host ""
    Write-Host "WARNING: This directory is already a git repository!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to reinitialize? (yes/no)"
    if ($response -ne "yes") {
        Write-Host "Aborted." -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Recurse -Force .git
}

# Initialize git repository
Write-Host ""
Write-Host "Initializing git repository..." -ForegroundColor Cyan
git init

# Create .gitignore if it doesn't exist or is empty
if (-not (Test-Path ".gitignore") -or (Get-Content ".gitignore" -ErrorAction SilentlyContinue).Count -eq 0) {
    Write-Host "Creating .gitignore..." -ForegroundColor Cyan
    @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Uploads
rfp-analyzer/analyzer/app/uploads/
uploads/

# Test outputs
*.pyc
.pytest_cache/
.coverage
htmlcov/

# Node modules (if any)
node_modules/
package-lock.json

# Excel temp files
~$*.xlsx
~$*.xls

# Backup files
*.backup
*.bak
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✓ .gitignore created" -ForegroundColor Green
} else {
    Write-Host "✓ .gitignore already exists" -ForegroundColor Green
}

# Stage all files
Write-Host ""
Write-Host "Staging files..." -ForegroundColor Cyan
git add .

# Show status
Write-Host ""
Write-Host "Git status:" -ForegroundColor Cyan
git status --short

# Create initial commit
Write-Host ""
Write-Host "Creating initial commit..." -ForegroundColor Cyan
$commitMessage = @"
Initial commit: Working RFP Analyzer

✅ Fixed Issues:
- Re-enabled embedder (was disabled for debugging)
- Re-enabled model preloading (was disabled for debugging)
- Timeout fixes in place (5-minute timeout, streaming uploads)
- PDF extraction enhanced
- Authentication unified (using common/.env)

📁 Key Components:
- RFP Analyzer with multi-agent system
- Phase 0 document router for multi-document support
- Scoping Architect integration
- Unified LLM authentication via common/.env

🔧 Configuration:
- Single .env file in common/ directory
- Model caching for performance
- Streaming file uploads
- Background task processing

📚 Documentation:
- START_APPLICATION.md - Quick start guide
- TIMEOUT_ISSUE_RESOLVED.md - Timeout fix details
- PDF_EXTRACTION_FIX.md - PDF handling improvements
- AUTHENTICATION_FIX_COMPLETE.md - Auth unification
- FINAL_CONFIGURATION_SUMMARY.md - Config details
"@

git commit -m $commitMessage

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Git repository initialized successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the application: cd rfp-analyzer/analyzer && python web_app.py" -ForegroundColor White
Write-Host "2. Add remote repository: git remote add origin <your-repo-url>" -ForegroundColor White
Write-Host "3. Push to remote: git push -u origin main" -ForegroundColor White
Write-Host ""

# Made with Bob
