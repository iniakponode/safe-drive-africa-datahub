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
**From your Plesk**: 216.225.195.203
```
Value: 216.225.195.203
```

### VPS_USERNAME
**Description**: SSH username for deployment (use root - has SSH access)
```
Value: root
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
**Example**: `/var/www/vhosts/safedriveafrica.com/datahub.safedriveafrica.com`
**Note**: This is the document root for your subdomain (no httpdocs subfolder)
```
Value: /var/www/vhosts/safedriveafrica.com/datahub.safedriveafrica.com
```

### PLESK_USER
**Description**: Web server user for file ownership
**From your Plesk System user's credentials**: safedriveafrica.com_vt8emkn07gl
```
Value: safedriveafrica.com_vt8emkn07gl
```

### PLESK_GROUP
**Description**: Web server group for file ownership
**For IONOS/Plesk**: Usually `psacln` or `psaserv`
```
Value: psacln
```

### VITE_API_BASE_URL
**Description**: Production API URL (used by React app at build time)
```
Value: https://api.safedriveafrica.com
```

## Optional Secrets (for Staging)

### STAGING_API_BASE_URL
**Description**: Staging API URL
```
Value: https://staging.api.safedriveafrica.com
```

### STAGING_APP_DIR
**Description**: Staging directory path (if you create a staging subdomain)
```
Value: /var/www/vhosts/safedriveafrica.com/staging.datahub.safedriveafrica.com
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
