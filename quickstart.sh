#!/bin/bash
# PBJRAG Quickstart
# Usage: ./quickstart.sh

set -e

echo "🥜🍇 Starting PBJRAG Quickstart..."
echo ""

# Check for docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Installing locally..."
    echo ""

    # Check for Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not found. Please install Python 3.8+."
        exit 1
    fi

    # Install PBJRAG
    echo "📦 Installing PBJRAG..."
    pip install -e .

    # Install WebUI dependencies
    echo "📦 Installing WebUI dependencies..."
    pip install streamlit plotly pandas

    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "🚀 Starting PBJRAG WebUI..."
    echo "   Open http://localhost:8501 in your browser"
    echo ""

    # Start streamlit
    streamlit run webui/app.py
else
    echo "🐳 Docker found! Using Docker Compose..."
    echo ""

    # Check for docker-compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        echo "❌ docker-compose not found. Please install Docker Compose."
        exit 1
    fi

    # Start services
    echo "🚀 Starting PBJRAG services..."
    $COMPOSE_CMD up -d

    echo ""
    echo "✅ PBJRAG is running!"
    echo ""
    echo "🌐 WebUI: http://localhost:8501"
    echo ""
    echo "📊 To view logs: $COMPOSE_CMD logs -f"
    echo "🛑 To stop: $COMPOSE_CMD down"
    echo ""

    # Try to open browser
    sleep 2
    xdg-open http://localhost:8501 2>/dev/null || \
    open http://localhost:8501 2>/dev/null || \
    echo "👉 Open http://localhost:8501 in your browser"
fi
