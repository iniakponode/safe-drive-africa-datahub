# Deployment Guide - Safe Drive Africa Data Hub

## Overview

This guide covers the deployment process for the Safe Drive Africa Data Hub web client to production at `datahub.safedriveafrica.com`.

## Architecture

- **Frontend**: React + TypeScript + Vite
- **API Backend**: FastAPI at `api.safedriveafrica.com`
- **Hosting**: IONOS VPS with Plesk
- **CI/CD**: GitHub Actions
- **Deployment Strategy**: Automated deployment with backup and rollback capabilities

## Prerequisites

### Required Access

1. GitHub repository access with Actions enabled
2. SSH access to IONOS VPS
3. Plesk control panel access (optional but recommended)

### Required Tools

- Node.js 20.x
- npm or yarn
- SSH client
- Git

## GitHub Secrets Configuration

Configure the following secrets in your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `VPS_HOST` | IONOS VPS IP address or hostname | `123.45.67.89` or `server.safedriveafrica.com` |
| `VPS_USERNAME` | SSH username for deployment | `root` or `safedriveafrica` |
| `VPS_SSH_KEY` | Private SSH key for authentication | See SSH Key Setup below |
| `VPS_PORT` | SSH port number | `22` (default) |
| `PLESK_APP_DIR` | Application directory path | `/var/www/vhosts/safedriveafrica.com/httpdocs/datahub` |
| `PLESK_USER` | Web server user | `www-data` or Plesk user |
| `PLESK_GROUP` | Web server group | `www-data` or `psaserv` |
| `VITE_API_URL` | Production API URL | `https://api.safedriveafrica.com` |

### Optional Secrets (for staging)

| Secret Name | Description |
|------------|-------------|
| `STAGING_API_URL` | Staging API URL |
| `STAGING_APP_DIR` | Staging directory path |

## SSH Key Setup

### 1. Generate SSH Key Pair

```bash
ssh-keygen -t ed25519 -C "github-actions@safedriveafrica.com" -f ~/.ssh/safedriveafrica_deploy
```

When prompted:
- Enter a passphrase (optional, but recommended for local keys)
- For GitHub Actions, use a key WITHOUT a passphrase

### 2. Copy Public Key to Server

```bash
ssh-copy-id -i ~/.ssh/safedriveafrica_deploy.pub user@your-vps-host
```

Or manually:
```bash
cat ~/.ssh/safedriveafrica_deploy.pub
# Copy the output and add it to ~/.ssh/authorized_keys on the server
```

### 3. Add Private Key to GitHub

```bash
# Display private key
cat ~/.ssh/safedriveafrica_deploy
```

