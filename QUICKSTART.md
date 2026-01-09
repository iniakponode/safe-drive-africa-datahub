# CI/CD Pipeline Quick Reference

## Quick Start Checklist

- [ ] Configure all GitHub Secrets (see `.github/SECRETS.md`)
- [ ] Set up server directories
- [ ] Configure web server (Apache/Nginx)
- [ ] Test SSH connection
- [ ] Run first deployment

## Deployment Commands

### Automatic Deployments
```bash
# Production (push to main branch)
git push origin main

# Staging (push to develop branch)  
git push origin develop
```

### Manual Deployment via GitHub
1. Go to **Actions** tab
2. Select **Deploy to Production**
3. Click **Run workflow**
4. Select branch and confirm

### Manual Build & Deploy
```bash
# Build locally
npm ci
npm run build

# Deploy using script
chmod +x scripts/deploy.sh
./scripts/deploy.sh production
```

## Rollback
```bash
# List available backups
ssh user@vps "ls -lt /var/backups/safedriveafrica/"

# Rollback to specific backup
export VPS_HOST="your-host"
export VPS_USER="root"
./scripts/rollback.sh 20260109_143000
```

## Common Issues

### Permission errors
```bash
ssh user@vps
chown -R www-data:www-data /var/www/vhosts/safedriveafrica.com/httpdocs/datahub
chmod -R 755 /var/www/vhosts/safedriveafrica.com/httpdocs/datahub
```

### SPA routing (404 on refresh)
Ensure `.htaccess` is deployed and mod_rewrite is enabled

### Blank page after deployment
Check browser console and verify VITE_API_URL is correct

## Monitoring

- **Production**: https://datahub.safedriveafrica.com
- **GitHub Actions**: Repository → Actions tab
- **Server Logs**: `ssh user@vps "tail -f /var/log/apache2/error.log"`

## Support Files

- **Full Guide**: `DEPLOYMENT.md`
- **Secrets Setup**: `.github/SECRETS.md`
- **Docker**: `Dockerfile` and `docker-compose.yml`
- **Scripts**: `scripts/deploy.sh`, `scripts/rollback.sh`
