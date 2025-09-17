#!/bin/bash

# LexLeaks Service Starter Script
# This script starts all necessary services for development

echo "🚀 Starting LexLeaks Services"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start service in background
start_service() {
    local name=$1
    local cmd=$2
    local port=$3
    
    echo -e "${BLUE}🔧 Starting $name...${NC}"
    
    if check_port $port; then
        echo -e "${YELLOW}⚠️  $name already running on port $port${NC}"
        return 0
    fi
    
    # Start service in background
    eval "$cmd" &
    local pid=$!
    
    # Wait a moment and check if it started
    sleep 2
    if check_port $port; then
        echo -e "${GREEN}✅ $name started successfully (PID: $pid)${NC}"
        echo $pid > ".${name,,}_pid"
        return 0
    else
        echo -e "${RED}❌ Failed to start $name${NC}"
        return 1
    fi
}

echo ""
echo "🔍 Checking Current Status:"
echo "==========================="

# Check if services are already running
if check_port 8000; then
    echo -e "${GREEN}✅ Backend API already running on port 8000${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API not running${NC}"
fi

if check_port 3000; then
    echo -e "${GREEN}✅ Frontend already running on port 3000${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend not running${NC}"
fi

echo ""
echo "🏗️  Starting Backend API:"
echo "========================"

cd backend-api

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start backend API
start_service "Backend API" "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" 8000

cd ..

echo ""
echo "🌐 Starting Frontend:"
echo "===================="

cd frontend-lexleaks

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found. Installing...${NC}"
    npm install
fi

# Start frontend
start_service "Frontend" "npm run dev" 3000

cd ..

echo ""
echo "📊 Service Status:"
echo "================="

# Check all services
echo -n "Backend API (port 8000): "
if check_port 8000; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

echo -n "Frontend (port 3000): "
if check_port 3000; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

echo ""
echo "🔗 Access URLs:"
echo "==============="
echo -e "${GREEN}• Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}• Backend API: http://localhost:8000${NC}"
echo -e "${GREEN}• API Docs: http://localhost:8000/docs${NC}"
echo -e "${GREEN}• Health Check: http://localhost:8000/health${NC}"

echo ""
echo "🛑 To stop services:"
echo "==================="
echo "• Kill backend: kill \$(cat .backend_api_pid 2>/dev/null) 2>/dev/null"
echo "• Kill frontend: kill \$(cat .frontend_pid 2>/dev/null) 2>/dev/null"
echo "• Or use: pkill -f 'uvicorn\|next'"

echo ""
echo "🎉 Services started successfully!"
echo "================================"
