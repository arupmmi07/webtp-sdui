#!/bin/bash
# Quick start script for Streamlit UI

echo "🏥 Therapist Replacement System - Chat UI"
echo "=========================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not found. Installing..."
    echo ""
    pip3 install streamlit plotly
    echo ""
fi

echo "🚀 Starting Chat UI..."
echo "   URL: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

# Run Streamlit
streamlit run demo/chat_ui.py

