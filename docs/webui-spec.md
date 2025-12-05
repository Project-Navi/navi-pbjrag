# PBJRAG WebUI Specification v1.0

**Project**: PBJRAG WebUI - Streamlit-based visualization interface for PBJRAG code analysis
**Created**: 2025-12-05
**Version**: 1.0.0
**Status**: Specification Phase (SPARC)

---

## 1. Executive Summary

### 1.1 Purpose

This specification defines the requirements for a Streamlit-based web user interface (WebUI) for PBJRAG, a 9-dimensional code analysis framework based on Differential Symbolic Calculus (DSC). The WebUI will provide an intuitive, visual way to interact with PBJRAG's analysis capabilities, eliminating the need for command-line expertise.

### 1.2 Goals

- **Accessibility**: Enable non-technical users to analyze codebases
- **Visualization**: Display blessing tiers, phases, and 9-dimensional analysis graphically
- **Semantic Search**: Provide Qdrant-powered semantic code search
- **Zero-Config Deploy**: `docker-compose up` should "just work"
- **Extensibility**: Support future features (comparisons, trends, exports)

### 1.3 Scope

**In Scope:**
- Streamlit web interface for PBJRAG
- Qdrant integration for semantic search
- Docker Compose orchestration
- File/directory upload and analysis
- Blessing tier and phase visualization
- 9-dimensional radar charts
- Code chunk viewer with metadata
- Basic export (JSON, Markdown, HTML)

**Out of Scope (Future Releases):**
- Multi-project comparison dashboards
- Historical trend analysis
- Real-time collaborative editing
- Authentication/authorization
- Cloud deployment configurations
- CI/CD pipeline integration
- Custom plugin system

---

## 2. Functional Requirements

### FR-001: Code Input and Upload

**Priority**: High
**Dependencies**: None

**Description**: Users must be able to specify code to analyze through multiple input methods.

**Acceptance Criteria**:
- **FR-001.1**: User can paste a file path into a text input field
- **FR-001.2**: User can upload a single file via file uploader widget
- **FR-001.3**: User can upload multiple files via file uploader widget
- **FR-001.4**: User can specify a directory path for batch analysis
- **FR-001.5**: Uploaded files are temporarily stored in `/tmp/pbjrag-uploads/`
- **FR-001.6**: System validates file extensions (`.py`, `.js`, `.ts`, `.java`, `.go`, `.rb`, `.php`, `.c`, `.cpp`, `.rs`)
- **FR-001.7**: System displays file size and line count before analysis
- **FR-001.8**: User receives clear error messages for invalid inputs

**Use Case**:
```gherkin
Scenario: Upload single Python file
  Given I am on the PBJRAG WebUI home page
  When I click "Upload File"
  And I select "my_module.py" from my filesystem
  Then I should see "✓ my_module.py uploaded (245 lines)"
  And the "Analyze" button should become enabled
```

---

### FR-002: Analysis Execution

**Priority**: High
**Dependencies**: FR-001

**Description**: Users initiate code analysis and monitor progress in real-time.

**Acceptance Criteria**:
- **FR-002.1**: User clicks "Analyze" button to start analysis
- **FR-002.2**: Progress bar displays during analysis (0-100%)
- **FR-002.3**: Progress updates show current stage: "Chunking", "Blessing Calculation", "Vector Embedding", "Finalizing"
- **FR-002.4**: Estimated time remaining is displayed
- **FR-002.5**: User can cancel analysis mid-process
- **FR-002.6**: Analysis results are cached for 1 hour to avoid re-computation
- **FR-002.7**: System handles errors gracefully with clear messages
- **FR-002.8**: Analysis parameters are configurable (purpose: stability/emergence/coherence/innovation)

**Use Case**:
```gherkin
Scenario: Successful analysis with progress tracking
  Given I have uploaded "large_project.py"
  When I click "Analyze with purpose: coherence"
  Then I should see a progress bar
  And I should see "Stage 1/4: Chunking code..."
  And I should see "Estimated: 45 seconds"
  When analysis completes
  Then I should see "✓ Analysis complete! 87 chunks analyzed"
  And I should be redirected to the results dashboard
```

---

### FR-003: Blessing Tier Distribution Visualization

**Priority**: High
**Dependencies**: FR-002

**Description**: Display the distribution of blessing tiers across all code chunks.

