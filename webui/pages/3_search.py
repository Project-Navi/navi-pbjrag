"""
🔎 Search - Semantic search across analyzed code
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for pbjrag imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "src"))

st.set_page_config(page_title="🔎 Search", page_icon="🔎", layout="wide")

st.title("🔎 Semantic Search")
st.markdown("Search for code chunks based on meaning and context, not just keywords.")

# Check if we have analysis results
if 'analysis_results' not in st.session_state or not st.session_state.analysis_results:
    st.warning("⚠️ No analysis results found. Please run analysis first.")
    st.info("👉 Go to the **📊 Analyze** page to analyze your code")
    st.stop()

results = st.session_state.analysis_results
chunks = results.get('chunks', [])

if not chunks:
    st.error("❌ No chunks found in analysis results")
    st.stop()

# Search interface
st.markdown("---")

# Search input
query = st.text_input(
    "🔍 Search Query",
    placeholder="e.g., 'error handling', 'data validation', 'API endpoints'",
    help="Enter a natural language query to search for relevant code chunks"
)

# Search options
col1, col2, col3 = st.columns(3)

with col1:
    search_mode = st.selectbox(
        "Search Mode",
        ["Semantic (AI)", "Keyword", "Hybrid"],
        help="Semantic uses meaning, Keyword uses exact matches, Hybrid combines both"
    )

with col2:
    max_results = st.slider(
        "Max Results",
        min_value=1,
        max_value=20,
        value=5,
        help="Maximum number of results to return"
    )

with col3:
    min_relevance = st.slider(
        "Min Relevance",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help="Minimum relevance score (0-1)"
    )

search_button = st.button("🚀 Search", type="primary")

# Search function
def keyword_search(query: str, chunks: list, max_results: int, min_score: float):
    """Simple keyword-based search."""
    results = []
    query_lower = query.lower()
    query_terms = query_lower.split()

    for i, chunk in enumerate(chunks):
        content = chunk.get('content', '').lower()

        # Calculate relevance score based on keyword matches
        score = 0
        for term in query_terms:
            # Count occurrences
            occurrences = content.count(term)
            score += occurrences * 0.1

        # Normalize score (cap at 1.0)
        score = min(score, 1.0)

        if score >= min_score:
            results.append({
                'chunk_index': i,
                'chunk': chunk,
                'score': score,
                'matches': sum(content.count(term) for term in query_terms)
            })

    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]

def semantic_search(query: str, chunks: list, max_results: int, min_score: float):
    """Semantic search using embeddings (placeholder - requires Qdrant)."""
    st.warning("⚠️ Semantic search requires Qdrant vector database integration.")
    st.info("💡 Falling back to keyword search for now...")
    return keyword_search(query, chunks, max_results, min_score)

def hybrid_search(query: str, chunks: list, max_results: int, min_score: float):
    """Hybrid search combining keyword and semantic approaches."""
    # For now, just use keyword search
    # In production, this would combine keyword and vector similarity scores
    return keyword_search(query, chunks, max_results, min_score)

# Execute search
if search_button and query:
    with st.spinner("🔍 Searching..."):
        if search_mode == "Semantic (AI)":
            search_results = semantic_search(query, chunks, max_results, min_relevance)
        elif search_mode == "Keyword":
            search_results = keyword_search(query, chunks, max_results, min_relevance)
        else:  # Hybrid
            search_results = hybrid_search(query, chunks, max_results, min_relevance)

        st.session_state.search_results = search_results
        st.session_state.search_query = query

# Display results
if 'search_results' in st.session_state and st.session_state.search_results:
    search_results = st.session_state.search_results

    st.markdown("---")
    st.subheader(f"📊 Search Results ({len(search_results)} matches)")

    if not search_results:
        st.info("🔍 No results found. Try adjusting your query or lowering the minimum relevance.")
        st.stop()

    # Display each result
    for i, result in enumerate(search_results):
        chunk = result['chunk']
        score = result['score']
        chunk_index = result['chunk_index']
        blessing = chunk.get('blessing', {})

        # Determine tier color
        tier = blessing.get('tier', 'Unknown')
        if tier == 'Φ+':
            tier_color = "🟢"
        elif tier == 'Φ~':
            tier_color = "🟡"
        elif tier == 'Φ-':
            tier_color = "🔴"
        else:
            tier_color = "⚪"

        # Create expander for each result
        with st.expander(
            f"{tier_color} **Result {i+1}** - Chunk {chunk_index} | "
            f"Relevance: {score:.2f} | Tier: {tier}",
            expanded=(i == 0)  # Expand first result by default
        ):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown("#### Code Content")
                code_content = chunk.get('content', '')

                # Highlight query terms (simple approach)
                if 'search_query' in st.session_state:
                    query_terms = st.session_state.search_query.lower().split()
                    st.markdown(f"**Matches:** {', '.join(query_terms)}")

                st.code(code_content, language='python', line_numbers=True)

            with col2:
                st.markdown("#### Metadata")
                st.metric("Relevance Score", f"{score:.3f}")
                st.metric("Chunk Index", chunk_index)
                st.metric("Blessing Tier", tier)
                st.metric("EPC", f"{blessing.get('epc', 0):.3f}")
                st.metric("Phase", blessing.get('phase', 'Unknown'))

                if 'matches' in result:
                    st.metric("Keyword Matches", result['matches'])

                # Link to explore page
                if st.button(f"📖 View in Explorer", key=f"view_{chunk_index}"):
                    st.info("💡 Navigate to the Explore page to see this chunk in detail")

    # Export search results
    st.markdown("---")
    if st.button("💾 Export Search Results"):
        import json
        export_data = {
            'query': st.session_state.search_query,
            'results_count': len(search_results),
            'results': [
                {
                    'chunk_index': r['chunk_index'],
                    'score': r['score'],
                    'tier': r['chunk'].get('blessing', {}).get('tier'),
                    'content_preview': r['chunk'].get('content', '')[:200] + '...'
                }
                for r in search_results
            ]
        }

        json_data = json.dumps(export_data, indent=2)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name="search_results.json",
            mime="application/json"
        )

else:
    # No search yet - show help
    st.info("👆 Enter a search query and click 'Search' to find relevant code chunks")

    with st.expander("📖 How to Search", expanded=True):
        st.markdown("""
        ### Search Modes

        - **Semantic (AI)**: Understands meaning and context (requires Qdrant)
        - **Keyword**: Simple text matching (currently available)
        - **Hybrid**: Combines both approaches (uses keyword for now)

        ### Tips for Better Results

        1. **Be Specific**: "error handling in API calls" > "error"
        2. **Use Multiple Terms**: "authentication login security"
        3. **Lower Min Relevance**: For broader results
        4. **Increase Max Results**: To see more matches

        ### Example Queries

        - "data validation and error handling"
        - "database queries and transactions"
        - "API endpoints with authentication"
        - "class definitions with inheritance"
        - "test functions for user management"
        """)

    # Show some stats about available chunks
    st.markdown("---")
    st.subheader("📊 Available Chunks")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Chunks", len(chunks))

    with col2:
        phi_plus = sum(1 for c in chunks if c.get('blessing', {}).get('tier') == 'Φ+')
        st.metric("Φ+ (High Quality)", phi_plus)

    with col3:
        total_lines = sum(len(c.get('content', '').split('\n')) for c in chunks)
        st.metric("Total Lines", total_lines)

# Footer tips
with st.expander("💡 Advanced Tips"):
    st.markdown("""
    ### Future Enhancements

    When Qdrant vector database is integrated, you'll be able to:

    - **Semantic Similarity**: Find code with similar meaning
    - **Context-Aware**: Understand code intent, not just keywords
    - **Cross-Reference**: Link related code chunks
    - **Pattern Detection**: Find similar architectural patterns

    ### Current Limitations

    - Currently using keyword-based search
    - Semantic search requires Qdrant setup
    - Relevance scores are approximate

    ### Setting Up Qdrant

    To enable full semantic search:

    1. Install Qdrant: `pip install qdrant-client`
    2. Run Qdrant server: `docker run -p 6333:6333 qdrant/qdrant`
    3. Index your code chunks
    4. Restart the WebUI
    """)
