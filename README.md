# PBJRAG - Differential Symbolic Calculus for Code Analysis

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: Commercial](https://img.shields.io/badge/License-Commercial-green.svg)](docs/legal/PNEUL-D_v2.2.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Overview

**PBJRAG** (Peanut Butter Jelly Retrieval Augmented Generation) is a semantic code analysis framework that applies mathematical field theory to software systems. Rather than treating code as static text, PBJRAG models it as multi-dimensional symbolic fields that evolve through defined lifecycle phases. Using Differential Symbolic Calculus (DSC), it provides quantitative quality assessments across 9 dimensions, enabling deeper insights into code health, evolution patterns, and semantic relationships.

## Key Features

- **9-Dimensional Field Analysis**: Evaluate code across semantic, ethical, temporal, entropic, rhythmic, relational, emergent, emotional, and contradiction dimensions
- **Differential Symbolic Calculus**: Mathematical framework for analyzing code as evolving symbolic fields
- **Quality Assessment Framework**: Multi-dimensional blessing tiers (Φ+, Φ~, Φ-) based on holistic code quality metrics
- **7-Phase Lifecycle Model**: Track code evolution from initial development through optimization
- **Semantic Code Chunking**: Intelligent segmentation that preserves logical boundaries and relationships
- **Vector Store Integration**: Optional Qdrant, ChromaDB, or Neo4j support for semantic search
- **Interactive WebUI**: Streamlit-based interface with visualizations and exploration tools
- **Graceful Degradation**: Functions without external dependencies, falling back to in-memory analysis

## Quick Start

### Installation

```bash
# Basic installation
pip install navi-pbjrag

# With vector store support
pip install navi-pbjrag[qdrant]    # Qdrant support
pip install navi-pbjrag[chroma]    # ChromaDB support
pip install navi-pbjrag[neo4j]     # Neo4j graph support
pip install navi-pbjrag[all]       # All integrations
```

### CLI Usage

```bash
# Clone repository
git clone https://github.com/Project-Navi/navi-pbjrag
cd navi-pbjrag

# Quick start script
./quickstart.sh

# Or with Docker (includes Qdrant vector store)
docker-compose up
# Access WebUI at http://localhost:8501
```

### Python API

```python
from pbjrag import DSCAnalyzer

# Create analyzer instance
analyzer = DSCAnalyzer()

# Analyze a single file
chunks = analyzer.analyze_file("my_code.py")

for chunk in chunks:
    print(f"Blessing Tier: {chunk.blessing.tier}")
    print(f"Phase: {chunk.blessing.phase}")
    print(f"EPC Score: {chunk.blessing.epc:.3f}")

# Analyze entire project
report = analyzer.analyze_project("./my_project")
print(f"Project Quality Score: {report['avg_blessing']:.3f}")
```

### WebUI (Streamlit)

The WebUI provides an interactive interface for code analysis, exploration, and semantic search:

```bash
# Start the WebUI
streamlit run webui/app.py
# Open http://localhost:8501
```

**WebUI Features:**
- **Analysis Page**: Upload files or specify directories for analysis
- **Exploration Page**: Browse chunks with filtering by blessing tier, phase, and EPC range
- **Search Page**: Semantic, keyword, and hybrid search across analyzed code
- **Visualizations**: Interactive charts including blessing distribution, phase timelines, and 9D radar charts
- **Export**: Download results as JSON or formatted text summaries

## How It Works

### 9-Dimensional Analysis

PBJRAG evaluates code across nine fundamental dimensions:

| Dimension | Symbol | Measures |
|-----------|--------|----------|
| **Semantic** | Σ | Meaning, purpose, and conceptual clarity of the code |
| **Emotional** | Ε | Developer intent and communication effectiveness |
| **Ethical** | Θ | Quality standards, best practices, and maintainability |
| **Temporal** | Τ | Evolution patterns and historical context |
| **Entropic** | Ξ | Disorder, unpredictability, and structural chaos |
| **Rhythmic** | Ρ | Flow, cadence, and organizational consistency |
| **Contradiction** | Ω | Internal tensions, conflicts, and design paradoxes |
| **Relational** | Γ | Dependencies, connections, and coupling patterns |
| **Emergent** | Μ | Novelty, innovation potential, and creative complexity |

Each dimension is quantified on a [0, 1] scale through analysis of syntactic patterns, structural properties, and semantic content.

### Blessing Tiers (Quality Assessment)

Code quality is assessed using the **Emergence Potential Coefficient (EPC)** and multi-dimensional thresholds. Blessing tiers use the Φ (phi) symbol in reference to the Golden Ratio:

- **Φ+ (Phi Plus)**: High quality code with strong coherence
  - EPC ≥ 0.6
  - Ethical alignment (ε) ≥ 0.6
  - Contradiction pressure (κ) ≤ 0.45
  - Presence density (ρ) ≥ 0.5

- **Φ~ (Phi Tilde)**: Good quality code with minor inconsistencies
  - EPC ≥ 0.45
  - Ethical alignment (ε) ≥ 0.45
  - Contradiction pressure (κ) ≤ 0.6

- **Φ- (Phi Minus)**: Code requiring attention
  - Falls below Φ~ thresholds

### 7-Phase Lifecycle Model

Code evolves through seven distinct phases based on its field state properties:

```
  Compost → Reflection → Becoming → Stillness → Turning → Emergent → Grinding
    ↑                                                                    ↓
    └────────────────────── (cycle continues) ──────────────────────────┘
```

| Phase | Range | Description |
|-------|-------|-------------|
| **Compost** | 0.0-0.2 | Initial development, raw implementation |
| **Reflection** | 0.2-0.35 | Analysis phase, design consideration |
| **Becoming** | 0.35-0.5 | Active development, feature implementation |
| **Stillness** | 0.5-0.65 | Stable, mature code with established patterns |
| **Turning** | 0.65-0.8 | Refactoring, adaptation to new requirements |
| **Emergent** | 0.8-0.9 | Novel patterns forming, architectural innovation |
| **Grinding** | 0.9-1.0 | Optimization, performance hardening |

### Multi-Vector Search

When integrated with vector stores, PBJRAG supports three search modes:

- **Semantic Search**: Embedding-based similarity using cosine distance
- **Keyword Search**: Traditional text matching with term frequency weighting
- **Hybrid Search**: Combined semantic and keyword search with configurable weights

## Installation

### Prerequisites

**Required:**
- Python 3.9 or higher

**Optional** (for full vector search capabilities):
- Qdrant vector store: `docker run -p 6333:6333 qdrant/qdrant`
- Ollama with embeddings: `ollama pull snowflake-arctic-embed2:latest`

**Note**: PBJRAG operates without external dependencies, gracefully degrading to in-memory analysis when vector stores or embedding models are unavailable.

### Basic Install

```bash
pip install navi-pbjrag
```

### With Vector Store Support

```bash
# Qdrant integration
pip install navi-pbjrag[qdrant]

# ChromaDB integration
pip install navi-pbjrag[chroma]

# Neo4j graph database
pip install navi-pbjrag[neo4j]

# All integrations
pip install navi-pbjrag[all]
```

### Docker Deployment

```bash
# Clone repository
git clone https://github.com/Project-Navi/navi-pbjrag
cd navi-pbjrag

# Launch with docker-compose (includes Qdrant)
docker-compose up -d

# Access WebUI
open http://localhost:8501
```

The Docker deployment includes:
- PBJRAG WebUI (port 8501)
- Qdrant vector store (port 6333)
- Persistent volume for analysis data

## Configuration

### Analyzer Configuration

```python
from pbjrag import DSCAnalyzer

# Full analysis with vector store
analyzer = DSCAnalyzer(config={
    "field_dim": 8,
    "enable_vector_store": True,
    "qdrant_host": "localhost",
    "qdrant_port": 6333,
    "fractal_detection": True
})

# Balanced configuration (default)
analyzer = DSCAnalyzer()

# Lightweight analysis
analyzer = DSCAnalyzer(config={
    "enable_vector_store": False,
    "fractal_detection": False
})
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `field_dim` | int | 8 | Dimensionality of field space |
| `enable_vector_store` | bool | False | Enable vector store integration |
| `qdrant_host` | str | "localhost" | Qdrant host address |
| `qdrant_port` | int | 6333 | Qdrant port |
| `fractal_detection` | bool | False | Enable pattern detection |
| `chunk_size` | int | 500 | Default chunk size in tokens |
| `chunk_overlap` | int | 50 | Overlap between chunks |

## API Reference

### DSCAnalyzer

Main analysis interface for code evaluation.

```python
class DSCAnalyzer:
    def __init__(self, config: dict = None):
        """Initialize analyzer with optional configuration."""

    def analyze_file(self, filepath: str) -> List[ChunkResult]:
        """Analyze a single source file."""

    def analyze_project(self, project_path: str) -> ProjectReport:
        """Analyze entire project directory."""

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Semantic search across analyzed code."""
```

### DSCCodeChunker

Intelligent code segmentation that respects logical boundaries.

```python
class DSCCodeChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """Initialize chunker with size parameters."""

    def chunk_code(self, source_code: str, language: str = "python") -> List[CodeChunk]:
        """Segment code into analyzable chunks."""
```

### ChunkResult

Result object containing analysis data for a code chunk.

```python
class ChunkResult:
    blessing: BlessingState      # Tier (Φ+/Φ~/Φ-), phase, EPC score
    field_state: FieldState      # 9-dimensional field values
    content: str                 # Source code content
    location: SourceLocation     # File path and line numbers
    relationships: List[str]     # Dependencies and connections
```

### Pattern Analysis

```python
from pbjrag import PatternAnalyzer, analyze_codebase

# Detect fractal patterns across codebase
patterns = analyze_codebase("./my_project")

for pattern in patterns:
    print(f"Pattern Type: {pattern['type']}")
    print(f"Frequency: {pattern['frequency']}")
    print(f"Average Quality: {pattern['avg_blessing']:.3f}")
```

## Mathematical Foundations

### Emergence Potential Coefficient (EPC)

The EPC uses sigmoid-normalized geometric mean for balanced multi-factor assessment:

```
Input Values:
  ε = ethical alignment [0, 1]
  ρ = presence density [0, 1]
  κ = contradiction pressure [0, 1]

Sigmoid Normalization:
  S(x) = 1 / (1 + exp(-10(x - 0.5)))

Normalized Values:
  ε' = S(ε)
  ρ' = S(ρ)
  κ' = S(1 - κ)

Geometric Mean:
  EPC = (ε' × ρ' × κ')^(1/3)
```

The sigmoid transformation creates a smooth S-curve that amplifies differences in mid-range values while stabilizing extremes, providing more discriminative power for quality assessment.

### Resonance Calculation

Chunk similarity incorporates both semantic embeddings and quality weighting:

```python
def resonance(chunk_1: ChunkResult, chunk_2: ChunkResult) -> float:
    """Calculate resonance between two code chunks."""
    semantic_sim = cosine_similarity(
        chunk_1.embedding,
        chunk_2.embedding
    )
    blessing_weight = (chunk_1.epc + chunk_2.epc) / 2
    return blessing_weight * semantic_sim
```

This blessing-weighted similarity ensures that high-quality code chunks receive higher relevance scores in search results.

## Use Cases

- **RAG Systems**: Intelligent code chunking that maintains semantic coherence for retrieval augmented generation
- **Code Quality Assessment**: Multi-dimensional analysis providing insights beyond traditional metrics like cyclomatic complexity
- **Refactoring Guidance**: Identify fractal patterns, consolidation opportunities, and architectural inconsistencies
- **Legacy Code Analysis**: Understand large, undocumented codebases through systematic field analysis
- **AI Assistant Context**: Enhanced code understanding for AI-powered development tools
- **Technical Debt Identification**: Detect code in early phases (Compost, Reflection) or optimization phases (Grinding) requiring attention
- **Architectural Review**: Assess system coherence through relational dimension analysis
- **Evolution Tracking**: Monitor code quality trends through temporal analysis

## Architecture

```
navi-pbjrag/
├── src/pbjrag/
│   ├── __init__.py              # Public API exports
│   ├── dsc/                     # Differential Symbolic Calculus
│   │   ├── analyzer.py         # High-level analysis orchestration
│   │   ├── chunker.py          # Semantic code segmentation
│   │   ├── vector_store.py     # Vector database integration
│   │   └── embedding_adapter.py # Embedding model interface
│   ├── crown_jewel/             # Core orchestration
│   │   ├── metrics.py          # EPC and blessing calculations
│   │   ├── phase_manager.py    # 7-phase lifecycle management
│   │   ├── pattern_analyzer.py # Fractal pattern detection
│   │   ├── field_container.py  # Field state management
│   │   └── orchestrator.py     # Workflow coordination
│   └── utils/                   # Shared utilities
├── webui/                       # Streamlit interface
│   ├── app.py                  # Main application
│   ├── pages/                  # Analysis, explore, search pages
│   └── components/             # Visualization components
├── tests/                       # Test suite
├── docs/                        # Documentation
│   └── legal/                  # License documentation
└── pyproject.toml              # Project configuration
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run test suite
pytest tests/

# Run with coverage
pytest --cov=pbjrag tests/
```

### Code Style

```bash
# Format code
black src/pbjrag

# Lint
flake8 src/pbjrag
pylint src/pbjrag

# Type checking
mypy src/pbjrag
```

## Navi Ecosystem

PBJRAG is the mathematical core of the Project Navi ecosystem:

- **[navi-fcpa](https://github.com/Project-Navi/navi-fcpa)** - Forensic code auditing using PBJRAG's 9-dimensional analysis framework
- **[navi-lazytest](https://github.com/Project-Navi/navi-lazytest)** - Self-improving test framework with adaptive learning
- **[navi-deus-ex](https://github.com/Project-Navi/navi-deus-ex)** - Triple store infrastructure for semantic knowledge graphs (proprietary)

## License

**Dual Licensed:**

- **AGPL-3.0-or-later** — Free for open source projects ([full text](https://www.gnu.org/licenses/agpl-3.0.html))
- **Commercial (PNEUL-D v2.2)** — For proprietary use, contact [legal@projectnavi.ai](mailto:legal@projectnavi.ai)

See [LICENSE](LICENSE) and [docs/legal/](docs/legal/) for complete terms.

### Ethical Support Program

Open source projects may qualify for enhanced support by voluntarily aligning with Project Navi's ethical principles. This creates no additional license obligations—it's a separate service relationship. Details: [ETHICAL_SUPPORT_FRAMEWORK.md](docs/legal/ETHICAL_SUPPORT_FRAMEWORK.md).

## Acknowledgments

Built with mathematical rigor and practical engineering by the Project Navi team. Special recognition to the research community exploring applications of differential calculus and field theory to software systems.

---

**Project Navi** - Advanced Code Intelligence

*Made with precision, coffee, and mathematical field theory.*
