#!/bin/bash

echo ""
echo "========================================"
echo "  Marketplace Bot Analyzer"
echo "  Starting up..."
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "[!] .env file not found!"
    echo ""
    echo "Creating .env from template..."
    cp "backend/.env.simple" "backend/.env"
    echo ""
    echo "[!] IMPORTANT: Edit backend/.env and add your API keys!"
    echo ""
    echo "    1. Get Anthropic API key from: https://console.anthropic.com"
    echo "    2. Get Facebook tokens from: https://developers.facebook.com"
    echo "    3. Open backend/.env in a text editor"
    echo "    4. Fill in your API keys"
    echo "    5. Save and run this script again"
    echo ""
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "[!] Dependencies not installed. Installing now..."
    echo ""
    cd backend
    pip3 install -r requirements.txt
    cd ..
    echo ""
    echo "[OK] Dependencies installed!"
    echo ""
fi

# Start the backend server
echo ""
echo "========================================"
echo "  Starting Backend Server..."
echo "========================================"
echo ""
echo "Backend running at: http://localhost:8000"
echo "Frontend: Open frontend/marketplace-app.html"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd backend
python3 main.py
