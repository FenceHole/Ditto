@echo off
echo.
echo ========================================
echo   Marketplace Bot Analyzer
echo   Starting up...
echo ========================================
echo.

REM Check if .env exists
if not exist "backend\.env" (
    echo [!] .env file not found!
    echo.
    echo Creating .env from template...
    copy "backend\.env.simple" "backend\.env"
    echo.
    echo [!] IMPORTANT: Edit backend\.env and add your API keys!
    echo.
    echo     1. Get Anthropic API key from: https://console.anthropic.com
    echo     2. Get Facebook tokens from: https://developers.facebook.com
    echo     3. Open backend\.env in Notepad
    echo     4. Fill in your API keys
    echo     5. Save and run this script again
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo.
    echo [!] Dependencies not installed. Installing now...
    echo.
    cd backend
    pip install -r requirements.txt
    cd ..
    echo.
    echo [OK] Dependencies installed!
    echo.
)

REM Start the backend server
echo.
echo ========================================
echo   Starting Backend Server...
echo ========================================
echo.
echo Backend running at: http://localhost:8000
echo Frontend: Open frontend\marketplace-app.html
echo.
echo Press Ctrl+C to stop
echo.

cd backend
python main.py