**Acceptance Criteria**:
- **FR-003.1**: Pie chart shows percentages of Φ+, Φ~, Φ- tiers
- **FR-003.2**: Bar chart shows count of chunks per tier
- **FR-003.3**: Color coding: Φ+ (green), Φ~ (yellow), Φ- (red)
- **FR-003.4**: Clicking on a tier filters results to show only those chunks
- **FR-003.5**: Overall blessing score (0.0-1.0) is prominently displayed
- **FR-003.6**: EPC (Emergence Potential Coefficient) average is shown
- **FR-003.7**: Charts are interactive (hover to see details)

**Visual Mockup**:
```
┌─────────────────────────────────────────────────┐
│  Overall Blessing: 0.72 (Φ~)   EPC: 0.68      │
│                                                 │
│  ┌─────────────┐  ┌───────────────────────┐   │
│  │  Φ+ (45%)   │  │                        │   │
│  │  Φ~ (38%)   │  │  ███ Φ+ (39 chunks)   │   │
│  │  Φ- (17%)   │  │  ███ Φ~ (33 chunks)   │   │
│  └─────────────┘  │  ███ Φ- (15 chunks)   │   │
│                    └───────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

### FR-004: Phase Distribution Visualization

**Priority**: High
**Dependencies**: FR-002

**Description**: Display the 7-phase lifecycle distribution of code chunks.

**Acceptance Criteria**:
- **FR-004.1**: Bar chart shows chunk count per phase (Compost, Reflection, Becoming, Stillness, Turning, Emergent, Grinding)
- **FR-004.2**: Phases are color-coded with a semantic gradient (brown → blue → green → gold → purple → orange → red)
- **FR-004.3**: Clicking on a phase filters results to show only those chunks
- **FR-004.4**: Dominant phase is highlighted with explanation
- **FR-004.5**: Phase distribution percentage is shown
- **FR-004.6**: Tooltip shows phase range and meaning

**Visual Mockup**:
```
Phase Distribution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Compost     ▓▓░░░░░░░░ (8 chunks, 9%)
Reflection  ▓▓▓░░░░░░░ (12 chunks, 14%)
Becoming    ▓▓▓▓░░░░░░ (16 chunks, 18%)
Stillness   ▓▓▓▓▓▓▓▓▓▓ (35 chunks, 40%) ← Dominant
Turning     ▓▓▓▓░░░░░░ (10 chunks, 11%)
Emergent    ▓▓░░░░░░░░ (5 chunks, 6%)
Grinding    ▓░░░░░░░░░ (1 chunk, 1%)
```

---

### FR-005: 9-Dimensional Radar Chart

**Priority**: High
**Dependencies**: FR-002

**Description**: Visualize the 9 dimensions of code analysis for selected chunks.

**Acceptance Criteria**:
- **FR-005.1**: Radar/spider chart displays all 9 dimensions: Σ (Semantic), Ε (Emotional), Θ (Ethical), Τ (Temporal), Ξ (Entropic), Ρ (Rhythmic), Ω (Contradiction), Γ (Relational), Μ (Emergent)
- **FR-005.2**: Each dimension is labeled with symbol and name
- **FR-005.3**: User can toggle between individual chunk view or aggregate view
- **FR-005.4**: Aggregate view shows average, min, max, or median
- **FR-005.5**: Color gradient indicates dimension strength (red → yellow → green)
- **FR-005.6**: Clicking on a dimension shows detailed explanation
- **FR-005.7**: Chart is exportable as SVG or PNG

**Visual Mockup**:
```
        Σ (Semantic)
           1.0
           /|\
          / | \
     Μ /  |  \ Ε
      /   |   \
     /    |    \
    /_____|_____\
   /      |      \
  /       |       \
 /________|________\ Θ
Γ        0.5        Τ
         / \
        /   \
       /     \
      Ω ─── Ξ ─── Ρ
