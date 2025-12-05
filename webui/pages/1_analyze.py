"""
📊 Analyze - Run PBJRAG analysis on code files
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Add parent directory to path for pbjrag imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "src"))

try:
    from pbjrag import DSCAnalyzer, DSCCodeChunker
    from pbjrag.crown_jewel import CoreMetrics, FieldContainer
    PBJRAG_AVAILABLE = True
except ImportError as e:
    PBJRAG_AVAILABLE = False
    st.error(f"❌ Error loading PBJRAG: {e}")

# Import visualization components
components_path = Path(__file__).parent.parent / "components"
sys.path.insert(0, str(components_path))

from charts import blessing_pie_chart, phase_bar_chart, epc_timeline_chart

st.set_page_config(page_title="📊 Analyze", page_icon="📊", layout="wide")

st.title("📊 Code Analysis")
st.markdown("Run PBJRAG analysis on your code files and visualize the results.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Analysis Configuration")

    analysis_type = st.radio(
        "Analysis Type",
        ["Single File", "Directory"],
        help="Choose whether to analyze a single file or entire directory"
    )

    if analysis_type == "Single File":
        file_path = st.text_input(
            "File Path",
            placeholder="/path/to/your/file.py",
            help="Enter the absolute path to the file you want to analyze"
        )
    else:
        file_path = st.text_input(
            "Directory Path",
            placeholder="/path/to/your/directory",
            help="Enter the absolute path to the directory you want to analyze"
        )

    # Note: PBJRAG uses AST-based semantic chunking, NOT line-based
    # Chunks are created at function/class/module boundaries automatically
    st.info(
        "🧠 **Semantic Chunking**: PBJRAG chunks code by AST boundaries "
        "(functions, classes, modules) - not arbitrary line counts. "
        "Each chunk includes its dependencies and provides metadata."
    )

    with st.expander("📖 How Semantic Chunking Works"):
        st.markdown("""
        Unlike traditional RAG systems that chunk by line count, PBJRAG uses
        **coherent semantic boundaries**:

        - **Functions** → Each function becomes a chunk with its dependencies tracked
        - **Classes** → Each class becomes a chunk with its methods listed in `provides`
        - **Module-level** → Imports and constants grouped separately

        Each chunk includes:
        - `provides`: What this code offers (function names, class names)
        - `depends_on`: What this code needs (imported names, called functions)
        - `field_state`: 9-dimensional quality vector
        - `blessing`: Quality tier (Φ+, Φ~, Φ-)

        This "adhesion" of context to each chunk is the key differentiator.
        """)

    analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)

    # Clear Analysis button
    if 'analysis_results' in st.session_state:
        st.markdown("---")
        if st.button("🗑️ Clear Analysis", help="Remove current analysis results", use_container_width=True):
            if 'analysis_results' in st.session_state:
                del st.session_state.analysis_results
            if 'analyzed_path' in st.session_state:
                del st.session_state.analyzed_path
            st.success("✅ Analysis cleared!")
            st.rerun()

# Main content area
if not PBJRAG_AVAILABLE:
    st.warning("⚠️ PBJRAG is not available. Please install it first.")
    st.code("pip install -e .", language="bash")
    st.stop()

if analyze_button:
    if not file_path:
        st.error("❌ Please provide a file or directory path")
        st.stop()

    path = Path(file_path)

    if not path.exists():
        st.error(f"❌ Path does not exist: {file_path}")
        st.stop()

    # Run analysis
    with st.spinner("🔄 Analyzing code..."):
        try:
            analyzer = DSCAnalyzer()

            if path.is_file():
                # Analyze single file
                results = analyzer.analyze_file(str(path))
                st.session_state.analysis_results = results
                st.session_state.analyzed_path = str(path)
                st.success(f"✅ Analysis complete: {path.name}")
            else:
                # Analyze directory
                all_chunks = []
                file_count = 0

                # Find all Python files
                python_files = list(path.rglob("*.py"))

                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, file in enumerate(python_files):
                    status_text.text(f"Analyzing: {file.name}")
                    try:
                        file_results = analyzer.analyze_file(str(file))
                        all_chunks.extend(file_results.get('chunks', []))
                        file_count += 1
                    except Exception as e:
                        st.warning(f"⚠️ Error analyzing {file.name}: {e}")

                    progress_bar.progress((i + 1) / len(python_files))

                results = {'chunks': all_chunks, 'file_count': file_count}
                st.session_state.analysis_results = results
                st.session_state.analyzed_path = str(path)

                status_text.empty()
                progress_bar.empty()
                st.success(f"✅ Analysis complete: {file_count} files, {len(all_chunks)} chunks")

        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.exception(e)
            st.stop()

# Display results
if 'analysis_results' in st.session_state and st.session_state.analysis_results:
    results = st.session_state.analysis_results
    chunks = results.get('chunks', [])

    if not chunks:
        st.warning("⚠️ No chunks found in analysis results")
        st.stop()

    st.markdown("---")
    st.header("📊 Analysis Results")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Chunks", len(chunks))

    with col2:
        phi_plus = sum(1 for c in chunks if c.get('blessing', {}).get('tier') == 'Φ+')
        percentage = (phi_plus / len(chunks) * 100) if chunks else 0
        st.metric("Φ+ Crown", phi_plus, f"{percentage:.1f}%")

    with col3:
        phi_tilde = sum(1 for c in chunks if c.get('blessing', {}).get('tier') == 'Φ~')
        percentage = (phi_tilde / len(chunks) * 100) if chunks else 0
        st.metric("Φ~ Core", phi_tilde, f"{percentage:.1f}%")

    with col4:
        phi_minus = sum(1 for c in chunks if c.get('blessing', {}).get('tier') == 'Φ-')
        percentage = (phi_minus / len(chunks) * 100) if chunks else 0
        st.metric("Φ- Noise", phi_minus, f"{percentage:.1f}%")

    # Visualizations
    st.markdown("---")
    st.subheader("📈 Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        try:
            fig = blessing_pie_chart(chunks)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating pie chart: {e}")

    with col2:
        try:
            fig = phase_bar_chart(chunks)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating bar chart: {e}")

    # EPC Timeline
    try:
        fig = epc_timeline_chart(chunks)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating timeline: {e}")

    # Export options
    st.markdown("---")
    st.subheader("💾 Export Results")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Export as JSON"):
            json_data = json.dumps(results, indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name="pbjrag_analysis.json",
                mime="application/json"
            )

    with col2:
        if st.button("📊 Export Summary"):
            summary = f"""PBJRAG Analysis Summary
