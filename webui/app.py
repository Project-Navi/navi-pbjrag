"""
🥜🍇 PBJRAG Code Analysis WebUI

A Streamlit-based web interface for visualizing PBJRAG code analysis results.
"""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path for pbjrag imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / "src"))

# Configure page
st.set_page_config(
    page_title="🥜🍇 PBJRAG", page_icon="🥜", layout="wide", initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 3rem;
    }
    .info-box {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .warning-box {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #FFC107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown('<div class="main-header">🥜🍇 PBJRAG</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Differential Symbolic Calculus for Code Analysis</div>',
    unsafe_allow_html=True,
)

# Introduction
st.markdown(
    """
## Welcome to PBJRAG v3

PBJRAG (Peanut Butter & Jelly Retrieval-Augmented Generation) is a next-generation
code analysis framework that understands code as living, evolving symbolic fields
rather than static text.

### Key Features

- **🎯 Blessing System**: Classifies code into tiers (Φ+, Φ~, Φ-) based on quality
- **📊 9-Dimensional Analysis**: Evaluates code across coherence, clarity, completeness, and more
- **🔍 Semantic Search**: Find code chunks based on meaning, not just keywords
- **📈 Visual Analytics**: Interactive charts and graphs for code insights
- **🌊 Field Theory**: Mathematical approach to understanding code evolution

### Getting Started

Use the sidebar to navigate between different analysis modes:

1. **📊 Analyze**: Upload or specify code files/folders for analysis
2. **🔍 Explore**: Browse and filter analyzed chunks
3. **🔎 Search**: Semantic search across your codebase

"""
)

# Sidebar
with st.sidebar:
    st.header("🎛️ Navigation")
    st.markdown(
        """
    **Pages:**
    - 📊 Analyze - Run code analysis
    - 🔍 Explore - Browse chunks
    - 🔎 Search - Semantic search

    **Status:**
    """
    )

    # Check if pbjrag is available
    try:
        from pbjrag import DSCAnalyzer, DSCCodeChunker
        from pbjrag.crown_jewel import CoreMetrics, FieldContainer

        st.success("✅ PBJRAG loaded successfully")
    except ImportError as e:
        st.error(f"❌ Error loading PBJRAG: {e}")
        st.info("💡 Make sure to install PBJRAG: `pip install -e .`")

    st.markdown("---")
    st.markdown(
        """
    **Version:** 3.0.0
    **Framework:** Streamlit
    **Engine:** DSC (Differential Symbolic Calculus)
    """
    )

    # Clear Session button
    st.markdown("---")
    if st.button(
        "🔄 Clear Session", help="Reset all analysis data and start fresh", use_container_width=True
    ):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ Session cleared! Restarting...")
        st.rerun()

# Quick stats (if session state has data)
if "analysis_results" in st.session_state and st.session_state.analysis_results:
    st.markdown("---")
    st.subheader("📊 Current Session Stats")

    results = st.session_state.analysis_results
    chunks = results.get("chunks", [])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Chunks", len(chunks))

    with col2:
        phi_plus = sum(1 for c in chunks if c.get("blessing", {}).get("tier") == "Φ+")
        st.metric("Φ+ (Crown)", phi_plus)

    with col3:
        phi_tilde = sum(1 for c in chunks if c.get("blessing", {}).get("tier") == "Φ~")
        st.metric("Φ~ (Core)", phi_tilde)

    with col4:
        phi_minus = sum(1 for c in chunks if c.get("blessing", {}).get("tier") == "Φ-")
        st.metric("Φ- (Noise)", phi_minus)

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #888;">
    <p>PBJRAG v3 - Differential Symbolic Calculus for Code Analysis</p>
    <p>🥜 Because code is peanut butter, not text 🍇</p>
</div>
""",
    unsafe_allow_html=True,
)