```

---

### FR-006: Code Chunk Browser

**Priority**: High
**Dependencies**: FR-002

**Description**: Display analyzed code chunks with metadata and blessing information.

**Acceptance Criteria**:
- **FR-006.1**: Chunks are displayed in a paginated list (25 per page)
- **FR-006.2**: Each chunk shows: file path, line range, blessing tier, phase, EPC score
- **FR-006.3**: Syntax-highlighted code preview is shown (collapsible)
- **FR-006.4**: User can filter by: blessing tier, phase, file, dimension threshold
- **FR-006.5**: User can sort by: blessing score, EPC, file name, line number, phase
- **FR-006.6**: Clicking on a chunk shows full 9-dimensional details
- **FR-006.7**: Code chunks are copy-to-clipboard enabled
- **FR-006.8**: Chunks with Φ- tier are highlighted in red for attention

**Visual Mockup**:
```
┌───────────────────────────────────────────────────────────┐
│ Filter: [All Tiers ▼] [All Phases ▼] Sort: [Blessing ▼] │
├───────────────────────────────────────────────────────────┤
│ 📄 src/auth/login.py:45-78                                │
│ Φ+  Stillness  EPC: 0.82                                  │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ def authenticate_user(email, password):             │   │
│ │     """Verify user credentials securely."""         │   │
│ │     ...                                             │   │
│ └─────────────────────────────────────────────────────┘   │
│ [View Details] [Copy Code]                                │
├───────────────────────────────────────────────────────────┤
│ 📄 src/utils/helpers.py:12-23                             │
│ Φ-  Compost  EPC: 0.28  ⚠️ Needs Attention               │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ def proc(x, y, z=None):                             │   │
│ │     if x:                                           │   │
│ │         ...                                         │   │
│ └─────────────────────────────────────────────────────┘   │
│ [View Details] [Copy Code]                                │
└───────────────────────────────────────────────────────────┘
```

---

### FR-007: Semantic Search (Qdrant-Powered)

**Priority**: High
**Dependencies**: FR-002, Qdrant running

**Description**: Enable semantic search across analyzed code using natural language queries.

**Acceptance Criteria**:
- **FR-007.1**: User enters natural language query (e.g., "error handling patterns")
- **FR-007.2**: System returns top-k relevant chunks (default k=10, configurable 5-50)
- **FR-007.3**: Results show relevance score (0.0-1.0) and blessing tier
- **FR-007.4**: Results are ranked by semantic similarity × blessing weight
- **FR-007.5**: User can filter search results by blessing tier or phase
- **FR-007.6**: Search history is preserved during session
- **FR-007.7**: System handles Qdrant connection failures gracefully
- **FR-007.8**: Search queries are vectorized using the same embeddings as analysis

**Use Case**:
```gherkin
Scenario: Semantic search for authentication code
  Given I have analyzed a project
  When I enter "user authentication with JWT tokens" in the search box
  And I click "Search"
  Then I should see 10 results ranked by relevance
  And the top result should have similarity > 0.75
  And each result should show file path, blessing tier, and code preview
  When I click on the first result
  Then I should see the full code chunk with 9-dimensional analysis
