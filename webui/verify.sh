#!/bin/bash
# Verification script for PBJRAG WebUI

echo "🥜🍇 PBJRAG WebUI Verification"
echo "=============================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python not found"
    exit 1
fi

# Check files
echo ""
echo "Checking files:"
FILES=(
    "app.py"
    "requirements.txt"
    "pages/1_analyze.py"
    "pages/2_explore.py"
    "pages/3_search.py"
    "components/charts.py"
    "components/__init__.py"
    ".streamlit/config.toml"
)

ALL_GOOD=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file"
        ALL_GOOD=false
    fi
done

# Check dependencies
echo ""
echo "Checking dependencies:"
DEPS=("streamlit" "plotly" "pandas" "numpy")

for dep in "${DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $dep"
    else
        echo -e "${YELLOW}⚠${NC} $dep (install with: pip install $dep)"
    fi
done

# Check PBJRAG
echo ""
echo -n "Checking PBJRAG... "
if python3 -c "import sys; sys.path.insert(0, '../src'); from pbjrag import DSCAnalyzer" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} PBJRAG available"
else
    echo -e "${YELLOW}⚠${NC} PBJRAG not installed (run: cd .. && pip install -e .)"
fi

# Summary
echo ""
echo "=============================="
if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✓ All core files present${NC}"
    echo ""
    echo "To start the WebUI:"
    echo "  streamlit run app.py"
    echo ""
    echo "Or use the quick start:"
    echo "  ./run.sh"
else
    echo -e "${RED}✗ Some files are missing${NC}"
    echo "Please check the installation"
fi
