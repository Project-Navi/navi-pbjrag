"""
🔍 Explore - Browse and filter analyzed code chunks
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add parent directory to path for pbjrag imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "src"))

# Import visualization components
components_path = Path(__file__).parent.parent / "components"
sys.path.insert(0, str(components_path))

from charts import dimension_radar_chart

st.set_page_config(page_title="🔍 Explore", page_icon="🔍", layout="wide")

st.title("🔍 Chunk Explorer")
st.markdown("Browse and filter analyzed code chunks with detailed insights.")

# Accessibility: Tier labels with icons and descriptions
TIER_LABELS = {
    "Φ+": "🟢 Φ+ Crown Jewel",
    "Φ~": "🟡 Φ~ Standard",
    "Φ-": "🔴 Φ- Needs Work",
}

# Check if we have analysis results
if "analysis_results" not in st.session_state or not st.session_state.analysis_results:
    st.warning("⚠️ No analysis results found. Please run analysis first.")
    st.info("👉 Go to the **📊 Analyze** page to analyze your code")
    st.stop()

results = st.session_state.analysis_results
chunks = results.get("chunks", [])

if not chunks:
    st.error("❌ No chunks found in analysis results")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("🎛️ Filters")

    # Blessing tier filter
    st.subheader("Blessing Tier")
    tier_options = ["All", "Φ+", "Φ~", "Φ-"]
    tier_display_options = ["All"] + [TIER_LABELS.get(t, t) for t in tier_options[1:]]
    selected_tier_display = st.selectbox("Select Tier", tier_display_options)
    # Map back to tier code
    selected_tier = (
        "All"
        if selected_tier_display == "All"
        else tier_options[tier_display_options.index(selected_tier_display)]
    )

    # Phase filter
    st.subheader("Blessing Phase")
    phases = set()
    for chunk in chunks:
        phase = chunk.get("blessing", {}).get("phase", "Unknown")
        phases.add(phase)

    phase_options = ["All"] + sorted(list(phases))
    selected_phase = st.selectbox("Select Phase", phase_options)

    # EPC range filter
    st.subheader("EPC Range")
    epc_min, epc_max = st.slider("EPC (Evolutionary Path Clarity)", 0.0, 1.0, (0.0, 1.0), step=0.05)

    # Sort options
    st.subheader("Sort By")
    sort_by = st.selectbox("Sort Order", ["Chunk Index", "EPC (High to Low)", "EPC (Low to High)"])

# Apply filters
filtered_chunks = []
for i, chunk in enumerate(chunks):
    blessing = chunk.get("blessing", {})
    tier = blessing.get("tier", "Unknown")
    phase = blessing.get("phase", "Unknown")
    epc = blessing.get("epc", 0.5)

    # Apply tier filter
    if selected_tier != "All" and tier != selected_tier:
        continue

    # Apply phase filter
    if selected_phase != "All" and phase != selected_phase:
        continue

    # Apply EPC filter
    if epc < epc_min or epc > epc_max:
        continue

    # Add chunk index for reference
    chunk_with_index = chunk.copy()
    chunk_with_index["_index"] = i
    filtered_chunks.append(chunk_with_index)

# Sort chunks
if sort_by == "EPC (High to Low)":
    filtered_chunks.sort(key=lambda c: c.get("blessing", {}).get("epc", 0), reverse=True)
elif sort_by == "EPC (Low to High)":
    filtered_chunks.sort(key=lambda c: c.get("blessing", {}).get("epc", 0), reverse=False)
# Default is by chunk index (already in order)

# Display results count
st.markdown(f"**Showing {len(filtered_chunks)} of {len(chunks)} chunks**")

if not filtered_chunks:
    st.warning("🔍 No chunks match the selected filters")
    st.stop()

# Create summary table
st.markdown("---")
st.subheader("📋 Chunk Summary")

summary_data = []
for chunk in filtered_chunks:
    blessing = chunk.get("blessing", {})
    field_state = chunk.get("field_state", {})

    # Calculate average field value
    field_values = [v for v in field_state.values() if isinstance(v, (int, float))]
    avg_field = sum(field_values) / len(field_values) if field_values else 0

    tier_raw = blessing.get("tier", "Unknown")
    tier_display = TIER_LABELS.get(tier_raw, tier_raw)

    summary_data.append(
        {
            "Index": chunk["_index"],
            "Tier": tier_display,
            "Phase": blessing.get("phase", "Unknown"),
            "EPC": f"{blessing.get('epc', 0):.3f}",
            "Avg Field": f"{avg_field:.3f}",
            "Lines": len(chunk.get("content", "").split("\n")),
        }
    )

df = pd.DataFrame(summary_data)
st.dataframe(df, use_container_width=True)

# Detailed view
st.markdown("---")
st.subheader("📖 Detailed Chunk View")

# Chunk selector
selected_idx = st.selectbox(
    "Select Chunk to View",
    range(len(filtered_chunks)),
    format_func=lambda i: f"Chunk {filtered_chunks[i]['_index']} - {TIER_LABELS.get(filtered_chunks[i].get('blessing', {}).get('tier', 'Unknown'), filtered_chunks[i].get('blessing', {}).get('tier', 'Unknown'))}",
)

selected_chunk = filtered_chunks[selected_idx]
blessing = selected_chunk.get("blessing", {})
field_state = selected_chunk.get("field_state", {})

# Display chunk details
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### Code Content")

    # Display tier with icon, text label, and color for accessibility
    tier = blessing.get("tier", "Unknown")
    tier_display = TIER_LABELS.get(tier, tier)
    if tier == "Φ+":
        color = "green"
    elif tier == "Φ~":
        color = "orange"
    elif tier == "Φ-":
        color = "red"
    else:
        color = "gray"

    st.markdown(f"**Blessing Tier:** :{color}[{tier_display}]")

    code_content = selected_chunk.get("content", "")
    st.code(code_content, language="python", line_numbers=True)

with col2:
    st.markdown("#### Metadata")

    st.metric("Chunk Index", selected_chunk["_index"])
    st.metric("EPC", f"{blessing.get('epc', 0):.3f}")
    st.metric("Phase", blessing.get("phase", "Unknown"))
    st.metric("Lines", len(code_content.split("\n")))

    # Additional blessing details
    with st.expander("📊 Blessing Details"):
        st.json(blessing)

# Field state visualization
st.markdown("---")
st.subheader("🌐 9-Dimensional Field State")

col1, col2 = st.columns([3, 2])

with col1:
    try:
        fig = dimension_radar_chart(field_state)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating radar chart: {e}")

with col2:
    st.markdown("#### Field Dimensions")

    dimensions = [
        ("coherence", "🔗 Logical flow"),
        ("clarity", "💡 Readability"),
        ("completeness", "✅ Feature coverage"),
        ("consistency", "🎯 Code patterns"),
        ("correctness", "✔️ Bug-free"),
        ("coupling", "🔌 Dependencies"),
        ("complexity", "🧩 Cyclomatic"),
        ("coverage", "🧪 Test coverage"),
        ("changeability", "🔧 Maintainability"),
    ]

    for dim, desc in dimensions:
        value = field_state.get(dim, 0.5)
        st.metric(desc, f"{value:.3f}")

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if selected_idx > 0:
        if st.button("⬅️ Previous Chunk"):
            st.rerun()

with col3:
    if selected_idx < len(filtered_chunks) - 1:
        if st.button("Next Chunk ➡️"):
            st.rerun()

# Tips
with st.expander("💡 Tips"):
    st.markdown(
        """
    ### Using the Explorer

    - **Filters**: Use sidebar filters to narrow down chunks
    - **Sorting**: Sort by EPC to find highest/lowest quality code
    - **Details**: Click on any chunk to see full code and metrics
    - **Radar Chart**: Visualizes 9-dimensional field state

    ### Interpreting Metrics

    - **EPC (0-1)**: Higher = clearer evolutionary path
    - **Field State (0-1)**: Higher values = better in that dimension
    - **Tier**: 🟢 Φ+ Crown Jewel (best) → 🟡 Φ~ Standard (okay) → 🔴 Φ- Needs Work (needs work)
    """
    )