```

---

### FR-008: Export and Reporting

**Priority**: Medium
**Dependencies**: FR-002

**Description**: Allow users to export analysis results in multiple formats.

**Acceptance Criteria**:
- **FR-008.1**: Export formats: JSON, Markdown, HTML
- **FR-008.2**: JSON export includes all raw data (chunks, dimensions, blessings, phases)
- **FR-008.3**: Markdown export generates a formatted report with charts (as ASCII art or image links)
- **FR-008.4**: HTML export generates a standalone, styled report with embedded charts
- **FR-008.5**: User can select what to export: all chunks, filtered chunks, summary only
- **FR-008.6**: Export files are named with timestamp: `pbjrag_report_2025-12-05_14-30-22.json`
- **FR-008.7**: Download button triggers browser download
- **FR-008.8**: Export includes metadata: PBJRAG version, analysis config, timestamp

---

### FR-009: Configuration Panel

**Priority**: Medium
**Dependencies**: None

**Description**: Provide a settings panel for customizing analysis behavior.

**Acceptance Criteria**:
- **FR-009.1**: User can select analysis purpose: Stability, Emergence, Coherence, Innovation
- **FR-009.2**: User can toggle vector store usage (Qdrant on/off)
- **FR-009.3**: User can set chunk size parameters (min: 50, max: 1000 lines)
- **FR-009.4**: User can enable/disable fractal pattern detection
- **FR-009.5**: User can adjust blessing tier thresholds (advanced)
- **FR-009.6**: Configuration changes persist for session duration
- **FR-009.7**: "Reset to Defaults" button restores default settings
- **FR-009.8**: Configuration is saved in session state

---

### FR-010: Error Handling and User Feedback

**Priority**: High
**Dependencies**: All

**Description**: Provide clear, actionable feedback for all user actions and system states.

**Acceptance Criteria**:
- **FR-010.1**: File upload errors show specific reasons (size, format, permissions)
- **FR-010.2**: Analysis errors display stack traces in expandable section
- **FR-010.3**: Qdrant connection errors suggest troubleshooting steps
- **FR-010.4**: Success messages use green checkmarks (✓)
- **FR-010.5**: Warnings use yellow icons (⚠️)
- **FR-010.6**: Errors use red icons (❌)
- **FR-010.7**: Loading states show spinners or progress bars
- **FR-010.8**: Empty states provide helpful guidance (e.g., "No results found. Try a different query.")

---

## 3. Non-Functional Requirements

### NFR-001: Performance

**Priority**: High

**Requirements**:
- **NFR-001.1**: WebUI page load time < 2 seconds
- **NFR-001.2**: Analysis of 1000-line file completes in < 30 seconds
- **NFR-001.3**: Semantic search returns results in < 3 seconds
- **NFR-001.4**: Chart rendering completes in < 1 second
- **NFR-001.5**: WebUI handles files up to 10MB (50,000 lines)
- **NFR-001.6**: Concurrent users: 10+ without degradation (local deployment)

**Measurement**:
- Use `time.time()` benchmarks for analysis stages
- Streamlit profiler for rendering performance
- Load testing with `locust` or `k6`

---

### NFR-002: Usability

**Priority**: High

**Requirements**:
- **NFR-002.1**: User can complete full workflow (upload → analyze → view results) in < 5 clicks
- **NFR-002.2**: All buttons, charts, and text are accessible on 1280x720 displays
- **NFR-002.3**: Color scheme is colorblind-friendly (use patterns in addition to colors)
- **NFR-002.4**: Font size is minimum 14px for body text
- **NFR-002.5**: Error messages are written in plain language, no jargon
- **NFR-002.6**: Help tooltips are available for all technical terms
- **NFR-002.7**: Mobile responsive (tablet-friendly, minimum 768px width)

**Measurement**:
- User testing with 5+ non-technical users
- WCAG 2.1 AA compliance check

---

### NFR-003: Reliability

**Priority**: High

**Requirements**:
- **NFR-003.1**: WebUI uptime > 99.5% (excluding maintenance)
- **NFR-003.2**: Analysis failures are retried once automatically
- **NFR-003.3**: Temporary file cleanup occurs every 1 hour
- **NFR-003.4**: Session state persists across page refreshes
- **NFR-003.5**: Qdrant disconnections trigger fallback mode (analysis without vector store)
- **NFR-003.6**: No data loss on unexpected shutdown (results cached to disk)

**Measurement**:
- Uptime monitoring (Prometheus + Grafana optional)
- Error rate tracking in logs

---

### NFR-004: Maintainability

**Priority**: Medium

**Requirements**:
- **NFR-004.1**: Code follows PEP 8 style guide
- **NFR-004.2**: Functions are documented with docstrings
- **NFR-004.3**: All Streamlit components are modular (< 200 lines per file)
- **NFR-004.4**: Configuration is externalized in `config.yaml`
- **NFR-004.5**: Logging uses Python `logging` module with DEBUG, INFO, WARN, ERROR levels
- **NFR-004.6**: Dependency versions are pinned in `requirements.txt`
- **NFR-004.7**: Unit tests cover > 80% of non-UI code

**Measurement**:
- Linting with `ruff` or `black`
- Coverage report with `pytest-cov`

---

### NFR-005: Security

**Priority**: Medium

**Requirements**:
- **NFR-005.1**: Uploaded files are sandboxed in temporary directories
- **NFR-005.2**: File uploads are scanned for suspicious content (e.g., no `.exe`, `.sh` execution)
- **NFR-005.3**: No code execution from uploaded files (static analysis only)
- **NFR-005.4**: Qdrant connections use authentication (optional, configurable)
- **NFR-005.5**: WebUI does not expose internal file paths to users
- **NFR-005.6**: No sensitive data (API keys, credentials) stored in logs
- **NFR-005.7**: HTTPS recommended for production deployments (nginx reverse proxy)

**Measurement**:
- Security audit checklist
- Dependency vulnerability scanning (`pip-audit`)

---

### NFR-006: Scalability

**Priority**: Low (Initial Release)

**Requirements**:
- **NFR-006.1**: Architecture supports horizontal scaling (stateless WebUI)
- **NFR-006.2**: Qdrant can be scaled independently
- **NFR-006.3**: Analysis tasks can be offloaded to worker queue (future: Celery)
- **NFR-006.4**: Session storage can be moved to Redis (future enhancement)

**Measurement**:
- Load testing with 50+ concurrent analyses

---

## 4. UI Wireframes (Textual)

### 4.1 Home Page

```
╔═══════════════════════════════════════════════════════════════╗
║  🥜🍇 PBJRAG WebUI - Code Analysis Made Simple               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Welcome to PBJRAG! Analyze your code with 9-dimensional     ║
║  Differential Symbolic Calculus.                             ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │  📁 Upload File or Directory                        │     ║
║  │  ┌───────────────────────────────────────────────┐  │     ║
║  │  │  [ Browse Files... ]                          │  │     ║
║  │  └───────────────────────────────────────────────┘  │     ║
║  │                                                      │     ║
║  │  Or enter a file path:                              │     ║
║  │  ┌───────────────────────────────────────────────┐  │     ║
║  │  │  /path/to/your/code.py                        │  │     ║
║  │  └───────────────────────────────────────────────┘  │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ⚙️ Analysis Settings                                        ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │  Purpose: [Coherence ▼]                             │     ║
║  │  Enable Vector Store: [✓] (requires Qdrant)         │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║                   [ 🚀 Analyze Code ]                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

