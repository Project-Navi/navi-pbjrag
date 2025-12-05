# PBJRAG: Track Code Quality Trajectory, Not Just Snapshots

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: Commercial](https://img.shields.io/badge/License-Commercial-green.svg)](docs/legal/PNEUL-D_v2.2.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Coverage: 80%](https://img.shields.io/badge/coverage-80%25-brightgreen.svg)](https://github.com/Project-Navi/navi-pbjrag/actions)

**What it does**: Detects whether your codebase is improving or quietly rotting—even when tests pass and linters approve.

Traditional analysis checks discrete snapshots: "Is this function too long?" "Did tests pass?" PBJRAG tracks **trajectory**: "Is this system drifting toward coherence or decay?"

---

## Quick Start

### Prerequisites (5 minutes first time)

```bash
# 1. Install PBJRAG
pip install navi-pbjrag[qdrant]

# 2. Start Qdrant (vector store)
docker run -d -p 6333:6333 qdrant/qdrant

# 3. Install embeddings (optional - uses defaults otherwise)
ollama pull snowflake-arctic-embed2
```

### Analyze Code

```python
from pbjrag import DSCAnalyzer

analyzer = DSCAnalyzer()
results = analyzer.analyze_file("my_code.py")

for chunk in results.get("chunks", []):
    print(f"Function: {chunk.get('name', 'unknown')}")
    print(f"  Quality: {chunk['blessing']['tier']}")     # Φ+, Φ~, or Φ-
    print(f"  Phase:   {chunk['blessing']['phase']}")    # compost → emergent
    print(f"  EPC:     {chunk['blessing']['epc']:.3f}")  # 0.0–1.0
```

### Example Output

```
Function: validate_token
  Quality: Φ+        ← High quality, minimal intervention needed
  Phase:   stillness ← Mature, stable code
  EPC:     0.847     ← Strong emergence potential

Function: legacy_auth_check
  Quality: Φ-        ← Below threshold, needs refactoring
  Phase:   grinding  ← Over-optimized, consider redesign
  EPC:     0.312     ← Low emergence potential
```

### WebUI & CLI

```bash
# Visual interface
pip install streamlit  # if not installed
streamlit run webui/app.py  # → http://localhost:8501

# Command line
pbjrag analyze ./my_project
pbjrag report --format json
```

---

## What the Tiers Mean

| Tier | Name | EPC Range | What To Do |
|------|------|-----------|------------|
| **Φ+** | Blessed | ≥0.6 | Ship it. Monitor occasionally. |
| **Φ~** | Mundane | 0.45–0.6 | Works but watch for drift. Review quarterly. |
| **Φ-** | Decay | <0.45 | Technical debt. Schedule refactoring. |

**Why Φ (phi)?** The Golden Ratio is relevant to coherence metrics. Also, we're pretentious.

---

## What Makes This Different

| Tool | Checks | Tracks Trajectory? | Explains Why? |
|------|--------|-------------------|---------------|
| pylint/ruff | Style rules | ❌ | ❌ (just counts) |
| SonarQube | Metrics | ⚠️ (history view) | ⚠️ (limited) |
| **PBJRAG** | 9D field state | ✅ | ✅ (dimension breakdown) |

**The core insight**: A codebase can pass every lint check while quietly rotting. Individual "good" outputs don't reveal trajectory toward unmaintainability.

PBJRAG uses **Differential Symbolic Calculus (DSC)** to represent code as a 9-dimensional field evolving through configuration space—enabling trajectory-based assessment rather than point-in-time validation.

---

## Core Concepts

### The Problem: Snapshot Blindness

Conventional code analysis operates like frame-by-frame video inspection: "Does this function have too many lines?" "Is this variable named correctly?" "Did the tests pass?"

These are **snapshot analyses**. They tell you nothing about *trajectory*—whether your codebase is drifting toward coherence or quietly rotting from the inside.

### The Solution: Field-Theoretic Code Representation

**PBJRAG** treats code as a multi-dimensional field that evolves through configuration space. Instead of asking "is this output okay right now?" it asks: "what direction is this system moving in?"

Each code chunk is characterized by:
- **Blessing tier** (Φ+, Φ~, Φ-) — quality classification across 9 dimensions
- **Phase** (compost → emergent) — lifecycle stage in 7-phase evolution
- **EPC score** — emergence potential coefficient via geometric mean

Think of them as behavioral vital signs. You don't take them once; you track them across commits, sessions, refactors.

### 7-Phase Lifecycle

```
Compost → Reflection → Becoming → Stillness → Turning → Emergent → Grinding
```

| Phase | What It Means | Recommended Action |
|-------|---------------|-------------------|
| **Compost** | New/raw code | Let it breathe. Don't refactor yet. |
| **Stillness** | Mature, stable | Minimal intervention. Monitor. |
| **Grinding** | Over-optimized | Stop adding features. Consider archive. |

The phase tells you what kind of intervention makes sense. You don't refactor code in Compost—you let it breathe. You don't add features to code in Grinding—you're past that.

---

## Mathematical Framework

**Skip this if**: You just want to use the tool. The API abstracts this completely.

**Read this if**: You want to understand the theory, modify the math, or cite the work.

### 9-Dimensional Semantic Field

Code is represented as a point in a 9-dimensional configuration space:

| Dimension | Symbol | Interpretation |
|-----------|--------|----------------|
| **Semantic** | Σ | Conceptual clarity and meaning coherence |
| **Emotional** | Ε | Developer intent and communication quality |
| **Ethical** | Θ | Best practices, maintainability |
| **Temporal** | Τ | Evolution stability and change patterns |
| **Entropic** | Ξ | Information density and structural predictability |
| **Rhythmic** | Ρ | Consistency and pattern coherence |
| **Contradiction** | Ω | Internal tensions and design paradoxes |
| **Relational** | Γ | Dependency structure and coupling |
| **Emergent** | Μ | Innovation potential and novel patterns |

Each dimension is normalized to [0, 1]. Together they form a **field state**—a fingerprint of how this code is *behaving*, not just what it *contains*.

### Emergence Potential Coefficient (EPC)

The EPC combines three key factors via geometric mean of sigmoid-transformed values:

```
EPC = ∛(σ(ethics) × σ(presence) × σ(1-contradiction))
```

where σ(x) = 1/(1 + exp(-10(x - 0.5)))

**Why geometric mean?** Ensures weakness in ANY dimension significantly impacts the score. No compensation effects—you can't offset bad practices with good naming.

**Full mathematical details**: [docs/mathematics/](docs/mathematics/)

---

## API Reference

### DSCAnalyzer

Primary interface for code analysis:

```python
analyzer = DSCAnalyzer(config=None)

# Single file analysis
analyzer.analyze_file(file_path: str) -> Dict

# Project-wide analysis
analyzer.analyze_project(project_path: str, max_depth=2) -> Dict

# Semantic search (requires vector store)
analyzer.search(query: str, **kwargs) -> List[Dict]

# Find resonant chunks (similar patterns)
analyzer.find_resonance(chunk_id: int, min_resonance=0.7) -> List[Dict]

# Query by lifecycle phase
analyzer.evolve_by_phase(target_phase: str) -> List[Dict]

# Generate comprehensive report
analyzer.generate_report() -> Dict
```

### DSCCodeChunker

Granular code chunking with blessing calculation:

```python
chunker = DSCCodeChunker()

# Chunk source code
chunker.chunk_code(code: str, filepath: str = "") -> List[DSCChunk]

# Calculate resonance between chunks
chunker.calculate_chunk_resonance(chunk1, chunk2) -> float
```

### DSCChunk

Data structure representing analyzed code:

```python
chunk.content          # Source code string
chunk.chunk_type       # "function", "class", "method", etc.
chunk.start_line       # Starting line number
chunk.end_line         # Ending line number
chunk.blessing.tier    # "Φ+", "Φ~", or "Φ-"
chunk.blessing.phase   # "compost", "reflection", ..., "grinding"
chunk.blessing.epc     # Emergence Potential Coefficient [0.0, 1.0]
chunk.provides         # Symbols this chunk defines
chunk.depends_on       # External dependencies
chunk.file_path        # Source file path
chunk.field_state      # 9-dimensional FieldState object
```

---

## Configuration

### Default Stack (YAML)

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

### Python Configuration

```python
analyzer = DSCAnalyzer(config={
    "field_dim": 8,
    "enable_vector_store": True,
    "qdrant_host": "localhost",
    "qdrant_port": 6333,
    "quantization_precision": 4,
    "pareto_alpha": 2.0,
    "stability_threshold": 0.5
})
```

---

## Architecture

```
src/pbjrag/
├── dsc/                    # Differential Symbolic Calculus
│   ├── analyzer.py         # DSCAnalyzer - primary interface
│   ├── chunker.py          # DSCCodeChunker, FieldState, BlessingState
│   ├── vector_store.py     # Qdrant integration
│   ├── embedding_adapter.py # Ollama/OpenAI embedding backends
│   ├── neo4j_store.py      # Optional graph store for relational queries
│   └── legacy/             # Archived ChromaDB implementation
├── crown_jewel/            # Core Mathematical Infrastructure
│   ├── metrics.py          # EPC calculations, blessing classification
│   ├── phase_manager.py    # 7-phase lifecycle management
│   ├── pattern_analyzer.py # Fractal pattern detection
│   ├── field_container.py  # Field state container and operations
│   └── orchestrator.py     # Workflow coordination
├── cli.py                  # Command-line interface
└── config.py               # Configuration management
```

**v3.0.0 is Qdrant-native.** Qdrant's the only vector store we actively maintain. If you need ChromaDB or something else, there's a template in `docs/adapters/`—but you're on your own.

---

## Development

### Setup

```bash
pip install -e ".[dev]"

# Run tests with coverage requirement
pytest tests/ --cov=src/pbjrag --cov-fail-under=80

# Format code
black src/pbjrag

# Type checking
mypy src/pbjrag
```

### Testing Requirements

- Minimum 80% code coverage (enforced by CI)
- All tests must pass before merging
- Type hints required for public APIs

---

## Theoretical Justification

### Why Bother?

Because snapshot safety doesn't scale with power.

A codebase that passes every lint check can still be drifting toward unmaintainability. Individual outputs can be "fine" while the trajectory screams trouble.

PBJRAG addresses a fundamental question in software quality assurance: **How do you detect trajectory toward harm before it manifests as discrete failures?**

Traditional static analysis tools operate in the **syntactic regime**: they check adherence to rules at discrete points in time. This is analogous to inspecting individual frames of a video—you might detect local defects, but you miss **temporal patterns** and **directional drift**.

PBJRAG operates in the **semantic-temporal regime**: it constructs a field representation that captures both current state and evolutionary trajectory. This enables:

1. **Trajectory-based assessment**: Detect quality drift before discrete failures
2. **Phase-aware intervention**: Match maintenance strategies to lifecycle stage
3. **Resonance detection**: Identify structurally similar patterns across codebase
4. **Field coherence metrics**: Evaluate group-level quality beyond individual components

This isn't about replacing human judgment. It's about giving humans something better than still photos when they're watching video.

---

## Navi Ecosystem

PBJRAG is the mathematical core of Project Navi's code intelligence suite:

- **[navi-fcpa](https://github.com/Project-Navi/navi-fcpa)** — Forensic code auditing using PBJRAG's 9D analysis with git history integration
- **[navi-lazytest](https://github.com/Project-Navi/navi-lazytest)** — Self-improving test framework with adaptive learning from field metrics
- **[navi-deus-ex](https://github.com/Project-Navi/navi-deus-ex)** — Triple store infrastructure for semantic knowledge graphs and ontological reasoning

---

## Citation

If you use PBJRAG in academic research, please cite:

```bibtex
@software{pbjrag2024,
  title = {PBJRAG: Semantic Code Analysis via 9-Dimensional Field Theory},
  author = {{Project Navi Contributors}},
  year = {2024},
  version = {3.0.0},
  url = {https://github.com/Project-Navi/navi-pbjrag},
  note = {Dual licensed: AGPL-3.0-or-later and Commercial (PNEUL-D v2.2)}
}
```

### Related Publications

*Academic paper in preparation.*

For early access to draft manuscripts or collaboration inquiries, contact: [research@projectnavi.ai](mailto:research@projectnavi.ai)

---

## License

**Dual Licensed:**

- **AGPL-3.0-or-later** — Free for open source ([full text](https://www.gnu.org/licenses/agpl-3.0.html))
- **Commercial (PNEUL-D v2.2)** — For proprietary use, contact [legal@projectnavi.ai](mailto:legal@projectnavi.ai)

See [LICENSE](LICENSE) and [docs/legal/](docs/legal/) for complete terms.

### Ethical Support Program

Open source projects may qualify for enhanced support by aligning with Project Navi's ethical principles. No additional license obligations—separate service relationship.

Details: [ETHICAL_SUPPORT_FRAMEWORK.md](docs/legal/ETHICAL_SUPPORT_FRAMEWORK.md)

---

**Project Navi** — Advanced Code Intelligence
*v3.0.0 — Qdrant Native*

*Built by someone who treats AI like whip-smart senior engineers and got tired of pretending single outputs tell the whole story.*
