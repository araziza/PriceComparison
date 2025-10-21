#!/bin/bash

echo "============================================"
echo "Nitro Price Comparison Tool"
echo "============================================"
echo ""
echo "Starting the application..."
echo "The dashboard will open in your web browser."
echo ""
echo "Press Ctrl+C to stop the application."
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    echo ""
    exit 1
fi

# Check if Streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Installing required dependencies..."
    echo "This may take a few minutes..."
    echo ""
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        echo "Please run: pip3 install -r requirements.txt"
        echo ""
        exit 1
    fi
fi

# Run the application
streamlit run app.py
