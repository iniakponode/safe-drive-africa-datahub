# Repository Migration Guide

This guide explains how to migrate from the Python FastAPI backend to this React frontend at the same GitHub repository.

## Quick Migration

### Using the Migration Script (Recommended)

**For Windows (PowerShell):**
```powershell
.\scripts\migrate-to-github.ps1
```

**For Linux/Mac:**
```bash
chmod +x scripts/migrate-to-github.sh
./scripts/migrate-to-github.sh
```

The script will:
1. ✅ Archive the Python FastAPI code in `archive/python-fastapi-v1` branch
2. ✅ Create a clean history for the React frontend
3. ✅ Push to GitHub replacing the main branch
4. ✅ Preserve all history in the archive branch

## Manual Migration Steps

If you prefer to migrate manually:

### Step 1: Add Remote Origin
```bash
git remote add origin https://github.com/iniakponode/safe-drive-africa-datahub.git
```

### Step 2: Fetch Existing Repository
```bash
git fetch origin
```

### Step 3: Archive Python Code
```bash
# Archive the existing main branch
git push origin origin/main:refs/heads/archive/python-fastapi-v1
```

### Step 4: Create Clean History
```bash
# Create orphan branch (no history)
git checkout --orphan new-main

# Add all React frontend files
git add .

# Create initial commit
git commit -m "feat: Initial React/TypeScript frontend

Replaces Python FastAPI implementation with modern React frontend.
Previous implementation archived in archive/python-fastapi-v1 branch."
```

### Step 5: Replace Main Branch
```bash
# Rename branch to main
git branch -M new-main main

# Force push to replace main branch
git push origin main --force
```

## Post-Migration Checklist

### 1. Update GitHub Repository Settings

Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings

- [ ] **Description**: "React + TypeScript frontend for Safe Drive Africa Data Hub"
- [ ] **Website**: https://datahub.safedriveafrica.com
- [ ] **Topics**: `react`, `typescript`, `vite`, `safe-driving`, `africa`, `datahub`
- [ ] **Include in home page**: ✓ Yes
- [ ] **Social preview**: Upload a screenshot

### 2. Configure GitHub Secrets

Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings/secrets/actions

See [`.github/SECRETS.md`](.github/SECRETS.md) for complete list. Required secrets:

- [ ] `VPS_HOST` - Your IONOS VPS hostname/IP
- [ ] `VPS_USERNAME` - SSH username
- [ ] `VPS_SSH_KEY` - Private SSH key for deployment
- [ ] `VPS_PORT` - SSH port (usually 22)
- [ ] `PLESK_APP_DIR` - Application directory path
- [ ] `PLESK_USER` - Web server user (www-data)
- [ ] `PLESK_GROUP` - Web server group (www-data)
- [ ] `VITE_API_URL` - Production API URL (https://api.safedriveafrica.com)

### 3. Set Up Branch Protection

Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings/branches

Create protection rule for `main` branch:

- [ ] **Require a pull request before merging**
  - [ ] Require approvals: 1
  - [ ] Dismiss stale pull request approvals when new commits are pushed
- [ ] **Require status checks to pass before merging**
  - [ ] Require branches to be up to date before merging
  - Status checks: `lint-and-type-check`, `build-check`
- [ ] **Require conversation resolution before merging**
- [ ] **Do not allow bypassing the above settings**

### 4. Create GitHub Environments

Go to: https://github.com/iniakponode/safe-drive-africa-datahub/settings/environments

**Production Environment:**
- [ ] Name: `production`
- [ ] URL: https://datahub.safedriveafrica.com
- [ ] Required reviewers: Add team members
- [ ] Wait timer: 0 minutes
- [ ] Deployment branches: Selected branches → `main`

**Staging Environment (Optional):**
- [ ] Name: `staging`
- [ ] URL: https://staging.datahub.safedriveafrica.com
- [ ] Deployment branches: Selected branches → `develop`

### 5. Update README

The current README should be updated to reflect the new frontend:

- [ ] Update project description
- [ ] Add installation instructions
- [ ] Add development setup guide
- [ ] Document API integration
- [ ] Add deployment instructions reference

### 6. Add Archive Notice to Old Python Branch

Create `ARCHIVE_NOTICE.md` in the `archive/python-fastapi-v1` branch:

```markdown
# ⚠️ ARCHIVED - Python FastAPI Implementation

This branch contains the legacy Python FastAPI backend implementation.

## Current Status
**Status**: ARCHIVED  
**Archived Date**: January 9, 2026  
**Reason**: Replaced with React + TypeScript frontend

## Current Implementation
The production system now uses:
- **Frontend**: React + TypeScript (main branch)
- **Repository**: [Main Branch](https://github.com/iniakponode/safe-drive-africa-datahub)
- **Production URL**: https://datahub.safedriveafrica.com
- **API Backend**: https://api.safedriveafrica.com

## This Archive
This branch preserves the original Python FastAPI implementation for:
- Reference purposes
- Historical record
- Emergency rollback (if needed)

## Migration Information
See [MIGRATION.md](../main/MIGRATION.md) for migration details.

---
For questions, contact: dev@safedriveafrica.com
```

### 7. Test CI/CD Pipeline

After configuring secrets:

```bash
# Make a test change
echo "# Safe Drive Africa Data Hub" > README.md
git add README.md
git commit -m "docs: Update README"
git push origin main

# Go to Actions tab and monitor deployment
# https://github.com/iniakponode/safe-drive-africa-datahub/actions
```

### 8. Verify Deployment

After successful deployment:

- [ ] Visit https://datahub.safedriveafrica.com
- [ ] Test all main features
- [ ] Verify API connectivity
- [ ] Check browser console for errors
- [ ] Test on multiple browsers
- [ ] Test on mobile devices

### 9. Update Documentation Links

Update any external documentation that references the old repository structure:

- [ ] Wiki pages
- [ ] Confluence/Notion docs
- [ ] Team documentation
- [ ] Deployment runbooks
- [ ] API documentation

### 10. Notify Team

Send notification to team members:

```
Subject: Repository Migration Complete - Safe Drive Africa Data Hub

Hi Team,

The Safe Drive Africa Data Hub repository has been successfully migrated 
from Python FastAPI to React + TypeScript frontend.

Repository: https://github.com/iniakponode/safe-drive-africa-datahub
Production: https://datahub.safedriveafrica.com

Key Changes:
- Frontend: React 19 + TypeScript + Vite
- CI/CD: GitHub Actions with automated deployment
- Archive: Old Python code preserved in archive/python-fastapi-v1 branch

Documentation:
- Deployment Guide: DEPLOYMENT.md
- Quick Reference: QUICKSTART.md
- Migration Guide: MIGRATION.md

Please review the new setup and reach out with any questions.

Thanks!
```

## Accessing Archived Python Code

The original Python FastAPI implementation is preserved at:

**Branch**: `archive/python-fastapi-v1`  
**URL**: https://github.com/iniakponode/safe-drive-africa-datahub/tree/archive/python-fastapi-v1

To checkout locally:
```bash
git fetch origin archive/python-fastapi-v1
git checkout archive/python-fastapi-v1
```

## Rollback (Emergency)

If you need to restore the Python implementation:

```bash
# Checkout archive branch
git checkout archive/python-fastapi-v1

# Create new main from archive
git checkout -b restore-python
git push origin restore-python:main --force

# Update deployment configuration accordingly
```

## Troubleshooting

### Migration Script Fails

**Issue**: "fatal: not a git repository"
```bash
git init
# Run migration script again
```

**Issue**: "Permission denied (publickey)"
```bash
# Configure GitHub credentials
gh auth login
# Or set up SSH keys
ssh-keygen -t ed25519 -C "your_email@example.com"
```

**Issue**: "Updates were rejected because the remote contains work"
- This is expected when force-pushing
- Ensure you've confirmed the force push in the script

### Post-Migration Issues

**Issue**: Actions not running
- Verify GitHub Secrets are configured
- Check workflow files in `.github/workflows/`
- Ensure repository has Actions enabled

**Issue**: Deployment fails
- Check server connectivity: `ssh user@vps-host`
- Verify server directories exist
- Review deployment logs in GitHub Actions

## Support

For migration issues:
- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: https://github.com/iniakponode/safe-drive-africa-datahub/issues
- **Email**: dev@safedriveafrica.com

## Migration Checklist Summary

Print this checklist and check off as you complete each item:

- [ ] Run migration script
- [ ] Update repository settings
- [ ] Configure GitHub Secrets (8 secrets)
- [ ] Set up branch protection
- [ ] Create GitHub environments
- [ ] Update README
- [ ] Add archive notice
- [ ] Test CI/CD pipeline
- [ ] Verify deployment
- [ ] Update documentation links
- [ ] Notify team
- [ ] Celebrate! 🎉
