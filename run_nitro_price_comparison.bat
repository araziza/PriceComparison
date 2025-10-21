@echo off
echo ============================================
echo Nitro Price Comparison Tool
echo ============================================
echo.
echo Starting the application...
echo The dashboard will open in your web browser.
echo.
echo Press Ctrl+C to stop the application.
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    echo.
    pause
    exit /b 1
)

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    echo This may take a few minutes...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Please run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

REM Run the application
streamlit run app.py

pause
