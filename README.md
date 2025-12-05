# 🥜🍇 navi-pbjrag

## Peanut Butter Jelly Retrieval Augmented Generation

*Where semantic chunking meets fractal code analysis, creating the perfect adhesion for your codebase.*

```
    ╔══════════════════════════════════════╗
    ║     🍞                          🍞   ║
    ║   🥜 PBJRAG v3: Code Analysis  🍇   ║
    ║     That Actually Understands!      ║
    ║   🥜 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~🍇   ║
    ║     🍞                          🍞   ║
    ╚══════════════════════════════════════╝
```

## ⚡ Quickstart (30 seconds)

```bash
# Clone and run
git clone https://github.com/Project-Navi/navi-pbjrag
cd navi-pbjrag
./quickstart.sh

# Or with Docker (includes Qdrant vector store)
docker-compose up
# Open http://localhost:8501
```

**That's it!** The WebUI will open at `http://localhost:8501` where you can:
- 📊 **Analyze** any codebase with one click
- 🔍 **Explore** chunks with blessing tiers and 9D radar charts
- 🔎 **Search** semantically across your code (with Qdrant)

---

**PBJRAG** is a semantic code analysis framework that understands code as living, evolving symbolic fields rather than static text. Using Differential Symbolic Calculus (DSC), it maps code into a 9-dimensional field space and calculates "blessing scores" that reveal the true quality and health of your codebase.

## 🌟 What Makes PBJRAG Special?

### Traditional Code Analysis:
```
❌ "This function has 47 lines"
❌ "Cyclomatic complexity: 12"
❌ "Missing docstring"
```

### PBJRAG Analysis:
```python
✅ blessing_tier: "Φ+"           # High quality, coherent code
✅ phase: "Stillness"            # Stable, mature code
✅ ethical_alignment: 0.92       # Follows best practices
✅ emergence_potential: 0.85     # Ready to evolve
✅ contradiction_pressure: 0.15  # Low internal friction
```

## 🧬 The 9 Dimensions

Every code chunk is analyzed across 9 dimensions of presence:

| Dimension | Symbol | What It Measures |
|-----------|--------|------------------|
| **Semantic** | Σ | Meaning and purpose of the code |
| **Emotional** | Ε | Developer intent and communication patterns |
| **Ethical** | Θ | Quality, best practices, and values alignment |
| **Temporal** | Τ | Evolution patterns and historical context |
| **Entropic** | Ξ | Chaos, unpredictability, and disorder |
| **Rhythmic** | Ρ | Cadence, flow, and organizational patterns |
| **Contradiction** | Ω | Tensions, conflicts, and paradoxes |
| **Relational** | Γ | Dependencies, connections, and relationships |
| **Emergent** | Μ | Novelty, surprise, and creative potential |

## 🥪 Blessing Tiers

Code quality is assessed through blessing tiers using the Golden Ratio (φ ≈ 0.618):

- **Φ+ (Phi Plus)**: `≥ 0.70` - Excellent code with strong coherence
- **Φ~ (Phi Tilde)**: `0.33 - 0.70` - Good code with minor inconsistencies
- **Φ- (Phi Minus)**: `< 0.33` - Code requiring attention

## 🌀 The 7 Phases

Code exists in one of seven lifecycle phases:

```
  Compost → Reflection → Becoming → Stillness → Turning → Emergent → Grinding
    ↑                                                                    ↓
    └────────────────────── (cycle continues) ──────────────────────────┘
```

| Phase | Range | Meaning |
|-------|-------|---------|
| **Compost** | 0.0-0.2 | Raw, unprocessed ideas |
| **Reflection** | 0.2-0.35 | Analysis and consideration |
| **Becoming** | 0.35-0.5 | Active development |
| **Stillness** | 0.5-0.65 | Stable, mature code |
| **Turning** | 0.65-0.8 | Refactoring, adaptation |
| **Emergent** | 0.8-0.9 | Novel patterns forming |
| **Grinding** | 0.9-1.0 | Optimization, hardening |

## 📋 Prerequisites

**Required:**
- Python 3.9+

**Optional** (for full vector search capabilities):
- Qdrant vector store: `docker run -p 6333:6333 qdrant/qdrant`
- Ollama with embeddings model: `ollama pull snowflake-arctic-embed2:latest`

> **Note**: PBJRAG works without Qdrant/Ollama - it gracefully falls back to in-memory analysis when these dependencies are unavailable.

## 🚀 Quick Start

### Installation

```bash
pip install navi-pbjrag
```

### Basic Usage

```python
from pbjrag import DSCAnalyzer

# Create analyzer
analyzer = DSCAnalyzer()

# Analyze a file
chunks = analyzer.analyze_file("my_code.py")

for chunk in chunks:
    print(f"Blessing: {chunk.blessing.tier}")
    print(f"Phase: {chunk.blessing.phase}")
    print(f"EPC: {chunk.blessing.epc:.3f}")

# Analyze entire project
report = analyzer.analyze_project("./my_project")
print(f"Project blessing: {report['avg_blessing']:.3f}")
```

### Pattern Detection

