#!/bin/bash

# LexLeaks Deployment Script
# This script handles complete deployment of the LexLeaks platform

echo "🚀 LexLeaks Deployment Script"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run command with error handling
run_command() {
    local cmd=$1
    local description=$2
    
    echo -e "${BLUE}📋 $description${NC}"
    echo "Running: $cmd"
    
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $description completed successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ $description failed${NC}"
        return 1
    fi
}

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "frontend-lexleaks" ] || [ ! -d "backend-api" ]; then
    echo -e "${RED}❌ Please run this script from the LexLeaks root directory${NC}"
    exit 1
fi

echo ""
echo "🔍 Pre-deployment Checks:"
echo "========================="

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo -e "${RED}❌ Netlify CLI not found. Installing...${NC}"
    npm install -g @netlify/cli
fi

# Check if we're logged into Netlify
if ! netlify status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged into Netlify. Please run: netlify login${NC}"
    exit 1
fi

echo ""
echo "🏗️  Building Frontend:"
echo "======================"

cd frontend-lexleaks

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    run_command "npm install" "Installing frontend dependencies"
fi

# Run type check
run_command "npm run type-check" "Running TypeScript type check"

# Build the frontend
run_command "npm run build" "Building frontend for production"

echo ""
echo "🚀 Deploying to Netlify:"
echo "========================"

# Deploy to Netlify
run_command "netlify deploy --prod" "Deploying to Netlify production"

echo ""
echo "🔧 Backend Health Check:"
echo "========================"

cd ../backend-api

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment and check backend
source venv/bin/activate

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Local backend is running${NC}"
else
    echo -e "${YELLOW}⚠️  Local backend not running. Starting...${NC}"
    echo "To start backend: cd backend-api && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
fi

cd ..

echo ""
echo "📊 Final Health Check:"
echo "======================"

# Run comprehensive health check
./health_check.sh

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo -e "${GREEN}✅ Frontend deployed to: https://lexleaks.com${NC}"
echo -e "${GREEN}✅ Backup URL: https://glittery-dragon-d3e69b.netlify.app${NC}"
echo -e "${GREEN}✅ Backend API: https://lexleaks-api-563011146464.asia-south1.run.app${NC}"
echo ""
echo "🔗 Useful Links:"
echo "  • Site: https://lexleaks.com"
echo "  • Admin: https://app.netlify.com/projects/glittery-dragon-d3e69b"
echo "  • API Docs: https://lexleaks-api-563011146464.asia-south1.run.app/docs"
echo ""
echo "📝 Next Steps:"
echo "  • Configure DNS for lexleaks.com if needed"
echo "  • Set up monitoring and alerts"
echo "  • Test all functionality"
