#!/bin/bash
# Quick start script for PBJRAG WebUI

echo "🥜🍇 Starting PBJRAG WebUI..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if pbjrag is installed
python3 -c "import pbjrag" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  PBJRAG not installed. Installing from parent directory..."
    cd .. && pip install -e . && cd webui
fi

echo "✅ All dependencies ready"
echo ""
echo "🚀 Launching WebUI at http://localhost:8501"
echo ""

streamlit run app.py
