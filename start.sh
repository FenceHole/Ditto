#!/bin/bash

# Marketplace Bot Analyzer - Startup Script

echo "🤖 Starting Marketplace Bot Analyzer..."
echo ""

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env and add your ANTHROPIC_API_KEY"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt
echo "✓ Dependencies installed"
echo ""

# Start the backend server
echo "🚀 Starting backend server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""
echo "🌐 Open frontend/marketplace-app.html in your browser to get started"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python main.py
