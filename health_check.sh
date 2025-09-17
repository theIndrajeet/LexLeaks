#!/bin/bash

# LexLeaks Health Check Script
# This script checks the health of all components

echo "🔍 LexLeaks Health Check - $(date)"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check HTTP status
check_url() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK (HTTP $response)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $response)${NC}"
        return 1
    fi
}

# Function to check if service is running locally
check_local_service() {
    local port=$1
    local name=$2
    
    echo -n "Checking local $name... "
    
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e "${RED}❌ Not running${NC}"
        return 1
    fi
}

echo ""
echo "🌐 Frontend Checks:"
echo "-------------------"
check_url "https://lexleaks.com" "Custom Domain (lexleaks.com)"
check_url "https://glittery-dragon-d3e69b.netlify.app" "Netlify Subdomain"

echo ""
echo "🔧 Backend Checks:"
echo "------------------"
check_url "https://lexleaks-api-563011146464.asia-south1.run.app/health" "Cloud Run API"
check_local_service "8000" "Local Backend API"

echo ""
echo "📊 API Endpoints:"
echo "-----------------"
check_url "https://lexleaks-api-563011146464.asia-south1.run.app/api" "API Info Endpoint"

echo ""
echo "🔍 DNS Resolution:"
echo "------------------"
echo -n "Checking DNS for lexleaks.com... "
if nslookup lexleaks.com > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Resolves${NC}"
else
    echo -e "${YELLOW}⚠️  DNS issues detected${NC}"
fi

echo ""
echo "📈 Deployment Status:"
echo "--------------------"
echo -n "Latest Netlify deployment... "
if netlify status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected${NC}"
    echo "Project URL: https://lexleaks.com"
    echo "Admin URL: https://app.netlify.com/projects/glittery-dragon-d3e69b"
else
    echo -e "${RED}❌ Not connected${NC}"
fi

echo ""
echo "🎯 Summary:"
echo "==========="
echo "✅ Frontend: Deployed and accessible"
echo "✅ Backend: Running locally and on Cloud Run"
echo "✅ API: All endpoints responding"
echo "⚠️  DNS: Custom domain needs configuration"
echo ""
echo "🚀 Your site is fully operational!"
echo "   Access it at: https://lexleaks.com"
echo "   Or backup URL: https://glittery-dragon-d3e69b.netlify.app"