Copy the entire output (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`) and add it to GitHub Secrets as `VPS_SSH_KEY`.

### 4. Test SSH Connection

```bash
ssh -i ~/.ssh/safedriveafrica_deploy user@your-vps-host
```

## Server Setup

### 1. Create Application Directory

```bash
ssh user@your-vps-host

# Create main application directory
mkdir -p /var/www/vhosts/safedriveafrica.com/httpdocs/datahub

# Set ownership
chown -R www-data:www-data /var/www/vhosts/safedriveafrica.com/httpdocs/datahub

# Set permissions
chmod -R 755 /var/www/vhosts/safedriveafrica.com/httpdocs/datahub
```

### 2. Create Backup Directory

```bash
# Create backup directory
mkdir -p /var/backups/safedriveafrica

# Set permissions
chmod 755 /var/backups/safedriveafrica
```

### 3. Configure Plesk

1. Log in to Plesk control panel
2. Navigate to **Domains** → **safedriveafrica.com**
3. Click **Add Subdomain**
   - Subdomain name: `datahub`
   - Document root: `/var/www/vhosts/safedriveafrica.com/httpdocs/datahub`
4. Enable **SSL/TLS Certificate** (Let's Encrypt recommended)
5. Configure **Apache & nginx Settings**:
   - Enable **Proxy mode** (if using nginx + Apache)

### 4. Web Server Configuration

#### For Apache (with Plesk)

Plesk typically uses Apache. Create or verify `.htaccess` in the document root:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>

# Security headers
<IfModule mod_headers.c>
  Header set X-Frame-Options "SAMEORIGIN"
  Header set X-Content-Type-Options "nosniff"
  Header set X-XSS-Protection "1; mode=block"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/gif "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType font/woff "access plus 1 year"
  ExpiresByType font/woff2 "access plus 1 year"
</IfModule>
```

#### For Nginx (if using standalone)

Add to nginx site configuration:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
```

## Deployment Workflows

### Automatic Deployment

#### Production Deployment (from `main` branch)

1. Make changes in a feature branch
2. Create Pull Request to `main`
3. PR triggers automatic checks (linting, type-checking, build)
4. After PR approval and merge to `main`:
   - Tests run automatically
   - Application builds
   - Deploys to production
   - Backup created automatically
   - Health check performed

**URL**: https://datahub.safedriveafrica.com

#### Staging Deployment (from `develop` branch)

1. Merge feature branches to `develop`
2. Automatic deployment to staging environment
3. Test in staging before promoting to production

**URL**: https://staging.datahub.safedriveafrica.com (if configured)

### Manual Deployment

#### Via GitHub Actions UI

1. Go to **Actions** tab in GitHub repository
2. Select **Deploy to Production** workflow
3. Click **Run workflow**
4. Select branch (usually `main`)
5. Click **Run workflow** button
6. Monitor progress in Actions tab

#### Via Command Line

Using the deployment script:

```bash
# Navigate to project directory
cd drive_africa_data_hub_front

# Make script executable
chmod +x scripts/deploy.sh

# Deploy to production
./scripts/deploy.sh production

# Deploy to staging
./scripts/deploy.sh staging
```

The script will:
1. Create environment file
2. Install dependencies
3. Run linting and type checks
4. Build the application
5. Create a deployment archive
6. Provide instructions for manual upload

## Environment Variables

### Production (.env.production)

```env
VITE_API_URL=https://api.safedriveafrica.com
VITE_ENV=production
```

### Staging (.env.staging)

```env
VITE_API_URL=https://staging.api.safedriveafrica.com
VITE_ENV=staging
```

### Local Development (.env.local)

```env
VITE_API_URL=http://localhost:8000
VITE_ENV=development
```

## Rollback Procedure

If a deployment fails or introduces issues, you can rollback to a previous version.

### Via Script

```bash
# Make script executable
chmod +x scripts/rollback.sh

# Set environment variables
export VPS_HOST="your-vps-host"
export VPS_USER="root"
export APP_DIR="/var/www/vhosts/safedriveafrica.com/httpdocs/datahub"

# List available backups
./scripts/rollback.sh

# Rollback to specific backup
./scripts/rollback.sh 20260109_143000
```

### Manual Rollback

```bash
# SSH into server
ssh user@your-vps-host

# List available backups
ls -lt /var/backups/safedriveafrica/

# Identify backup to restore (timestamp format: YYYYMMDD_HHMMSS)
BACKUP_TIMESTAMP=20260109_143000

# Create backup of current state
CURRENT_BACKUP=/var/backups/safedriveafrica/rollback-$(date +%Y%m%d_%H%M%S)
mkdir -p $CURRENT_BACKUP
cp -r /var/www/vhosts/safedriveafrica.com/httpdocs/datahub/* $CURRENT_BACKUP/

# Restore from backup
rm -rf /var/www/vhosts/safedriveafrica.com/httpdocs/datahub/*
cp -r /var/backups/safedriveafrica/$BACKUP_TIMESTAMP/* /var/www/vhosts/safedriveafrica.com/httpdocs/datahub/

# Set proper permissions
chown -R www-data:www-data /var/www/vhosts/safedriveafrica.com/httpdocs/datahub
find /var/www/vhosts/safedriveafrica.com/httpdocs/datahub -type d -exec chmod 755 {} \;
find /var/www/vhosts/safedriveafrica.com/httpdocs/datahub -type f -exec chmod 644 {} \;
```

## Monitoring and Logging

### Application Monitoring

- **Production URL**: https://datahub.safedriveafrica.com
- **Health Check**: Automatic health check after each deployment
- **Browser Console**: Check for JavaScript errors

### GitHub Actions Logs

1. Go to **Actions** tab in repository
2. Select the workflow run
3. View logs for each job (Test, Build, Deploy)
4. Download logs if needed for debugging

### Server Logs

```bash
# SSH into server
ssh user@your-vps-host

# Apache error logs
tail -f /var/log/apache2/error.log

# Apache access logs
tail -f /var/log/apache2/access.log

# Nginx logs (if applicable)
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Plesk logs
tail -f /var/log/plesk/panel.log
```

## Troubleshooting

### Deployment Fails with Permission Error

```bash
ssh user@your-vps-host
chown -R www-data:www-data /var/www/vhosts/safedriveafrica.com/httpdocs/datahub
chmod -R 755 /var/www/vhosts/safedriveafrica.com/httpdocs/datahub
```

### Application Shows Blank Page

1. **Check browser console** for JavaScript errors
2. **Verify API URL** in environment variables
3. **Check network tab** for failed requests
4. **Verify static assets** are accessible:
   ```bash
   curl https://datahub.safedriveafrica.com/assets/index-[hash].js
   ```

### 404 Errors on Page Refresh

This indicates SPA routing is not configured properly.

**For Apache**, ensure `.htaccess` contains:
```apache
RewriteEngine On
RewriteBase /
RewriteRule ^index\.html$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]
```

**For Nginx**, ensure configuration contains:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### SSH Connection Fails

1. **Verify SSH key** is added to server:
   ```bash
   ssh -i ~/.ssh/safedriveafrica_deploy user@your-vps-host
   ```

2. **Check authorized_keys** on server:
   ```bash
   cat ~/.ssh/authorized_keys
   ```

3. **Verify SSH port** (default is 22, but may be changed for security)

### Build Fails in GitHub Actions

1. Check the **Actions logs** for specific error
2. Common issues:
   - Missing dependencies (run `npm ci` locally)
   - TypeScript errors (run `npm run type-check`)
   - Linting errors (run `npm run lint`)
   - Environment variables not set

### API Connection Issues

1. **Verify API is accessible**:
   ```bash
   curl https://api.safedriveafrica.com/health
   ```

2. **Check CORS settings** on API server
3. **Verify API URL** in environment variables
4. **Check browser console** for CORS errors

## Security Best Practices

1. **Never commit** `.env` files with sensitive data
2. **Rotate SSH keys** periodically
3. **Use strong passwords** for VPS access
4. **Enable firewall** on VPS (allow only necessary ports)
5. **Keep dependencies updated** (Dependabot helps with this)
6. **Use HTTPS** for all connections (Let's Encrypt)
7. **Regular backups** (automated by deployment process)
8. **Monitor access logs** for suspicious activity

## Maintenance Tasks

### Update Dependencies

```bash
# Check for outdated packages
npm outdated

# Update dependencies
npm update

# For major version updates, review changelogs
npm install package-name@latest
```

### Clean Old Backups

Backups are automatically cleaned (keeps last 5). To manually clean:

```bash
ssh user@your-vps-host
ls -lt /var/backups/safedriveafrica/
# Remove old backups
rm -rf /var/backups/safedriveafrica/[old-timestamp]
```

### SSL Certificate Renewal

If using Let's Encrypt via Plesk:
1. Plesk automatically renews certificates
2. Check status in Plesk: **Domains** → **SSL/TLS Certificates**

Manual renewal:
```bash
certbot renew
```

## Support and Contact

For deployment issues or questions:
- **Email**: dev@safedriveafrica.com
- **Repository**: [GitHub Repository URL]
- **Documentation**: This file

## Changelog

### Version 1.0.0 (January 2026)
- Initial CI/CD setup
- GitHub Actions workflows for production and staging
- Automated backup and rollback system
- Docker support
- Comprehensive documentation
