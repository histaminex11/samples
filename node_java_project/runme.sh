#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Node.js + Java Full-Stack Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Java version
check_java() {
    if ! command_exists java; then
        echo -e "${RED}❌ Java is not installed${NC}"
        echo "Please install Java 17 or higher:"
        echo "  macOS: brew install openjdk@17"
        echo "  Ubuntu: sudo apt-get install openjdk-17-jdk"
        return 1
    fi
    
    JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
    if [ "$JAVA_VERSION" -lt 17 ]; then
        echo -e "${RED}❌ Java version is too old (found: $JAVA_VERSION, required: 17+)${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Java $(java -version 2>&1 | head -n 1)${NC}"
    return 0
}

# Function to check Maven
check_maven() {
    if ! command_exists mvn; then
        echo -e "${RED}❌ Maven is not installed${NC}"
        echo "Please install Maven:"
        echo "  macOS: brew install maven"
        echo "  Ubuntu: sudo apt-get install maven"
        return 1
    fi
    
    echo -e "${GREEN}✅ Maven $(mvn -version | head -n 1)${NC}"
    return 0
}

# Function to check Node.js
check_node() {
    if ! command_exists node; then
        echo -e "${RED}❌ Node.js is not installed${NC}"
        echo "Please install Node.js 16 or higher:"
        echo "  Visit: https://nodejs.org/"
        return 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        echo -e "${RED}❌ Node.js version is too old (found: $NODE_VERSION, required: 16+)${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Node.js $(node -v)${NC}"
    return 0
}

# Function to check npm
check_npm() {
    if ! command_exists npm; then
        echo -e "${RED}❌ npm is not installed${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ npm $(npm -v)${NC}"
    return 0
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
echo ""

PREREQS_OK=true

if ! check_java; then
    PREREQS_OK=false
fi

if ! check_maven; then
    PREREQS_OK=false
fi

if ! check_node; then
    PREREQS_OK=false
fi

if ! check_npm; then
    PREREQS_OK=false
fi

echo ""

if [ "$PREREQS_OK" = false ]; then
    echo -e "${RED}❌ Prerequisites check failed. Please install missing dependencies.${NC}"
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies (Maven)...${NC}"
cd "$BACKEND_DIR"
if mvn clean install -DskipTests > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Maven install had warnings, continuing...${NC}"
    mvn clean install -DskipTests
fi
cd "$SCRIPT_DIR"
echo ""

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies (npm)...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    if npm install > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  npm install had warnings, continuing...${NC}"
        npm install
    fi
else
    echo -e "${GREEN}✅ Frontend dependencies already installed${NC}"
fi
cd "$SCRIPT_DIR"
echo ""

# Check if ports are available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 1
    else
        return 0
    fi
}

# Kill processes on ports if they exist
echo -e "${YELLOW}Checking for existing processes on ports 8080 and 5173...${NC}"
if ! check_port 8080; then
    echo -e "${YELLOW}⚠️  Port 8080 is in use. Attempting to free it...${NC}"
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if ! check_port 5173; then
    echo -e "${YELLOW}⚠️  Port 5173 is in use. Attempting to free it...${NC}"
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    sleep 2
fi
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Start backend server
echo -e "${YELLOW}Starting backend server (Spring Boot)...${NC}"
cd "$BACKEND_DIR"
mvn spring-boot:run > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for backend to start
echo -e "${BLUE}Waiting for backend to start on port 8080...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8080/api/greeting > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend server is running on http://localhost:8080${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend server failed to start. Check logs: /tmp/backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done
echo ""

# Start frontend server
echo -e "${YELLOW}Starting frontend server (Vite)...${NC}"
cd "$FRONTEND_DIR"
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for frontend to start
echo -e "${BLUE}Waiting for frontend to start on port 5173...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend server is running on http://localhost:5173${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Frontend server failed to start. Check logs: /tmp/frontend.log${NC}"
        kill $BACKEND_PID 2>/dev/null
        kill $FRONTEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done
echo ""

# Test the API
echo -e "${YELLOW}Testing API connection...${NC}"
API_RESPONSE=$(curl -s http://localhost:8080/api/greeting)
if echo "$API_RESPONSE" | grep -q "Hello from the Java backend"; then
    echo -e "${GREEN}✅ API is responding correctly${NC}"
    echo -e "${BLUE}   Response: $API_RESPONSE${NC}"
else
    echo -e "${YELLOW}⚠️  API test inconclusive${NC}"
fi
echo ""

# Success message
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ Application is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}Backend API:${NC} http://localhost:8080/api/greeting"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Wait for user interrupt
wait
