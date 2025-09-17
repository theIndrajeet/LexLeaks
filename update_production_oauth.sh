#!/bin/bash

# Update Production OAuth Configuration Script
# This script updates the Cloud Run environment variables for production OAuth

echo "🚀 Updating Production OAuth Configuration"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud CLI not found. Please install it first.${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated with Google Cloud. Please run: gcloud auth login${NC}"
    exit 1
fi

echo ""
echo "🔧 Updating Cloud Run Environment Variables:"
echo "============================================"

# Set the service name and region
SERVICE_NAME="lexleaks-api"
REGION="asia-south1"
PROJECT_ID="563011146464"

echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "Project: $PROJECT_ID"

# Update environment variables
echo ""
echo "Setting production environment variables..."

# Update FRONTEND_URL
echo -n "Setting FRONTEND_URL... "
if gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --set-env-vars="FRONTEND_URL=https://lexleaks.com" \
    --quiet; then
    echo -e "${GREEN}✅ Success${NC}"
else
    echo -e "${RED}❌ Failed${NC}"
fi

# Update GOOGLE_REDIRECT_URI
echo -n "Setting GOOGLE_REDIRECT_URI... "
if gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --set-env-vars="GOOGLE_REDIRECT_URI=https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/callback" \
    --quiet; then
    echo -e "${GREEN}✅ Success${NC}"
else
    echo -e "${RED}❌ Failed${NC}"
fi

echo ""
echo "📋 Current Environment Variables:"
echo "================================"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)" | while read name value; do
    if [[ -n "$name" && -n "$value" ]]; then
        echo "• $name: $value"
    fi
done

echo ""
echo "🎯 Next Steps:"
echo "============="
echo "1. ✅ Cloud Run environment variables updated"
echo "2. 🔧 Update Google OAuth Console:"
echo "   • Go to: https://console.developers.google.com/"
echo "   • Add redirect URI: https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/callback"
echo "3. 🚀 Test OAuth flow on: https://lexleaks.com"

echo ""
echo "🔗 Production OAuth URLs:"
echo "========================"
echo "• Frontend: https://lexleaks.com"
echo "• Backend: https://lexleaks-api-563011146464.asia-south1.run.app"
echo "• OAuth Callback: https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/callback"

echo ""
echo -e "${GREEN}🎉 Production OAuth configuration update complete!${NC}"
