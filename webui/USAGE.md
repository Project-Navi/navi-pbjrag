# PBJRAG WebUI Usage Guide

## Quick Start

```bash
# From navi-pbjrag directory
streamlit run webui/app.py

# Or use the quick start script
./webui/run.sh
```

## Step-by-Step Guide

### 1. Analyze Code

1. Navigate to **📊 Analyze** page (should be first in sidebar)
2. Choose analysis type:
   - **Single File**: Analyze one Python file
   - **Directory**: Analyze all Python files in a folder
3. Enter the absolute path (e.g., `/home/user/project/main.py`)
4. Optionally adjust:
   - **Chunk Size**: Lines per chunk (default: 50)
   - **Overlap**: Overlapping lines between chunks (default: 10)
5. Click **🚀 Analyze**
6. View results:
   - Blessing tier distribution (Φ+, Φ~, Φ-)
   - Phase distribution
   - EPC timeline
7. Export results as JSON or text summary

### 2. Explore Chunks

1. Navigate to **🔍 Explore** page
2. Use sidebar filters:
   - **Blessing Tier**: Filter by Φ+, Φ~, or Φ-
   - **Phase**: Filter by specific phases
   - **EPC Range**: Filter by Evolutionary Path Clarity score
   - **Sort By**: Order chunks by index or EPC
3. Browse the summary table
4. Select a chunk to view:
   - Full code content
   - Blessing metadata
   - 9-dimensional field state radar chart
   - Detailed metrics
5. Navigate between chunks using Previous/Next buttons

### 3. Search Code

1. Navigate to **🔎 Search** page
2. Enter a search query (e.g., "error handling in API calls")
3. Configure search:
   - **Search Mode**: 
     - Semantic (AI) - Uses meaning (requires Qdrant)
     - Keyword - Simple text matching
     - Hybrid - Combines both
   - **Max Results**: How many results to show (1-20)
   - **Min Relevance**: Minimum score threshold (0-1)
4. Click **🚀 Search**
5. View results with:
   - Relevance scores
   - Blessing tiers
   - Code content
   - Metadata
6. Export search results as JSON

## Understanding Results

### Blessing Tiers

- **Φ+ (Crown)**: High-quality, well-structured code
  - Clear purpose and design
  - Good maintainability
  - Recommended for reference
  
- **Φ~ (Core)**: Average quality, functional code
  - Works but could be improved
  - May have some technical debt
  - Focus on incremental improvements
  
- **Φ- (Noise)**: Low-quality code needing attention
  - Complexity issues
  - Poor structure
  - Priority for refactoring

### EPC (Evolutionary Path Clarity)

Score from 0-1 indicating:
- **High (0.8-1.0)**: Clear path forward, easy to evolve
- **Medium (0.4-0.7)**: Some uncertainty, moderate effort
- **Low (0-0.3)**: Unclear direction, needs redesign

### 9 Dimensions

1. **Coherence**: Logical flow and structure
2. **Clarity**: Readability and understandability
3. **Completeness**: Feature coverage and edge cases
4. **Consistency**: Code patterns and conventions
5. **Correctness**: Bug-free implementation
6. **Coupling**: Dependency management
7. **Complexity**: Cyclomatic complexity
8. **Coverage**: Test coverage
9. **Changeability**: Ease of modification

Values range 0-1, higher is better.

## Tips & Tricks

### For Best Analysis Results

1. **Use appropriate chunk sizes**:
   - Small files: 30-50 lines
   - Large files: 50-100 lines
   - Very large files: 100-200 lines

2. **Set overlap for context**:
   - Simple code: 0-5 lines
   - Complex code: 10-20 lines
   - Interdependent code: 20-50 lines

3. **Analyze directories**:
   - Better for project-wide insights
   - Shows architectural patterns
   - Identifies consistency issues

### For Better Search

1. **Be specific**: "authentication error handling" > "errors"
2. **Use multiple terms**: "database transaction rollback"
3. **Try different modes**: Keyword for exact matches, Semantic for meaning
4. **Adjust relevance**: Lower for broader results, higher for precision

### For Effective Exploration

