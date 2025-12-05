# 🥜🍇 PBJRAG WebUI

Streamlit-based web interface for visualizing PBJRAG code analysis results.

## Features

- **📊 Analysis Page**: Run PBJRAG analysis on files or directories
- **🔍 Exploration Page**: Browse and filter analyzed code chunks
- **🔎 Search Page**: Semantic/keyword search across chunks
- **📈 Visualizations**: Interactive charts (pie, bar, radar, timeline)
- **💾 Export**: Download results as JSON or text summaries

## Installation

1. Install dependencies:
```bash
cd webui
pip install -r requirements.txt
```

2. Make sure PBJRAG is installed:
```bash
cd ..
pip install -e .
```

## Usage

Run the Streamlit app:
```bash
streamlit run webui/app.py
```

Or from the webui directory:
```bash
cd webui
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## Pages

### 📊 Analyze
- Input: File path or directory path
- Configure chunk size and overlap
- Run analysis with the 🚀 Analyze button
- View blessing distribution, phase distribution, EPC timeline
- Export results as JSON or text summary

### 🔍 Explore
- Browse all analyzed chunks
- Filter by blessing tier (Φ+, Φ~, Φ-)
- Filter by phase and EPC range
- View detailed code content
- See 9-dimensional field state radar chart
- Navigate between chunks

### 🔎 Search
- Enter natural language queries
- Choose search mode (Semantic, Keyword, Hybrid)
- Adjust max results and min relevance
- View matching chunks with relevance scores
- Export search results

## Architecture

```
webui/
├── app.py                  # Main entry point
├── pages/
│   ├── 1_analyze.py       # Analysis page
│   ├── 2_explore.py       # Chunk explorer
│   └── 3_search.py        # Search interface
├── components/
│   ├── __init__.py
│   └── charts.py          # Visualization helpers
├── .streamlit/
│   └── config.toml        # Theme configuration
└── requirements.txt       # Dependencies
```

## Visualizations

### Blessing Pie Chart
Shows distribution of blessing tiers (Φ+, Φ~, Φ-)

### Phase Bar Chart
Shows distribution of blessing phases

### Dimension Radar Chart
9-dimensional field state visualization:
- Coherence, Clarity, Completeness
- Consistency, Correctness, Coupling
- Complexity, Coverage, Changeability

### EPC Timeline
Evolutionary Path Clarity over chunks

## API Usage

The WebUI imports from PBJRAG:
```python
from pbjrag import DSCAnalyzer, DSCCodeChunker
from pbjrag.crown_jewel import CoreMetrics, FieldContainer
```

Example analysis:
```python
analyzer = DSCAnalyzer()
results = analyzer.analyze_file("/path/to/file.py")
chunks = results.get('chunks', [])

for chunk in chunks:
    blessing = chunk.get('blessing', {})
    tier = blessing.get('tier')  # Φ+, Φ~, or Φ-
    epc = blessing.get('epc')    # 0-1 score
    phase = blessing.get('phase')
    field_state = chunk.get('field_state', {})  # 9 dimensions
```

## Configuration

Edit `.streamlit/config.toml` to customize theme:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

## Development

To add new visualizations:
1. Add function to `components/charts.py`
2. Import in page: `from charts import your_new_chart`
3. Use in page: `st.plotly_chart(your_new_chart(data))`

## Troubleshooting

**PBJRAG import error:**
```bash
pip install -e /path/to/navi-pbjrag
```

**Streamlit port conflict:**
```bash
streamlit run app.py --server.port 8502
```

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

## Future Enhancements

- [ ] Qdrant vector database integration for semantic search
- [ ] Real-time analysis progress tracking
- [ ] Comparison mode for multiple files/directories
- [ ] Historical analysis tracking
- [ ] Custom blessing tier thresholds
- [ ] Export to PDF reports
- [ ] Multi-language support
- [ ] Collaborative annotations

## License

Same as PBJRAG parent project.