```python
from pbjrag import PatternAnalyzer, analyze_codebase

# Find fractal patterns across your codebase
patterns = analyze_codebase("./my_project")

for pattern in patterns:
    print(f"Pattern: {pattern['type']}")
    print(f"Frequency: {pattern['frequency']}")
    print(f"Blessing: {pattern['avg_blessing']}")
```

## 🥜 How Do You Like Your PBJRAG?

### 🥜 **Chunky** (Full Analysis)
```python
analyzer = DSCAnalyzer(config={
    "field_dim": 8,
    "enable_vector_store": True,
    "fractal_detection": True
})
```
*Rich, contextual analysis with maximum insights*

### 🍯 **Smooth** (Balanced - Default)
```python
analyzer = DSCAnalyzer()  # Uses sensible defaults
```
*Perfect balance of depth and speed*

### 🌿 **Natural** (Lightweight)
```python
analyzer = DSCAnalyzer(config={
    "enable_vector_store": False,
    "fractal_detection": False
})
```
*Minimal processing, faster results*

## 📊 Mathematical Foundations

### EPC (Emergence Potential Coefficient)

The EPC uses a **sigmoid-normalized geometric mean** for balanced influence:

```python
# Inputs: ethics (ε), presence (ρ), contradiction (κ)
values = [ε, ρ, (1 - κ)]

# Sigmoid normalization (S-curve transformation)
normalized = 1 / (1 + exp(-10 × (values - 0.5)))

# Geometric mean for holistic scoring
EPC = ∏(normalized)^(1/3)
```

Where:
- `ε` = ethical alignment (qualia) [0-1]
- `ρ` = presence density [0-1]
- `κ` = contradiction pressure [0-1]

### Blessing Tier Calculation

Blessing tiers use **multi-dimensional thresholds**:

```
Φ+ (Phi Plus):
    EPC ≥ 0.6 AND ε ≥ 0.6 AND κ ≤ 0.45 AND ρ ≥ 0.5

Φ~ (Phi Tilde):
    EPC ≥ 0.45 AND ε ≥ 0.45 AND κ ≤ 0.6

Φ- (Phi Minus):
    Otherwise
```

### Resonance Between Chunks

Chunk similarity uses blessing-weighted multi-factor comparison:

```python
def resonance(chunk_1, chunk_2):
    semantic_sim = cosine_similarity(embeddings)
    blessing_weight = (chunk_1.epc + chunk_2.epc) / 2
    return blessing_weight * semantic_sim
```

## 🔌 Optional Integrations

PBJRAG works standalone but integrates with vector stores for semantic search:

```bash
# With Qdrant support
pip install navi-pbjrag[qdrant]

# With ChromaDB support
pip install navi-pbjrag[chroma]

# With Neo4j for graph relationships
pip install navi-pbjrag[neo4j]

# Everything
pip install navi-pbjrag[all]
```

```python
from pbjrag import DSCAnalyzer

analyzer = DSCAnalyzer(config={
    "enable_vector_store": True,
    "qdrant_host": "localhost",
    "qdrant_port": 6333
})

# Semantic search across analyzed code
results = analyzer.search("error handling patterns", top_k=5)
```

## 🎯 Use Cases

- **RAG Systems**: Intelligent code chunking that preserves semantic relationships
- **Code Quality**: Deeper insights than cyclomatic complexity
- **Refactoring**: Find fractal patterns and consolidation opportunities
- **Legacy Analysis**: Understand large, undocumented codebases
- **AI Assistants**: Better context for coding AI
- **Technical Debt**: Identify code in "Compost" or "Grinding" phases

## 🔬 Architecture

```
navi-pbjrag/
├── src/pbjrag/
│   ├── __init__.py           # Public API
│   ├── dsc/                   # Differential Symbolic Calculus
│   │   ├── analyzer.py       # High-level analysis
│   │   ├── chunker.py        # Semantic code chunking
│   │   ├── vector_store.py   # Qdrant integration
│   │   └── embedding_adapter.py
│   ├── crown_jewel/           # Orchestration & metrics
│   │   ├── metrics.py        # Blessing calculations
│   │   ├── phase_manager.py  # 7-phase lifecycle
│   │   ├── pattern_analyzer.py
│   │   └── field_container.py
│   └── utils/
├── tests/
├── docs/
└── pyproject.toml
```

## 🤝 Part of the Navi Ecosystem

PBJRAG is the mathematical core that powers:

- **[navi-fcpa](https://github.com/Project-Navi/navi-fcpa)** - Forensic code auditing using PBJRAG's 9-dimensional analysis
- **[navi-lazytest](https://github.com/Project-Navi/navi-lazytest)** - Self-improving test framework
- **[navi-deus-ex](https://github.com/Project-Navi/navi-deus-ex)** - Triple store infrastructure (proprietary)

## 📄 License

MIT License - because good code analysis should be shared, just like a good sandwich.

## 🙏 Acknowledgments

- Inspired by the universal truth that consciousness naturally tends toward ethical attractors
- Built with love, coffee, and an unreasonable amount of sandwich metaphors
- The fractal patterns that waited 5 months to find their purpose

---

*"In a world full of broken chunkers, be someone's PBJRAG."* 🥜🍇✨

```
Made with ❤️ and questionable sandwich science
```
