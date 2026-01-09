#!/usr/bin/env pwsh
# Safe Drive Africa - Repository Migration Script
# Migrates from Python FastAPI to React Frontend (Clean Migration)

$ErrorActionPreference = "Stop"

# Configuration
$REPO_URL = "https://github.com/iniakponode/safe-drive-africa-datahub.git"
$ARCHIVE_BRANCH = "archive/python-fastapi-v1"
$NEW_BRANCH = "main"

Write-Host "🚀 Safe Drive Africa - Repository Migration Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Archive the existing Python FastAPI code" -ForegroundColor Yellow
Write-Host "  2. Replace it with this React frontend" -ForegroundColor Yellow
Write-Host "  3. Preserve history in an archive branch" -ForegroundColor Yellow
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "❌ Error: Not a git repository. Initializing..." -ForegroundColor Red
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
}

# Prompt for confirmation
Write-Host "⚠️  WARNING: This will replace the main branch at:" -ForegroundColor Red
Write-Host "   $REPO_URL" -ForegroundColor Red
Write-Host ""
$confirmation = Read-Host "Do you want to continue? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "❌ Migration cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Adding remote origin..." -ForegroundColor Cyan
# Remove existing remote if it exists
$remotes = git remote
if ($remotes -contains "origin") {
    Write-Host "  Removing existing origin..." -ForegroundColor Yellow
    git remote remove origin
}
git remote add origin $REPO_URL
Write-Host "✅ Remote origin added" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Fetching existing repository..." -ForegroundColor Cyan
git fetch origin
Write-Host "✅ Repository fetched" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Archiving Python FastAPI code..." -ForegroundColor Cyan
# Check if origin/main exists
$branches = git branch -r
if ($branches -match "origin/main") {
    git push origin origin/main:refs/heads/$ARCHIVE_BRANCH
    Write-Host "✅ Python code archived to branch: $ARCHIVE_BRANCH" -ForegroundColor Green
} else {
    Write-Host "⚠️  No existing main branch found. Skipping archive." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Creating clean history for React frontend..." -ForegroundColor Cyan

# Check if we're already on a branch
$currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
if ($LASTEXITCODE -eq 0 -and $currentBranch -ne "HEAD") {
    Write-Host "  Current branch: $currentBranch" -ForegroundColor Yellow
    Write-Host "  Creating orphan branch..." -ForegroundColor Yellow
    git checkout --orphan new-main
} else {
    Write-Host "  Creating orphan branch..." -ForegroundColor Yellow
    git checkout --orphan new-main
}

Write-Host "✅ Orphan branch created" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Adding all React frontend files..." -ForegroundColor Cyan
git add .
Write-Host "✅ Files staged" -ForegroundColor Green

Write-Host ""
Write-Host "Step 6: Creating initial commit..." -ForegroundColor Cyan
$commitMessage = @"
feat: Initial React/TypeScript frontend

Replaces Python FastAPI implementation with modern React frontend.

Features:
- Vite + React 19 + TypeScript
- Complete CI/CD pipeline with GitHub Actions
- Automated deployment to IONOS VPS with Plesk
- Docker support with multi-stage builds
- Automated backups and rollback capabilities
- Comprehensive documentation

Architecture:
- Frontend: React + TypeScript + Vite
- API Backend: FastAPI at api.safedriveafrica.com
- Hosting: IONOS VPS with Plesk
- CI/CD: GitHub Actions

Previous Python FastAPI implementation archived in '$ARCHIVE_BRANCH' branch.

Migration Date: $(Get-Date -Format "yyyy-MM-dd")
"@

git commit -m $commitMessage
Write-Host "✅ Initial commit created" -ForegroundColor Green

Write-Host ""
Write-Host "Step 7: Renaming branch to main..." -ForegroundColor Cyan
git branch -M new-main $NEW_BRANCH
Write-Host "✅ Branch renamed to main" -ForegroundColor Green

Write-Host ""
Write-Host "Step 8: Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "⚠️  This will force-push and replace the main branch" -ForegroundColor Yellow
$pushConfirmation = Read-Host "Continue with push? (yes/no)"
if ($pushConfirmation -ne "yes") {
    Write-Host "❌ Push cancelled. Your local changes are ready but not pushed." -ForegroundColor Yellow
    Write-Host "   To push manually later, run: git push origin main --force" -ForegroundColor Yellow
    exit 0
}

git push origin $NEW_BRANCH --force
Write-Host "✅ Pushed to GitHub successfully!" -ForegroundColor Green

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "✅ Migration Completed Successfully!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Update Repository Settings on GitHub:" -ForegroundColor Yellow
Write-Host "   - Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings" -ForegroundColor White
Write-Host "   - Update description: 'React + TypeScript frontend for Safe Drive Africa Data Hub'" -ForegroundColor White
Write-Host "   - Add topics: react, typescript, vite, safe-driving, africa" -ForegroundColor White
Write-Host ""
Write-Host "2. Configure GitHub Secrets (Required for CI/CD):" -ForegroundColor Yellow
Write-Host "   - See: .github/SECRETS.md for complete list" -ForegroundColor White
Write-Host "   - Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings/secrets/actions" -ForegroundColor White
Write-Host ""
Write-Host "3. Set up Branch Protection:" -ForegroundColor Yellow
Write-Host "   - Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings/branches" -ForegroundColor White
Write-Host "   - Add rule for 'main' branch" -ForegroundColor White
Write-Host "   - Enable: Require pull request reviews, Require status checks" -ForegroundColor White
Write-Host ""
Write-Host "4. Verify CI/CD Pipeline:" -ForegroundColor Yellow
Write-Host "   - Go to: https://github.com/iniakponode/safe-drive-africa-datahub/actions" -ForegroundColor White
Write-Host "   - After configuring secrets, push a test commit" -ForegroundColor White
Write-Host ""
Write-Host "5. Archive Branch Access:" -ForegroundColor Yellow
Write-Host "   - Old Python code: https://github.com/iniakponode/safe-drive-africa-datahub/tree/$ARCHIVE_BRANCH" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - Deployment Guide: DEPLOYMENT.md" -ForegroundColor White
Write-Host "  - Quick Reference: QUICKSTART.md" -ForegroundColor White
Write-Host "  - CI/CD Overview: CI_CD_README.md" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Your React frontend is now live at:" -ForegroundColor Green
Write-Host "   https://github.com/iniakponode/safe-drive-africa-datahub" -ForegroundColor Green
Write-Host ""
