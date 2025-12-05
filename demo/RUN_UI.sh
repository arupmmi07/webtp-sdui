#!/bin/bash

# Script to run Streamlit UI from the correct directory

echo "=========================================="
echo "Starting AI Assistant UI"
echo "=========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
echo "Demo directory: $SCRIPT_DIR"
echo ""

# Activate virtual environment
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    echo "✓ Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "✗ Virtual environment not found at $PROJECT_ROOT/venv"
    echo "  Run 'make install' first!"
    exit 1
fi

# Change to demo directory
cd "$SCRIPT_DIR"
echo "✓ Changed to demo directory"
echo ""

# Check if pages exist
if [ -d "pages" ]; then
    echo "✓ pages/ directory found"
    echo "  Files:"
    ls -la pages/*.py 2>/dev/null | awk '{print "    - " $9}'
else
    echo "✗ pages/ directory not found!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Starting Streamlit..."
echo "=========================================="
echo ""
echo "UI will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run Streamlit
streamlit run chat_ui.py