### 4.2 Analysis Progress Page

```
╔═══════════════════════════════════════════════════════════════╗
║  🥜🍇 PBJRAG - Analyzing: my_project/src/auth.py             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Stage 2/4: Calculating Blessings                            ║
║                                                               ║
║  Progress:                                                    ║
║  ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░ 45%           ║
║                                                               ║
║  Estimated time remaining: 18 seconds                        ║
║                                                               ║
║  ✓ Chunking complete: 127 chunks identified                  ║
║  ⏳ Analyzing dimensions...                                   ║
║  ⏳ Pending: Vector embedding                                 ║
║  ⏳ Pending: Finalizing report                                ║
║                                                               ║
║                      [ Cancel ]                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

### 4.3 Results Dashboard

```
╔═══════════════════════════════════════════════════════════════╗
║  🥜🍇 PBJRAG Results - my_project/src/                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Tabs: [Overview] [Chunks] [Search] [Export] [Settings]     ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📊 Overall Metrics                                           ║
║  ┌─────────────────┬─────────────────┬─────────────────┐     ║
║  │ Blessing: 0.68  │ EPC: 0.72       │ Chunks: 127     │     ║
║  │ Φ~ (Good)       │                 │ Files: 12       │     ║
║  └─────────────────┴─────────────────┴─────────────────┘     ║
║                                                               ║
║  🥪 Blessing Distribution        📈 Phase Distribution       ║
║  ┌───────────────────┐            ┌───────────────────┐     ║
║  │      Φ+ 42%       │            │ Compost      8    │     ║
║  │      Φ~ 39%       │            │ Reflection  12    │     ║
║  │      Φ- 19%       │            │ Becoming    16    │     ║
║  │                   │            │ Stillness   45 ← │     ║
║  └───────────────────┘            │ Turning     28    │     ║
║                                    │ Emergent    15    │     ║
║  🌀 9-Dimension Radar              │ Grinding     3    │     ║
║  ┌───────────────────┐            └───────────────────┘     ║
║  │   (Radar chart)   │                                       ║
║  │   Showing avg     │                                       ║
║  │   across all      │                                       ║
║  │   chunks          │                                       ║
║  └───────────────────┘                                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

### 4.4 Chunk Detail View

