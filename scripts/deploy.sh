#!/bin/bash

# Safe Drive Africa - Manual Deployment Script
# Usage: ./scripts/deploy.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 Starting deployment to $ENVIRONMENT..."

# Load environment variables
if [ "$ENVIRONMENT" = "production" ]; then
    API_URL="https://api.safedriveafrica.com"
    DEPLOY_PATH="/var/www/vhosts/safedriveafrica.com/datahub"
elif [ "$ENVIRONMENT" = "staging" ]; then
    API_URL="https://staging.api.safedriveafrica.com"
    DEPLOY_PATH="/var/www/vhosts/safedriveafrica.com/staging.datahub"
else
    echo "❌ Invalid environment: $ENVIRONMENT"
    exit 1
fi

# Create production .env
echo "📝 Creating environment file..."
cat > .env.production << EOF
VITE_API_URL=$API_URL
VITE_ENV=$ENVIRONMENT
EOF

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Run checks
echo "🔍 Running linter..."
npm run lint

echo "🔍 Running type check..."
npm run type-check

# Build
echo "🏗️  Building application..."
npm run build

# Create deployment archive
echo "📦 Creating deployment archive..."
tar -czf "dist-$TIMESTAMP.tar.gz" -C dist .

echo "✅ Build completed successfully!"
echo "📦 Archive: dist-$TIMESTAMP.tar.gz"
echo ""
echo "To deploy manually to the server:"
echo "1. Upload dist-$TIMESTAMP.tar.gz to the server"
echo "2. SSH into the server"
echo "3. Extract: tar -xzf dist-$TIMESTAMP.tar.gz -C $DEPLOY_PATH"
echo "4. Set permissions: chown -R www-data:www-data $DEPLOY_PATH"
