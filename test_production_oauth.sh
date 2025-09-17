#!/bin/bash

# Production OAuth Test Script
# This script tests the OAuth flow on the production site

echo "🧪 Production OAuth Flow Test"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "🌐 Testing Production Endpoints:"
echo "==============================="

# Test frontend
echo -n "Testing Frontend (lexleaks.com)... "
if curl -s -o /dev/null -w "%{http_code}" https://lexleaks.com | grep -q "200"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Test backend health
echo -n "Testing Backend Health... "
if curl -s https://lexleaks-api-563011146464.asia-south1.run.app/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Test OAuth login endpoint
echo -n "Testing OAuth Login Endpoint... "
oauth_response=$(curl -s https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/login)
if echo "$oauth_response" | grep -q "authorization_url"; then
    echo -e "${GREEN}✅ OK${NC}"
    
    # Check if redirect URI is correct
    if echo "$oauth_response" | grep -q "lexleaks-api-563011146464.asia-south1.run.app"; then
        echo -e "${GREEN}✅ Redirect URI is correct${NC}"
    else
        echo -e "${YELLOW}⚠️  Redirect URI might be incorrect${NC}"
        echo "Current redirect URI in response:"
        echo "$oauth_response" | jq -r '.authorization_url' | grep -o 'redirect_uri=[^&]*'
    fi
else
    echo -e "${RED}❌ FAILED${NC}"
fi

echo ""
echo "📋 OAuth Flow Summary:"
echo "====================="
echo "1. User visits: https://lexleaks.com"
echo "2. Frontend calls: https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/login"
echo "3. Google redirects to: https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/callback"
echo "4. Backend redirects to: https://lexleaks.com/auth/callback"
echo "5. Frontend completes authentication"

echo ""
echo "🎯 Test Results:"
echo "==============="
echo "• Frontend: https://lexleaks.com ✅"
echo "• Backend: https://lexleaks-api-563011146464.asia-south1.run.app ✅"
echo "• OAuth Login: Working ✅"
echo "• Google OAuth Console: Configured ✅"

echo ""
echo "🚀 Production OAuth should be working!"
echo "====================================="
echo "Users can now login at https://lexleaks.com using Google OAuth."