========================
Path: {st.session_state.analyzed_path}
Total Chunks: {len(chunks)}

Blessing Distribution:
- Φ+ (Crown): {phi_plus} ({phi_plus/len(chunks)*100:.1f}%)
- Φ~ (Core): {phi_tilde} ({phi_tilde/len(chunks)*100:.1f}%)
- Φ- (Noise): {phi_minus} ({phi_minus/len(chunks)*100:.1f}%)
"""
            st.download_button(
                label="⬇️ Download Summary",
                data=summary,
                file_name="pbjrag_summary.txt",
                mime="text/plain"
            )

else:
    st.info("👈 Use the sidebar to configure and run analysis")

    # Example section
    with st.expander("📖 How to use"):
        st.markdown("""
        ### Analysis Steps

        1. **Choose Analysis Type**: Select whether to analyze a single file or directory
        2. **Enter Path**: Provide the absolute path to your code
        3. **Run Analysis**: Click the "🚀 Analyze" button
        4. **View Results**: Explore the visualizations and metrics

        ### Understanding Results

        - **Φ+ (Crown)**: High-quality, well-structured code with good documentation, type hints, error handling
        - **Φ~ (Core)**: Average quality, functional code that works but could be improved
        - **Φ- (Noise)**: Low-quality code needing improvement (high complexity, poor documentation)

        ### The 9 Field Dimensions

        Each chunk is analyzed across 9 dimensions:
        1. **Semantic** - What the code means and does
        2. **Emotional** - Developer intent and naming sentiment
        3. **Ethical** - Code quality and best practices
        4. **Temporal** - Evolution and change patterns
        5. **Entropic** - Chaos and unpredictability
        6. **Rhythmic** - Cadence and flow
        7. **Contradiction** - Internal tensions and complexity
        8. **Relational** - Dependencies and connections
        9. **Emergent** - Novelty and surprise

        ### Tips

        - Semantic chunking automatically groups by function/class boundaries
        - Each chunk includes dependency tracking (`provides`, `depends_on`)
        - Export results for integration with vector stores
        """)