```
╔═══════════════════════════════════════════════════════════════╗
║  🥜🍇 Chunk Detail - src/auth/login.py:45-78                 ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Blessing: Φ+  Phase: Stillness  EPC: 0.82                   ║
║                                                               ║
║  📝 Code Preview                                              ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │ 45  def authenticate_user(email: str, password: str):│     ║
║  │ 46      """                                          │     ║
║  │ 47      Verify user credentials securely.           │     ║
║  │ 48      ...                                          │     ║
║  │ 78      return user                                  │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  🌀 9-Dimensional Analysis                                    ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │  Σ Semantic:     0.88  (Strong naming & purpose)    │     ║
║  │  Ε Emotional:    0.76  (Good documentation)         │     ║
║  │  Θ Ethical:      0.85  (Security best practices)    │     ║
║  │  Τ Temporal:     0.72  (Stable over time)           │     ║
║  │  Ξ Entropic:     0.18  (Low complexity)             │     ║
║  │  Ρ Rhythmic:     0.90  (Excellent flow)             │     ║
║  │  Ω Contradiction: 0.12  (Minimal conflicts)         │     ║
║  │  Γ Relational:   0.80  (Clear dependencies)         │     ║
║  │  Μ Emergent:     0.42  (Standard approach)          │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  [ Copy Code ]  [ View in Context ]  [ Back to List ]        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 5. API Endpoints (Internal)

The WebUI uses PBJRAG's Python API internally. No REST API is exposed initially.

### 5.1 Core Analysis API

```python
from pbjrag import DSCAnalyzer

# Initialize analyzer
analyzer = DSCAnalyzer(config={
    "purpose": "coherence",
    "enable_vector_store": True,
    "qdrant_host": "qdrant",
    "qdrant_port": 6333
})

# Analyze file
chunks = analyzer.analyze_file("/path/to/file.py")

# Analyze directory
report = analyzer.analyze_project("/path/to/project")

# Semantic search (if Qdrant enabled)
results = analyzer.search(query="error handling patterns", top_k=10)
```

### 5.2 Data Models

**Chunk Object**:
```python
{
    "id": "chunk_abc123",
    "file_path": "src/auth/login.py",
    "line_start": 45,
    "line_end": 78,
    "code": "def authenticate_user(...):\n    ...",
    "blessing": {
        "tier": "Φ+",
        "epc": 0.82,
        "phase": "Stillness",
        "dimensions": {
            "semantic": 0.88,
            "emotional": 0.76,
            "ethical": 0.85,
            "temporal": 0.72,
            "entropic": 0.18,
            "rhythmic": 0.90,
            "contradiction": 0.12,
            "relational": 0.80,
            "emergent": 0.42
        }
    },
    "embedding": [0.12, 0.45, ...],  # 768-dim vector
    "metadata": {
        "language": "python",
        "complexity": 4,
        "loc": 34
    }
}
```

**Analysis Report**:
```python
{
    "summary": {
        "total_chunks": 127,
        "total_files": 12,
        "avg_blessing": 0.68,
        "avg_epc": 0.72,
        "blessing_distribution": {
            "phi_plus": 53,
            "phi_tilde": 50,
            "phi_minus": 24
        },
        "phase_distribution": {
            "compost": 8,
            "reflection": 12,
            "becoming": 16,
            "stillness": 45,
            "turning": 28,
            "emergent": 15,
            "grinding": 3
        }
    },
    "chunks": [...],  # List of chunk objects
    "metadata": {
        "pbjrag_version": "3.0.0",
        "analysis_config": {...},
        "timestamp": "2025-12-05T14:30:22Z"
    }
}
```

---

## 6. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ 1. Upload file/dir
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT WEBUI (Frontend)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Upload Page │  │ Config Page │  │ Results Page │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ 2. Call analyze()
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              PBJRAG CORE (Backend)                           │
│  ┌───────────────────────────────────────────────┐          │
│  │  DSCAnalyzer                                   │          │
│  │  ┌─────────────┐  ┌──────────────┐           │          │
│  │  │  Chunker    │  │  Metrics     │           │          │
│  │  └─────────────┘  └──────────────┘           │          │
│  │  ┌─────────────┐  ┌──────────────┐           │          │
│  │  │  Phase Mgr  │  │  Orchestrator│           │          │
│  │  └─────────────┘  └──────────────┘           │          │
│  └───────────────────────────────────────────────┘          │
└───────────────────┬─────────────────┬───────────────────────┘
                    │                 │
        3. Embed    │                 │ 4. Store vectors
        chunks      │                 │
                    ▼                 ▼
┌──────────────────────────────────────────────────────────┐
│             QDRANT VECTOR STORE (Optional)                │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Collections: pbjrag_chunks                        │  │
│  │  Vectors: 768-dim embeddings                       │  │
│  │  Payload: chunk metadata + blessing scores         │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ 5. Semantic search
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT WEBUI (Results)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Charts      │  │ Chunk List  │  │ Search UI   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                       │
                       │ 6. Export
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FILE SYSTEM (Exports)                           │
│  pbjrag_report_2025-12-05_14-30-22.json                     │
│  pbjrag_report_2025-12-05_14-30-22.html                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Docker Architecture

### 7.1 Stack Overview

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.7.4
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  pbjrag-webui:
    build: .
    ports:
      - "8501:8501"
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - PBJRAG_ENV=production
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      qdrant:
        condition: service_healthy
    restart: unless-stopped

volumes:
  qdrant_data:
```

