#!/bin/bash

# Setup script for Session-Based Recommendation System

set -e

echo "=================================="
echo "Session-Rec-Engine Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Error: Python 3.10+ is required"
    exit 1
fi
echo "✓ Python version OK"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Copy .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created (you can customize it if needed)"
else
    echo "✓ .env file already exists"
fi
echo ""

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "To start the system, you have two options:"
echo ""
echo "Option 1: Using Docker Compose (Recommended)"
echo "  docker-compose up -d"
echo ""
echo "Option 2: Manual setup"
echo "  1. Start Redis: redis-server"
echo "  2. Start Qdrant: docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant"
echo "  3. Start API: python main.py"
echo ""
echo "Then visit: http://localhost:8000/docs for API documentation"
echo ""
