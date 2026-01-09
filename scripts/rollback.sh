#!/bin/bash

# Safe Drive Africa - Rollback Script
# Usage: ./scripts/rollback.sh [backup-timestamp]

set -e

if [ -z "$1" ]; then
    echo "Available backups:"
    ssh $VPS_USER@$VPS_HOST "ls -lt /var/backups/safedriveafrica/ | head -10"
    echo ""
    echo "Usage: ./scripts/rollback.sh [backup-timestamp]"
    echo "Example: ./scripts/rollback.sh 20260109_143000"
    exit 1
fi

BACKUP_TIMESTAMP=$1
VPS_HOST=${VPS_HOST:-"your-vps-host"}
VPS_USER=${VPS_USER:-"root"}
APP_DIR=${APP_DIR:-"/var/www/vhosts/safedriveafrica.com/httpdocs/datahub"}

echo "🔄 Rolling back to backup: $BACKUP_TIMESTAMP"

ssh $VPS_USER@$VPS_HOST << EOF
    BACKUP_DIR="/var/backups/safedriveafrica/$BACKUP_TIMESTAMP"
    APP_DIR="$APP_DIR"
    
    if [ ! -d "\$BACKUP_DIR" ]; then
        echo "❌ Backup not found: \$BACKUP_DIR"
        exit 1
    fi
    
    echo "📦 Creating backup of current state..."
    CURRENT_BACKUP="/var/backups/safedriveafrica/rollback-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "\$CURRENT_BACKUP"
    cp -r "\$APP_DIR"/* "\$CURRENT_BACKUP/" || true
    
    echo "🔄 Restoring from backup..."
    rm -rf "\$APP_DIR"/*
    cp -r "\$BACKUP_DIR"/* "\$APP_DIR/"
    
    echo "🔒 Setting permissions..."
    chown -R www-data:www-data "\$APP_DIR"
    find "\$APP_DIR" -type d -exec chmod 755 {} \;
    find "\$APP_DIR" -type f -exec chmod 644 {} \;
    
    echo "✅ Rollback completed successfully!"
EOF

echo "✅ Rollback to $BACKUP_TIMESTAMP completed!"
echo "🌐 Check application at: https://datahub.safedriveafrica.com"