### 7.2 Dockerfile for WebUI

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 7.3 Quickstart Experience

**User Journey**:
```bash
# Clone repository
git clone https://github.com/Project-Navi/navi-pbjrag
cd navi-pbjrag

# Start services (Qdrant + WebUI)
docker-compose up -d

# Wait for services to be ready (~15 seconds)
docker-compose logs -f pbjrag-webui

# Open browser
# Navigate to http://localhost:8501

# ✓ WebUI is ready!
```

**Expected Output**:
```
qdrant_1        | [2025-12-05 14:30:15] INFO: Qdrant HTTP API listening on 0.0.0.0:6333
pbjrag-webui_1  | [2025-12-05 14:30:22] INFO: Streamlit app started at http://0.0.0.0:8501
pbjrag-webui_1  | [2025-12-05 14:30:22] INFO: Connected to Qdrant at qdrant:6333
pbjrag-webui_1  | [2025-12-05 14:30:22] INFO: PBJRAG WebUI ready!
```

---

## 8. Technology Stack

### 8.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **WebUI Framework** | Streamlit | 1.29+ | Interactive web interface |
| **Backend** | PBJRAG (Python) | 3.0.0 | Code analysis engine |
| **Vector Store** | Qdrant | 1.7+ | Semantic search |
| **Charts** | Plotly | 5.17+ | Interactive visualizations |
| **Code Highlighting** | Pygments | 2.17+ | Syntax highlighting |
| **Container** | Docker | 20.10+ | Deployment orchestration |

### 8.2 Dependencies

**requirements.txt**:
```
streamlit==1.29.0
pbjrag==3.0.0
plotly==5.17.0
pygments==2.17.0
qdrant-client==1.7.0
pandas==2.1.3
numpy==1.24.0
pyyaml==6.0.1
```

---

## 9. User Stories

### US-001: As a developer, I want to analyze my codebase without CLI
**Priority**: High
**Story**: "I want to upload my Python project and see blessing scores in a dashboard, so I can quickly identify code quality issues without learning command-line tools."

### US-002: As a tech lead, I want to search for code patterns semantically
**Priority**: High
**Story**: "I want to type 'authentication patterns' and find all related code chunks, so I can ensure consistency across my team's codebase."

### US-003: As a data scientist, I want to export analysis results
**Priority**: Medium
**Story**: "I want to download analysis results as JSON, so I can integrate PBJRAG insights into my ML pipeline."

### US-004: As a non-technical manager, I want visual summaries
**Priority**: Medium
**Story**: "I want to see pie charts and phase distributions, so I can understand code health without reading code."

### US-005: As an auditor, I want to drill into specific code chunks
**Priority**: Medium
**Story**: "I want to click on a Φ- (low quality) chunk and see exactly what dimensions are problematic, so I can provide actionable feedback."

---

## 10. Success Criteria

### 10.1 Minimum Viable Product (MVP)

✅ **Complete** when:
1. User can upload a file and see blessing distribution
2. User can view 9-dimensional analysis for any chunk
3. Semantic search returns relevant results (if Qdrant is running)
4. `docker-compose up` launches both Qdrant and WebUI
5. User can export results as JSON or Markdown
6. All core visualizations render correctly (pie, bar, radar)

### 10.2 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **User Adoption** | 50+ GitHub stars in 1 month | GitHub analytics |
| **Ease of Use** | 90% of users complete analysis without docs | User testing |
| **Performance** | Analysis time < 30s for 1000 LOC | Benchmarks |
| **Error Rate** | < 5% of analyses fail | Error logs |
| **Search Accuracy** | Top-3 results relevant 80% of time | Manual review |

---

## 11. Risk Assessment

