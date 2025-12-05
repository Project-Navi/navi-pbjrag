"""
Chunk Viewer Components for PBJRAG WebUI
Display and interact with code chunks
"""

import streamlit as st
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound


def get_blessing_color(tier):
    """Get CSS class for blessing tier"""
    tier_map = {"Φ+": "blessing-positive", "Φ~": "blessing-neutral", "Φ-": "blessing-negative"}
    return tier_map.get(tier, "blessing-neutral")


def render_chunk(chunk, show_metrics=True, show_code=True):
    """
    Render a single chunk with formatting

    Args:
        chunk: DSCChunk object
        show_metrics: Whether to show detailed metrics
        show_code: Whether to show code content
    """
    blessing_class = get_blessing_color(chunk.blessing.tier)

    # Header
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"### {chunk.chunk_type}")
        st.caption(f"Lines {chunk.start_line}-{chunk.end_line}")

    with col2:
        st.markdown(
            f'<span class="{blessing_class}">{chunk.blessing.tier}</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"Phase: {chunk.blessing.phase}")

    with col3:
        st.metric("EPC", f"{chunk.blessing.epc:.2f}")

    # Metadata
    if chunk.provides:
        st.markdown(f"**Provides:** `{', '.join(chunk.provides)}`")

    if chunk.depends_on:
        st.markdown(f"**Depends on:** `{', '.join(chunk.depends_on)}`")

    # Metrics
    if show_metrics:
        with st.expander("📊 Detailed Metrics"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Complexity", f"{chunk.field_state.semantic[1]:.2f}")
                st.metric("Documentation", f"{chunk.field_state.semantic[2]:.2f}")

            with col2:
                st.metric("Error Handling", f"{chunk.field_state.ethical[0]:.2f}")
                st.metric("Type Hints", f"{chunk.field_state.ethical[2]:.2f}")

            with col3:
                st.metric("Independence", f"{chunk.field_state.relational[0]:.2f}")
                st.metric("Coupling", f"{chunk.field_state.relational[2]:.2f}")

            with col4:
                st.metric("Resonance", f"{chunk.blessing.resonance_score:.2f}")
                st.metric("Ethical Alignment", f"{chunk.blessing.ethical_alignment:.2f}")

    # Code content
    if show_code and chunk.content:
        with st.expander("💻 View Code", expanded=False):
            # Try to detect language and highlight
            try:
                # Guess lexer based on content
                lexer = guess_lexer(chunk.content)
                formatter = HtmlFormatter(style="monokai", noclasses=True)
                highlighted = highlight(chunk.content, lexer, formatter)

                st.markdown(
                    f'<div class="code-chunk">{highlighted}</div>',
                    unsafe_allow_html=True,
                )
            except (ClassNotFound, Exception):
                # Fallback to plain code block
                st.code(chunk.content, language="python")

    st.divider()


def render_chunk_list(chunks, page_size=10):
    """
    Render paginated list of chunks

    Args:
        chunks: List of DSCChunk objects
        page_size: Number of chunks per page
    """
    total_chunks = len(chunks)

    if total_chunks == 0:
        st.info("No chunks to display")
        return

    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        page = st.number_input(
            "Page",
            min_value=1,
            max_value=(total_chunks + page_size - 1) // page_size,
            value=1,
            step=1,
        )

    with col2:
        st.write(
            f"Showing {(page-1)*page_size + 1}-{min(page*page_size, total_chunks)} of {total_chunks}"
        )

    with col3:
        show_code = st.checkbox("Show Code", value=False)

    # Get chunks for current page
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_chunks)
    page_chunks = chunks[start_idx:end_idx]

    # Render chunks
    for chunk in page_chunks:
        render_chunk(chunk, show_metrics=True, show_code=show_code)


def render_chunk_details(chunk):
    """
    Render detailed view of a single chunk with all information

    Args:
        chunk: DSCChunk object
    """
    # Main header
    st.markdown(f"## {chunk.chunk_type}")

    if chunk.file_path:
        st.caption(f"📁 {chunk.file_path}:{chunk.start_line}-{chunk.end_line}")

    # Blessing badge
    blessing_class = get_blessing_color(chunk.blessing.tier)
    st.markdown(
        f'<h3><span class="{blessing_class}">{chunk.blessing.tier}</span> Blessing</h3>',
        unsafe_allow_html=True,
    )

    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("EPC", f"{chunk.blessing.epc:.3f}")

    with col2:
        st.metric("Ethical", f"{chunk.blessing.ethical_alignment:.3f}")

    with col3:
        st.metric("Resonance", f"{chunk.blessing.resonance_score:.3f}")

    with col4:
        st.metric("Presence", f"{chunk.blessing.presence_density:.3f}")

    with col5:
        st.metric("Contradiction", f"{chunk.blessing.contradiction_pressure:.3f}")

    st.divider()

    # Tabbed interface
    tab1, tab2, tab3, tab4 = st.tabs(
        ["💻 Code", "📊 Field State", "🔗 Dependencies", "🧬 Blessing"]
    )

    with tab1:
        st.subheader("Code Content")

        # Language selector
        lang = st.selectbox(
            "Syntax Highlighting",
            ["python", "javascript", "typescript", "java", "cpp", "go", "rust", "auto"],
            index=0,
        )

        if lang == "auto":
            try:
                lexer = guess_lexer(chunk.content)
                formatter = HtmlFormatter(style="monokai", noclasses=True, linenos=True)
                highlighted = highlight(chunk.content, lexer, formatter)
                st.markdown(highlighted, unsafe_allow_html=True)
            except Exception:
                st.code(chunk.content)
        else:
            st.code(chunk.content, language=lang)

    with tab2:
        st.subheader("Field State Analysis")

        # Import and use radar chart
        from .charts import plot_field_state_radar

        fig = plot_field_state_radar(chunk)
        st.plotly_chart(fig, use_container_width=True)

        # Field breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Semantic Field**")
            st.write(f"- Clarity: {chunk.field_state.semantic[0]:.3f}")
            st.write(f"- Complexity: {chunk.field_state.semantic[1]:.3f}")
            st.write(f"- Documentation: {chunk.field_state.semantic[2]:.3f}")

            st.markdown("**Ethical Field**")
            st.write(f"- Error Handling: {chunk.field_state.ethical[0]:.3f}")
            st.write(f"- Validation: {chunk.field_state.ethical[1]:.3f}")
            st.write(f"- Type Hints: {chunk.field_state.ethical[2]:.3f}")

        with col2:
            st.markdown("**Relational Field**")
            st.write(f"- Independence: {chunk.field_state.relational[0]:.3f}")
            st.write(f"- Encapsulation: {chunk.field_state.relational[1]:.3f}")
            st.write(f"- Coupling: {chunk.field_state.relational[2]:.3f}")

            st.markdown("**Contradiction Field**")
            st.write(f"- Alignment: {chunk.field_state.contradiction[0]:.3f}")
            st.write(f"- Pressure: {chunk.field_state.contradiction[1]:.3f}")
            st.write(f"- Tension: {chunk.field_state.contradiction[2]:.3f}")

    with tab3:
        st.subheader("Dependencies & Relationships")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Provides (Exports)**")
            if chunk.provides:
                for item in chunk.provides:
                    st.markdown(f"- `{item}`")
            else:
                st.info("No exports")

        with col2:
            st.markdown("**Depends On (Imports)**")
            if chunk.depends_on:
                for item in chunk.depends_on:
                    st.markdown(f"- `{item}`")
            else:
                st.info("No dependencies")

    with tab4:
        st.subheader("Blessing Breakdown")

        st.markdown(f"**Phase:** `{chunk.blessing.phase}`")
        st.progress(chunk.blessing.epc, text=f"EPC: {chunk.blessing.epc:.2%}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Positive Factors**")
            st.write(f"- Ethical Alignment: {chunk.blessing.ethical_alignment:.3f}")
            st.write(f"- Resonance Score: {chunk.blessing.resonance_score:.3f}")
            st.write(f"- Presence Density: {chunk.blessing.presence_density:.3f}")

        with col2:
            st.markdown("**Challenge Factors**")
            st.write(f"- Contradiction Pressure: {chunk.blessing.contradiction_pressure:.3f}")

            # Tier explanation
            tier_explanation = {
                "Φ+": "✨ This code is well-structured, documented, and follows best practices.",
                "Φ~": "⚖️ This code has both strengths and areas for improvement.",
                "Φ-": "⚠️ This code needs attention - consider refactoring or documentation.",
            }

            st.info(tier_explanation.get(chunk.blessing.tier, ""))