1. **Start with filters**: Focus on specific tiers or phases
2. **Sort by EPC**: Find best/worst code quickly
3. **Use the radar chart**: Identify specific weaknesses
4. **Compare chunks**: Look at multiple examples of same tier

## Example Workflows

### Workflow 1: Code Quality Audit

1. Analyze entire project directory
2. Note Φ- percentage (should be <20%)
3. Explore Φ- chunks to identify patterns
4. Search for common issues: "error handling", "validation", "edge cases"
5. Export findings for team review

### Workflow 2: Refactoring Prioritization

1. Analyze target module/file
2. Sort chunks by EPC (low to high)
3. Focus on low EPC Φ- chunks first
4. Review dimension radar for specific issues
5. Create refactoring tasks based on dimensions

### Workflow 3: Architecture Review

1. Analyze multiple related files
2. Look at phase distribution
3. Identify architectural inconsistencies
4. Search for specific patterns: "singleton", "factory", "dependency injection"
5. Use findings to guide architectural decisions

### Workflow 4: Knowledge Transfer

1. Analyze codebase for new team member
2. Filter for Φ+ chunks (best examples)
3. Export code examples with metadata
4. Create reading list based on phases
5. Use search to answer specific questions

## Keyboard Shortcuts

Streamlit default shortcuts:
- `R` - Rerun app
- `C` - Clear cache
- `⌘/Ctrl + K` - Command palette

## Troubleshooting

### "No analysis results found"
- Run analysis first on the Analyze page
- Make sure the file/directory path is correct
- Check that files are Python (.py) files

### "Error loading PBJRAG"
```bash
pip install -e /path/to/navi-pbjrag
```

### Charts not displaying
- Check browser console for errors
- Try refreshing the page
- Ensure plotly is installed: `pip install plotly`

### Search returns no results
- Lower the min relevance threshold
- Try different search terms
- Check that chunks were analyzed
- Use keyword mode instead of semantic

### Performance issues
- Reduce chunk size
- Analyze smaller directories
- Close unused browser tabs
- Clear Streamlit cache (press `C`)

## Configuration

### Theme Customization

Edit `webui/.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"  # Accent color
backgroundColor = "#0E1117"  # Main background
secondaryBackgroundColor = "#262730"  # Sidebar background
textColor = "#FAFAFA"  # Text color
font = "sans serif"  # Font family
```

### Port Configuration

Change default port (8501):
```bash
streamlit run app.py --server.port 8502
```

Or edit config.toml:
```toml
[server]
port = 8502
```

## Advanced Features

### Session State

Analysis results persist in Streamlit session state:
- Switch between pages without re-analyzing
- State cleared on page refresh
- Use browser back button safely

### Export Formats

**JSON Export**: Full analysis data
- All chunks with metadata
- Blessing information
- Field states
- Suitable for further processing

**Text Summary**: Human-readable report
- Statistics and distributions
- Suitable for reports
- Easy to share via email/chat

### Multiple Analyses

To compare analyses:
1. Run first analysis, export JSON
2. Refresh page or clear cache
3. Run second analysis, export JSON
4. Compare JSON files externally

## Integration

### With CI/CD

```bash
# In CI pipeline
streamlit run webui/app.py --server.headless true &
sleep 5
# Take screenshot or generate report
pkill streamlit
```

### With VS Code

Add to `.vscode/tasks.json`:
```json
{
  "label": "Launch PBJRAG WebUI",
  "type": "shell",
  "command": "streamlit run ${workspaceFolder}/webui/app.py"
}
```

### With Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e . && pip install -r webui/requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "webui/app.py"]
```

## Best Practices

1. **Analyze regularly**: Run analysis after major changes
2. **Track trends**: Export and compare results over time
3. **Share findings**: Export summaries for team discussions
4. **Focus on patterns**: Look for recurring issues across chunks
5. **Prioritize Φ-**: Address low-quality code systematically
6. **Use search**: Find examples of good/bad patterns
7. **Document decisions**: Keep notes on architectural choices
8. **Iterate**: Re-analyze after refactoring to measure improvement

## Support

For issues or questions:
- Check PBJRAG documentation
- Review error messages in terminal
- Check Streamlit logs
- Verify Python/dependency versions
