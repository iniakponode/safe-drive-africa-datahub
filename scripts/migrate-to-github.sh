#!/bin/bash
# Safe Drive Africa - Repository Migration Script
# Migrates from Python FastAPI to React Frontend (Clean Migration)

set -e

# Configuration
REPO_URL="https://github.com/iniakponode/safe-drive-africa-datahub.git"
ARCHIVE_BRANCH="archive/python-fastapi-v1"
NEW_BRANCH="main"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Safe Drive Africa - Repository Migration Script${NC}"
echo -e "${CYAN}=================================================${NC}"
echo ""
echo -e "${YELLOW}This script will:${NC}"
echo -e "${YELLOW}  1. Archive the existing Python FastAPI code${NC}"
echo -e "${YELLOW}  2. Replace it with this React frontend${NC}"
echo -e "${YELLOW}  3. Preserve history in an archive branch${NC}"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo -e "${RED}❌ Error: Not a git repository. Initializing...${NC}"
    git init
    echo -e "${GREEN}✅ Git repository initialized${NC}"
fi

# Prompt for confirmation
echo -e "${RED}⚠️  WARNING: This will replace the main branch at:${NC}"
echo -e "${RED}   $REPO_URL${NC}"
echo ""
read -p "Do you want to continue? (yes/no): " confirmation
if [ "$confirmation" != "yes" ]; then
    echo -e "${YELLOW}❌ Migration cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}Step 1: Adding remote origin...${NC}"
# Remove existing remote if it exists
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}  Removing existing origin...${NC}"
    git remote remove origin
fi
git remote add origin $REPO_URL
echo -e "${GREEN}✅ Remote origin added${NC}"

echo ""
echo -e "${CYAN}Step 2: Fetching existing repository...${NC}"
git fetch origin
echo -e "${GREEN}✅ Repository fetched${NC}"

echo ""
echo -e "${CYAN}Step 3: Archiving Python FastAPI code...${NC}"
# Check if origin/main exists
if git branch -r | grep -q "origin/main"; then
    git push origin origin/main:refs/heads/$ARCHIVE_BRANCH
    echo -e "${GREEN}✅ Python code archived to branch: $ARCHIVE_BRANCH${NC}"
else
    echo -e "${YELLOW}⚠️  No existing main branch found. Skipping archive.${NC}"
fi

echo ""
echo -e "${CYAN}Step 4: Creating clean history for React frontend...${NC}"

# Check if we're already on a branch
current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ -n "$current_branch" ] && [ "$current_branch" != "HEAD" ]; then
    echo -e "${YELLOW}  Current branch: $current_branch${NC}"
    echo -e "${YELLOW}  Creating orphan branch...${NC}"
    git checkout --orphan new-main
else
    echo -e "${YELLOW}  Creating orphan branch...${NC}"
    git checkout --orphan new-main
fi

echo -e "${GREEN}✅ Orphan branch created${NC}"

echo ""
echo -e "${CYAN}Step 5: Adding all React frontend files...${NC}"
git add .
echo -e "${GREEN}✅ Files staged${NC}"

echo ""
echo -e "${CYAN}Step 6: Creating initial commit...${NC}"
commit_message="feat: Initial React/TypeScript frontend

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

Migration Date: $(date +%Y-%m-%d)"

git commit -m "$commit_message"
echo -e "${GREEN}✅ Initial commit created${NC}"

echo ""
echo -e "${CYAN}Step 7: Renaming branch to main...${NC}"
git branch -M new-main $NEW_BRANCH
echo -e "${GREEN}✅ Branch renamed to main${NC}"

echo ""
echo -e "${CYAN}Step 8: Pushing to GitHub...${NC}"
echo -e "${YELLOW}⚠️  This will force-push and replace the main branch${NC}"
read -p "Continue with push? (yes/no): " push_confirmation
if [ "$push_confirmation" != "yes" ]; then
    echo -e "${YELLOW}❌ Push cancelled. Your local changes are ready but not pushed.${NC}"
    echo -e "${YELLOW}   To push manually later, run: git push origin main --force${NC}"
    exit 0
fi

git push origin $NEW_BRANCH --force
echo -e "${GREEN}✅ Pushed to GitHub successfully!${NC}"

echo ""
echo -e "${CYAN}=================================================${NC}"
echo -e "${GREEN}✅ Migration Completed Successfully!${NC}"
echo -e "${CYAN}=================================================${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo ""
echo -e "${YELLOW}1. Update Repository Settings on GitHub:${NC}"
echo -e "   - Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings"
echo -e "   - Update description: 'React + TypeScript frontend for Safe Drive Africa Data Hub'"
echo -e "   - Add topics: react, typescript, vite, safe-driving, africa"
echo ""
echo -e "${YELLOW}2. Configure GitHub Secrets (Required for CI/CD):${NC}"
echo -e "   - See: .github/SECRETS.md for complete list"
echo -e "   - Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings/secrets/actions"
echo ""
echo -e "${YELLOW}3. Set up Branch Protection:${NC}"
echo -e "   - Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings/branches"
echo -e "   - Add rule for 'main' branch"
echo -e "   - Enable: Require pull request reviews, Require status checks"
echo ""
echo -e "${YELLOW}4. Verify CI/CD Pipeline:${NC}"
echo -e "   - Go to: https://github.com/iniakponode/safe-drive-africa-datahub/actions"
echo -e "   - After configuring secrets, push a test commit"
echo ""
echo -e "${YELLOW}5. Archive Branch Access:${NC}"
echo -e "   - Old Python code: https://github.com/iniakponode/safe-drive-africa-datahub/tree/$ARCHIVE_BRANCH"
echo ""
echo -e "${CYAN}Documentation:${NC}"
echo -e "  - Deployment Guide: DEPLOYMENT.md"
echo -e "  - Quick Reference: QUICKSTART.md"
echo -e "  - CI/CD Overview: CI_CD_README.md"
echo ""
echo -e "${GREEN}🎉 Your React frontend is now live at:${NC}"
echo -e "${GREEN}   https://github.com/iniakponode/safe-drive-africa-datahub${NC}"
echo ""
