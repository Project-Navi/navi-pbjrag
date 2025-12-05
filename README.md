# PBJRAG v3 — Qdrant-Native Code Analysis

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: Commercial](https://img.shields.io/badge/License-Commercial-green.svg)](docs/legal/PNEUL-D_v2.2.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Coverage: 80%+](https://img.shields.io/badge/coverage-80%25+-green.svg)]()

## What This Actually Is

We lint code like we screenshot video: one frame at a time.

"Does this function have too many lines?" "Is this variable named correctly?" "Did the tests pass?"

That's snapshot analysis. It tells you nothing about *trajectory*—whether your codebase is drifting toward coherence or quietly rotting from the inside.

**PBJRAG** treats code as a multi-dimensional field that evolves over time. Instead of asking "is this output okay right now?" it asks: "what direction is this system moving in?"

Each code chunk gets:
- **Blessing tier** (Φ+, Φ~, Φ-) — quality assessment across 9 dimensions
- **Phase** (compost → emergent) — lifecycle stage
- **EPC score** — emergence potential coefficient

Think of them as behavioral vital signs. You don't take them once; you track them across commits, sessions, refactors.

**v3.0.0 is Qdrant-native.** Qdrant's the only vector store we actively maintain. If you need ChromaDB or something else, there's a template in `docs/adapters/` — but you're on your own.

## The 9 Dimensions

Here's what we actually measure:

| Dimension | What It Catches |
|-----------|-----------------|
| **Semantic** (Σ) | Does this code mean what it says? Conceptual clarity. |
| **Emotional** (Ε) | Developer intent. Is this written to communicate or to survive? |
| **Ethical** (Θ) | Best practices. Maintainability. Does future-you want to touch this? |
| **Temporal** (Τ) | Evolution patterns. Is this stable or constantly patched? |
| **Entropic** (Ξ) | Chaos. Disorder. Structural unpredictability. |
| **Rhythmic** (Ρ) | Consistency. Does the codebase have a pulse or a seizure? |
| **Contradiction** (Ω) | Internal tensions. Design paradoxes. Code that argues with itself. |
| **Relational** (Γ) | Dependencies. Coupling. How tangled is the graph? |
| **Emergent** (Μ) | Innovation potential. Is something new trying to form here? |

Each dimension is [0, 1]. Together they form a field state—a fingerprint of how this code is behaving, not just what it contains.

## Blessing Tiers

The **Emergence Potential Coefficient (EPC)** combines these dimensions into a quality signal. Blessing tiers use Φ (phi) because we're pretentious like that (and because the Golden Ratio is actually relevant to coherence metrics):

- **Φ+ (Phi Plus)** — High quality. EPC ≥ 0.6, ethical ≥ 0.6, contradiction ≤ 0.45.
- **Φ~ (Phi Tilde)** — Acceptable. EPC ≥ 0.45. Needs attention but won't catch fire.
- **Φ- (Phi Minus)** — Below threshold. The codebase equivalent of "we should talk."

## 7-Phase Lifecycle

Code doesn't sit still. It moves through phases:

```
Compost → Reflection → Becoming → Stillness → Turning → Emergent → Grinding
  0.0       0.2          0.35        0.5        0.65       0.8        0.9
    ↑                                                                    ↓
    └────────────────────── (cycle continues) ──────────────────────────┘
```

| Phase | What's Happening |
|-------|------------------|
| **Compost** | Raw implementation. First draft. Survival code. |
| **Reflection** | Stepping back. Design consideration starting to show. |
| **Becoming** | Active development. Features taking shape. |
| **Stillness** | Stable. Mature. Patterns established. |
| **Turning** | Refactoring. Adapting to new requirements. |
| **Emergent** | Novel patterns forming. Architectural innovation. |
| **Grinding** | Optimization. Performance hardening. Polish. |

This isn't decorative. The phase tells you what kind of intervention makes sense. You don't refactor code in Compost—you let it breathe. You don't add features to code in Grinding—you're past that.

## Quick Start

```bash
# Install
pip install navi-pbjrag[qdrant]

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Start Ollama with Arctic embeddings
ollama pull snowflake-arctic-embed2
```

### Analyze Something

```python
from pbjrag import DSCAnalyzer

analyzer = DSCAnalyzer()

# Analyze a file
results = analyzer.analyze_file("my_code.py")
for chunk in results.get("chunks", []):
    print(f"Tier: {chunk['blessing']['tier']}")
    print(f"Phase: {chunk['blessing']['phase']}")
    print(f"EPC: {chunk['blessing']['epc']:.3f}")

# Analyze a project
report = analyzer.analyze_project("./my_project")
print(f"Total chunks: {report['total_chunks']}")
```

### Chunk Code Directly

```python
from pbjrag import DSCCodeChunker

chunker = DSCCodeChunker()
chunks = chunker.chunk_code(source_code, filepath="example.py")

for chunk in chunks:
    print(f"Type: {chunk.chunk_type}")
    print(f"Blessing: {chunk.blessing.tier}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
```

### Search (with Qdrant)

```python
from pbjrag import DSCAnalyzer

analyzer = DSCAnalyzer(config={
    "enable_vector_store": True,
    "qdrant_host": "localhost",
    "qdrant_port": 6333
})

# Index first
analyzer.analyze_project("./my_project")

# Then search
results = analyzer.search("authentication handler", top_k=5)
```

### WebUI

```bash
streamlit run webui/app.py
# http://localhost:8501
```

### CLI

```bash
pbjrag analyze ./my_project
pbjrag report --format json
```

## Configuration

### Default Stack

```yaml
# ~/.pbjrag/config.yaml
vector_store:
  backend: qdrant
  host: localhost
  port: 6333
  collection: crown_jewel_dsc

embedding:
  backend: ollama
  model: snowflake-arctic-embed2
  host: localhost
  port: 11434
  dimensions: 1024
```

### Python Config

```python
analyzer = DSCAnalyzer(config={
    "field_dim": 8,
    "enable_vector_store": True,
    "qdrant_host": "localhost",
    "qdrant_port": 6333,
})
```

## API Reference

### DSCAnalyzer

```python
analyzer = DSCAnalyzer(config=None)

analyzer.analyze_file(file_path: str) -> Dict
analyzer.analyze_project(project_path: str, max_depth=2) -> Dict
analyzer.search(query: str, **kwargs) -> List[Dict]
analyzer.find_resonance(chunk_id: int, min_resonance=0.7) -> List[Dict]
analyzer.evolve_by_phase(target_phase: str) -> List[Dict]
analyzer.generate_report() -> Dict
```

### DSCCodeChunker

```python
chunker = DSCCodeChunker()

chunker.chunk_code(code: str, filepath: str = "") -> List[DSCChunk]
chunker.calculate_chunk_resonance(chunk1, chunk2) -> float
```

### DSCChunk

```python
chunk.content          # Source code
chunk.chunk_type       # "function", "class", "method", etc.
chunk.start_line       # Start line number
chunk.end_line         # End line number
chunk.blessing.tier    # "Φ+", "Φ~", or "Φ-"
chunk.blessing.phase   # "witness", "reflection", etc.
chunk.blessing.epc     # 0.0 to 1.0
chunk.provides         # Symbols this chunk defines
chunk.depends_on       # Dependencies
chunk.file_path        # Source file path
chunk.field_state      # 9-dimensional FieldState
```

### Pattern Analysis (Advanced)

```python
from pbjrag.crown_jewel.pattern_analyzer import PatternAnalyzer, analyze_codebase

patterns = analyze_codebase("./my_project")

# Or directly
pa = PatternAnalyzer()
result = pa.analyze_code(source_code)
```

## Architecture

```
src/pbjrag/
├── dsc/                    # Differential Symbolic Calculus
│   ├── analyzer.py         # DSCAnalyzer
│   ├── chunker.py          # DSCCodeChunker, FieldState, BlessingState
│   ├── vector_store.py     # Qdrant integration
│   ├── embedding_adapter.py # Ollama/OpenAI
│   ├── neo4j_store.py      # Optional graph store
│   └── legacy/             # Archived (ChromaDB)
├── crown_jewel/            # Core orchestration
│   ├── metrics.py          # EPC calculations
│   ├── phase_manager.py    # 7-phase lifecycle
│   ├── pattern_analyzer.py # Fractal pattern detection
│   ├── field_container.py  # Field state management
│   └── orchestrator.py     # Workflow coordination
├── cli.py
└── config.py
```

## Development

```bash
pip install -e ".[dev]"

# Tests (80% coverage required)
pytest tests/ --cov=src/pbjrag --cov-fail-under=80

# Format
black src/pbjrag

# Type check
mypy src/pbjrag
```

## Why Bother?

Because snapshot safety doesn't scale with power.

A codebase that passes every lint check can still be drifting toward unmaintainability. Individual outputs can be "fine" while the trajectory screams trouble.

PBJRAG is one piece of a larger question: how do you hold systems that behave over time? How do you see "trajectory toward harm" before it hits the wall?

This isn't about replacing human judgment. It's about giving humans something better than still photos when they're watching video.

## Navi Ecosystem

PBJRAG is the mathematical core of Project Navi:

- **[navi-fcpa](https://github.com/Project-Navi/navi-fcpa)** — Forensic code auditing using PBJRAG's 9D analysis
- **[navi-lazytest](https://github.com/Project-Navi/navi-lazytest)** — Self-improving test framework with adaptive learning
- **[navi-deus-ex](https://github.com/Project-Navi/navi-deus-ex)** — Triple store infrastructure for semantic knowledge graphs

## License

**Dual Licensed:**

- **AGPL-3.0-or-later** — Free for open source ([full text](https://www.gnu.org/licenses/agpl-3.0.html))
- **Commercial (PNEUL-D v2.2)** — For proprietary use, contact [legal@projectnavi.ai](mailto:legal@projectnavi.ai)

See [LICENSE](LICENSE) and [docs/legal/](docs/legal/) for complete terms.

### Ethical Support Program

Open source projects may qualify for enhanced support by aligning with Project Navi's ethical principles. No additional license obligations—separate service relationship. Details: [ETHICAL_SUPPORT_FRAMEWORK.md](docs/legal/ETHICAL_SUPPORT_FRAMEWORK.md).

---

**Project Navi** — Advanced Code Intelligence

*v3.0.0 — Qdrant Native*

*Built by someone who treats AI like whip-smart senior engineers and got tired of pretending single outputs tell the whole story.*
