#!/bin/bash
# setup.sh - Setup and run script for development

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚦 Smart City Traffic Management System - Setup${NC}"
echo "================================================"

# Check Python version
echo -e "${BLUE}✓ Checking Python version...${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "  Python: $python_version"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}✓ Creating virtual environment...${NC}"
    python -m venv venv
else
    echo -e "${BLUE}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}✓ Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo -e "${BLUE}✓ Installing requirements...${NC}"
pip install --upgrade pip setuptools
pip install -r requirements.txt

# Download YOLO model
echo -e "${BLUE}✓ Downloading YOLO model...${NC}"
python -c "from ultralytics import YOLO; model = YOLO('yolov8s.pt'); print('✅ Model downloaded')" 2>/dev/null || echo "⚠️  Model download may take a moment..."

# Check static files
echo -e "${BLUE}✓ Checking for video files in static/...${NC}"
if [ -f "static/traffic1.mp4" ]; then
    echo "  ✅ traffic1.mp4 found"
else
    echo "  ⚠️  traffic1.mp4 NOT found"
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "To run the application:"
echo "  python app.py"
echo ""
echo "Dashboard will be available at:"
echo "  http://localhost:5000"
echo ""
