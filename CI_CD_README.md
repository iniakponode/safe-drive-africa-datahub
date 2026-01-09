# Safe Drive Africa Data Hub - CI/CD Pipeline

This repository includes a complete CI/CD pipeline for automated deployment to production.

## 📋 What's Included

### GitHub Actions Workflows
- **Production Deployment**: Automatic deployment when pushing to `main` branch
- **Staging Deployment**: Automatic deployment when pushing to `develop` branch  
- **Pull Request Checks**: Automatic linting and build verification for all PRs

### Deployment Scripts
- **`scripts/deploy.sh`**: Manual deployment script for local builds
- **`scripts/rollback.sh`**: Quick rollback to previous versions

### Docker Support
- **`Dockerfile`**: Multi-stage build for containerized deployment
- **`docker-compose.yml`**: Docker Compose configuration
- **`nginx.conf`**: Nginx configuration for SPA routing

### Configuration Files
- **`.github/workflows/`**: GitHub Actions workflow definitions
- **`.github/dependabot.yml`**: Automatic dependency updates
- **`public/.htaccess`**: Apache configuration for SPA routing

### Documentation
- **`DEPLOYMENT.md`**: Complete deployment guide with troubleshooting
- **`QUICKSTART.md`**: Quick reference for common tasks
- **`.github/SECRETS.md`**: GitHub Secrets configuration guide

## 🚀 Quick Setup

1. **Configure GitHub Secrets** (see [`.github/SECRETS.md`](.github/SECRETS.md))
   - VPS connection details
   - SSH authentication
   - API URLs

2. **Prepare Server** (see [`DEPLOYMENT.md`](DEPLOYMENT.md))
   - Create application directories
   - Set up backup directories
   - Configure web server

3. **Deploy**
   ```bash
   git push origin main  # Triggers automatic deployment
   ```

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference
- **[.github/SECRETS.md](.github/SECRETS.md)** - GitHub Secrets setup

## 🔄 Deployment Process

1. **Test** - Run linting and type checks
2. **Build** - Build production bundle
3. **Backup** - Create backup of current deployment
4. **Deploy** - Copy new files to server
5. **Verify** - Run health check

## 🛡️ Features

- ✅ Automated testing and building
- ✅ Automatic backups before deployment
- ✅ Quick rollback capability
- ✅ Health checks after deployment
- ✅ Manual deployment option
- ✅ Staging environment support
- ✅ Docker support
- ✅ Dependency updates via Dependabot

## 📞 Support

For deployment issues, see the troubleshooting section in [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

**Production URL**: https://datahub.safedriveafrica.com  
**API Backend**: https://api.safedriveafrica.com
