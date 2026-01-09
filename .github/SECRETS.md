# GitHub Secrets Setup Guide

This file documents all the GitHub Secrets required for CI/CD deployment.

## How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below

## Required Secrets

### VPS_HOST
**Description**: Your IONOS VPS IP address or hostname
**Example**: `123.45.67.89` or `server.safedriveafrica.com`
```
Value: <your-vps-host>
```

### VPS_USERNAME
**Description**: SSH username for deployment (typically root or a dedicated deploy user)
**Example**: `root` or `safedriveafrica`
```
Value: <your-ssh-username>
```

### VPS_SSH_KEY
**Description**: Private SSH key for authentication
**How to generate**:
```bash
ssh-keygen -t ed25519 -C "github-actions@safedriveafrica.com" -f ~/.ssh/safedriveafrica_deploy
cat ~/.ssh/safedriveafrica_deploy
```
**Value**: Copy the entire private key including:
```
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

### VPS_PORT
**Description**: SSH port (usually 22)
```
Value: 22
```

### PLESK_APP_DIR
**Description**: Full path to application directory on server
**Example**: `/var/www/vhosts/safedriveafrica.com/httpdocs/datahub`
```
Value: <your-app-directory-path>
```

### PLESK_USER
**Description**: Web server user for file ownership
**Common values**: `www-data`, `apache`, `nginx`, or Plesk-specific user
```
Value: www-data
```

### PLESK_GROUP
**Description**: Web server group for file ownership
**Common values**: `www-data`, `psaserv`, `apache`, `nginx`
```
Value: www-data
```

### VITE_API_URL
**Description**: Production API URL
```
Value: https://api.safedriveafrica.com
```

## Optional Secrets (for Staging)

### STAGING_API_URL
**Description**: Staging API URL
```
Value: https://staging.api.safedriveafrica.com
```

### STAGING_APP_DIR
**Description**: Staging directory path
```
Value: /var/www/vhosts/safedriveafrica.com/httpdocs/staging.datahub
```

## Verification

After adding all secrets, verify they are correct:

1. Go to **Actions** tab
2. Manually trigger **Deploy to Production** workflow
3. Select **Run workflow** on `main` branch
4. Monitor the logs for any authentication or permission errors

## Security Notes

- Never commit actual secret values to the repository
- Rotate SSH keys periodically (every 6-12 months)
- Use dedicated deployment users with minimal permissions
- Enable 2FA on GitHub account
- Regularly review GitHub Actions logs for suspicious activity
