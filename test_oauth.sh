#!/bin/bash

# Google OAuth Test Script for LexLeaks
# This script tests the OAuth flow and endpoints

echo "🔐 Google OAuth Test Script"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK (HTTP $response)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $response)${NC}"
        return 1
    fi
}

echo ""
echo "🌐 Frontend Endpoints:"
echo "====================="
test_endpoint "http://localhost:3000" "Frontend Home"
test_endpoint "http://localhost:3000/auth/callback" "OAuth Callback Page"
test_endpoint "http://localhost:3000/auth/error" "OAuth Error Page"

echo ""
echo "🔧 Backend OAuth Endpoints:"
echo "=========================="
test_endpoint "http://localhost:8000/api/auth/google/login" "OAuth Login Endpoint"
test_endpoint "http://localhost:8000/api/auth/google/callback" "OAuth Callback Endpoint" 405

echo ""
echo "📋 OAuth Configuration:"
echo "======================"

# Check environment variables
echo -n "GOOGLE_CLIENT_ID: "
if [ -n "$(grep GOOGLE_CLIENT_ID /Users/issac/Downloads/LexLeaks/backend-api/.env)" ]; then
    echo -e "${GREEN}✅ Set${NC}"
else
    echo -e "${RED}❌ Missing${NC}"
fi

echo -n "GOOGLE_CLIENT_SECRET: "
if [ -n "$(grep GOOGLE_CLIENT_SECRET /Users/issac/Downloads/LexLeaks/backend-api/.env)" ]; then
    echo -e "${GREEN}✅ Set${NC}"
else
    echo -e "${RED}❌ Missing${NC}"
fi

echo -n "GOOGLE_REDIRECT_URI: "
redirect_uri=$(grep GOOGLE_REDIRECT_URI /Users/issac/Downloads/LexLeaks/backend-api/.env | cut -d'=' -f2)
if [ -n "$redirect_uri" ]; then
    echo -e "${GREEN}✅ $redirect_uri${NC}"
else
    echo -e "${RED}❌ Missing${NC}"
fi

echo ""
echo "🔗 OAuth Flow Test:"
echo "=================="

# Test OAuth login endpoint
echo "Testing OAuth login endpoint..."
oauth_response=$(curl -s http://localhost:8000/api/auth/google/login)
if echo "$oauth_response" | grep -q "authorization_url"; then
    echo -e "${GREEN}✅ OAuth login endpoint working${NC}"
    
    # Extract authorization URL
    auth_url=$(echo "$oauth_response" | jq -r '.authorization_url' 2>/dev/null)
    if [ -n "$auth_url" ] && [ "$auth_url" != "null" ]; then
        echo -e "${GREEN}✅ Authorization URL generated${NC}"
        echo "   URL: $auth_url"
    else
        echo -e "${RED}❌ Failed to generate authorization URL${NC}"
    fi
else
    echo -e "${RED}❌ OAuth login endpoint failed${NC}"
fi

echo ""
echo "📊 Service Status:"
echo "================="
echo -n "Frontend (port 3000): "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

echo -n "Backend (port 8000): "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

echo ""
echo "🎯 OAuth Flow Summary:"
echo "====================="
echo "1. User clicks 'Continue with Google'"
echo "2. Frontend calls: http://localhost:8000/api/auth/google/login"
echo "3. Backend redirects to Google OAuth"
echo "4. Google redirects to: http://localhost:8000/api/auth/google/callback"
echo "5. Backend processes callback and redirects to: http://localhost:3000/auth/callback"
echo "6. Frontend handles final authentication"

echo ""
echo "🚀 Ready for OAuth Testing!"
echo "=========================="
echo "• Frontend: http://localhost:3000"
echo "• Backend API: http://localhost:8000"
echo "• OAuth Login: http://localhost:8000/api/auth/google/login"
echo ""
echo "To test OAuth flow:"
echo "1. Open http://localhost:3000"
echo "2. Click 'Continue with Google'"
echo "3. Complete Google authentication"
echo "4. You should be redirected back to the frontend"
