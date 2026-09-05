#!/bin/bash
# ===========================================
# FraudShield AI - Setup Script
# ===========================================
# This script sets up the development environment
# Usage: ./scripts/setup.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "   FraudShield AI - Development Setup"
echo "=========================================="
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Check Node.js version
echo -e "${YELLOW}Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Setting up Backend...${NC}"
echo "-------------------------------------------"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created (using default mock providers)${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo -e "${YELLOW}Setting up Frontend...${NC}"
echo "-------------------------------------------"

# Install Node.js dependencies
cd frontend
echo "Installing Node.js dependencies..."
npm install --silent
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"

# Create frontend .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating frontend .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    echo -e "${GREEN}✓ Frontend .env.local created${NC}"
else
    echo -e "${GREEN}✓ Frontend .env.local already exists${NC}"
fi

cd ..

echo ""
echo "=========================================="
echo -e "${GREEN}   Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "  1. Start the backend (Terminal 1):"
echo -e "     ${YELLOW}source venv/bin/activate${NC}"
echo -e "     ${YELLOW}uvicorn app.main:app --reload --port 8000${NC}"
echo ""
echo "  2. Start the frontend (Terminal 2):"
echo -e "     ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo "  3. Open http://localhost:3000 in your browser"
echo ""
echo "Provider Configuration:"
echo "  - LLM Provider: mock (no API key needed)"
echo "  - Pattern Provider: local_json"
echo ""
echo "To use real AI providers, edit .env and set:"
echo "  - LLM_PROVIDER=azure_openai or openai"
echo "  - Add your API keys"
echo ""