### 11.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Qdrant setup complexity** | Medium | High | Provide detailed Docker Compose setup, fallback mode without Qdrant |
| **Large file processing** | High | Medium | Implement file size limits (10MB), chunked processing |
| **Streamlit performance** | Medium | Medium | Lazy loading, pagination, caching |
| **Cross-platform Docker issues** | Low | High | Test on Linux, macOS, Windows; provide platform-specific notes |

### 11.2 User Experience Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Overwhelming UI** | Medium | High | Progressive disclosure, clear defaults, tooltips |
| **Confusing terminology** | High | Medium | Glossary, help section, "translation modes" (devops/scholar/general) |
| **Slow feedback loop** | Medium | Medium | Real-time progress bars, estimated time remaining |

---

## 12. Future Enhancements (Out of Scope)

### 12.1 V2.0 Features

- **Multi-Project Comparison**: Side-by-side blessing analysis of two codebases
- **Historical Trends**: Track blessing scores over time (requires database)
- **AI-Powered Insights**: GPT-4 explanations of Φ- chunks
- **Collaborative Annotations**: Team comments on code chunks
- **Custom Dimension Weights**: User-defined emphasis on dimensions
- **Real-Time Analysis**: Watch mode for live code editing

### 12.2 Enterprise Features

- **SSO Authentication**: LDAP, OAuth integration
- **Role-Based Access Control**: Admin, viewer, analyst roles
- **Multi-Tenant Support**: Isolated workspaces per team
- **Scheduled Analysis**: Cron-based project scanning
- **Slack/Email Notifications**: Alerts for code quality degradation

---

## 13. Acceptance Criteria Summary

### 13.1 Functional Acceptance

- [ ] User can upload files via drag-and-drop or file picker
- [ ] Analysis progress is shown with real-time updates
- [ ] Blessing tier distribution is visualized as pie + bar charts
- [ ] Phase distribution is shown with color-coded bars
- [ ] 9-dimensional radar chart displays for any chunk
- [ ] Code chunks are browsable with filtering and sorting
- [ ] Semantic search returns top-10 relevant chunks
- [ ] Export works for JSON, Markdown, HTML formats
- [ ] Configuration panel allows purpose and Qdrant toggle
- [ ] Error messages are clear and actionable

### 13.2 Non-Functional Acceptance

- [ ] WebUI loads in < 2 seconds
- [ ] Analysis completes in < 30 seconds for 1000 LOC
- [ ] Semantic search returns results in < 3 seconds
- [ ] `docker-compose up` succeeds on Linux/macOS/Windows
- [ ] UI is responsive on 1280x720+ displays
- [ ] Code is PEP 8 compliant with 80%+ test coverage
- [ ] Documentation includes quickstart and troubleshooting

---

## 14. References

### 14.1 Internal Documentation

- [PBJRAG README](../README.md)
- [9 Dimensions Explained](./9-dimensions.md)
- [PBJRAG API Reference](./api.md)
- [Migration Plan](./navi-pbjrag-migration-plan.md)

### 14.2 External Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Qdrant Vector Database](https://qdrant.tech/documentation/)
- [Plotly Python](https://plotly.com/python/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

## 15. Glossary

| Term | Definition |
|------|------------|
| **Blessing Tier** | Quality classification: Φ+ (excellent), Φ~ (good), Φ- (needs work) |
| **EPC** | Emergence Potential Coefficient - holistic quality score (0.0-1.0) |
| **DSC** | Differential Symbolic Calculus - mathematical framework for code analysis |
| **Chunk** | Semantic code segment (function, class, module) |
| **Phase** | Lifecycle stage: Compost, Reflection, Becoming, Stillness, Turning, Emergent, Grinding |
| **Dimension** | One of 9 aspects of code presence (Semantic, Emotional, Ethical, etc.) |
| **Vector Store** | Qdrant database for semantic similarity search |
| **Radar Chart** | Spider chart showing 9-dimensional analysis |

---

## 16. Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-05 | SPARC Spec Agent | Initial specification |

---

## 17. Approval Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | ___________ | ___________ | ______ |
| Tech Lead | ___________ | ___________ | ______ |
| DevOps | ___________ | ___________ | ______ |
| UX Designer | ___________ | ___________ | ______ |

---

**End of Specification**

*This document is the foundation for the Pseudocode and Architecture phases of SPARC methodology.*
