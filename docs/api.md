# PBJRAG API Documentation

## Core Classes

### DSCAnalyzer

High-level interface for analyzing code with 9-dimensional DSC analysis.

```python
from pbjrag import DSCAnalyzer

analyzer = DSCAnalyzer(config={
    "field_dim": 8,
    "enable_vector_store": True,
    "output_dir": "dsc_analysis"
})
```

**Configuration Options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `field_dim` | int | 8 | Dimensionality of the symbolic field |
| `enable_vector_store` | bool | True | Enable Qdrant vector storage |
| `qdrant_host` | str | "localhost" | Qdrant server host |
| `qdrant_port` | int | 6333 | Qdrant server port |
| `output_dir` | str | "dsc_analysis" | Output directory for results |
| `fractal_detection` | bool | True | Enable pattern analysis |

**Methods:**

#### `analyze_file(file_path: str) -> List[DSCChunk]`

Analyze a single file and return DSC chunks with blessing scores.

```python
chunks = analyzer.analyze_file("my_code.py")

for chunk in chunks:
    print(f"Content: {chunk.content[:50]}...")
    print(f"Blessing: {chunk.blessing.tier}")
    print(f"Phase: {chunk.blessing.phase}")
    print(f"EPC: {chunk.blessing.epc:.3f}")
```

**Returns:** List of `DSCChunk` objects with blessing metadata.

#### `analyze_project(project_path: str) -> Dict[str, Any]`

Analyze entire project directory and generate comprehensive report.

```python
report = analyzer.analyze_project("./my_project")

print(f"Total files: {report['total_files']}")
print(f"Average blessing: {report['avg_blessing']:.3f}")
print(f"Φ+ chunks: {report['phi_plus_count']}")
```

**Returns:** Dictionary with aggregate statistics and per-file results.

#### `search(query: str, top_k: int = 5) -> List[Dict]`

Semantic search across analyzed code (requires vector store).

```python
results = analyzer.search("authentication logic", top_k=5)

for result in results:
    print(f"File: {result['file_path']}")
    print(f"Score: {result['score']:.3f}")
    print(f"Blessing: {result['blessing']}")
```

**Parameters:**
- `query`: Search query string
- `top_k`: Number of results to return

**Returns:** List of matching chunks with metadata.

---

### DSCCodeChunker

Low-level chunking engine for semantic code splitting.

```python
from pbjrag import DSCCodeChunker

chunker = DSCCodeChunker(field_dim=8)
chunks = chunker.chunk_code(source_code, file_path="example.py")
```

**Methods:**

#### `chunk_code(code: str, file_path: str = "") -> List[DSCChunk]`

Split code into semantically meaningful chunks with DSC analysis.

```python
chunks = chunker.chunk_code(code, file_path="app.py")
```

**Returns:** List of `DSCChunk` objects.

---

### DSCChunk

Data class representing a single analyzed code chunk.

**Attributes:**

```python
@dataclass
class DSCChunk:
    content: str              # The actual code content
    start_line: int          # Starting line number
    end_line: int            # Ending line number
    chunk_type: str          # Type: function, class, module, etc.
    blessing: BlessingVector # Blessing metadata
    metadata: Dict[str, Any] # Additional metadata
```

**Blessing Vector:**

```python
chunk.blessing.tier        # "Φ+", "Φ~", or "Φ-"
chunk.blessing.phase       # Current lifecycle phase
chunk.blessing.epc         # Emergence Potential Coefficient (0-1)
chunk.blessing.dimensions  # Dict of 9 dimension scores
```

---

### PhaseManager

Manages 7-phase lifecycle detection and transitions.

```python
from pbjrag import PhaseManager

pm = PhaseManager()
phase = pm.detect_phase(presence=0.75, entropy=0.3)
print(phase)  # "Stillness"
```

**The 7 Phases:**

| Phase | Range | Description |
|-------|-------|-------------|
| Compost | 0.0-0.2 | Raw, unprocessed code |
| Reflection | 0.2-0.35 | Analysis phase |
| Becoming | 0.35-0.5 | Active development |
| Stillness | 0.5-0.65 | Stable, mature code |
| Turning | 0.65-0.8 | Refactoring phase |
| Emergent | 0.8-0.9 | Novel patterns forming |
| Grinding | 0.9-1.0 | Optimization phase |

**Methods:**

#### `detect_phase(presence: float, entropy: float) -> str`

Determine lifecycle phase from metrics.

---

### CoreMetrics

Calculate blessing tiers and field metrics.

```python
from pbjrag.crown_jewel import CoreMetrics

metrics = CoreMetrics()
blessing_vector = metrics.create_blessing_vector(
    ethics=0.85,
    presence=0.78,
    contradiction=0.22
)
```

**Methods:**

#### `create_blessing_vector(ethics: float, presence: float, contradiction: float) -> Dict`

Generate blessing vector with tier assignment.

```python
vector = metrics.create_blessing_vector(
    ethics=0.85,      # Ethical alignment (0-1)
    presence=0.78,    # Presence density (0-1)
    contradiction=0.22 # Contradiction pressure (0-1)
)

print(vector["tier"])  # "Φ+"
print(vector["epc"])   # 0.783
```

**Blessing Tier Thresholds:**

```python
Φ+ (Excellent):
    EPC ≥ 0.6 AND ethics ≥ 0.6 AND contradiction ≤ 0.45 AND presence ≥ 0.5

Φ~ (Good):
    EPC ≥ 0.45 AND ethics ≥ 0.45 AND contradiction ≤ 0.6

Φ- (Needs Attention):
    Otherwise
```

---

### PatternAnalyzer

Detect fractal patterns across codebases.

```python
from pbjrag.crown_jewel import PatternAnalyzer

analyzer = PatternAnalyzer()
patterns = analyzer.analyze_patterns(chunks)
```

**Methods:**

#### `analyze_patterns(chunks: List[DSCChunk]) -> List[Dict]`

Find recurring patterns in code chunks.

```python
patterns = analyzer.analyze_patterns(chunks)

for pattern in patterns:
    print(f"Type: {pattern['pattern_type']}")
    print(f"Frequency: {pattern['frequency']}")
    print(f"Avg Blessing: {pattern['avg_blessing']:.3f}")
```

---

## CLI Usage

### Basic Commands

```bash
# Analyze single file
pbjrag analyze file.py

# Analyze project directory
pbjrag analyze ./my_project --output report.json

# Search indexed code
pbjrag search "error handling" --top-k 10

# Show version
pbjrag --version
```

### Advanced Options

```bash
# With custom config
pbjrag analyze ./project --config custom.json

# Enable vector store
pbjrag analyze ./project --vector-store --qdrant-host localhost

# Pattern detection only
pbjrag patterns ./project --output patterns.json
```

---

## Vector Store Integration

### Qdrant Setup

```python
from pbjrag import DSCAnalyzer

analyzer = DSCAnalyzer(config={
    "enable_vector_store": True,
    "qdrant_host": "localhost",
    "qdrant_port": 6333,
    "collection_name": "my_codebase"
})

# Analyze and auto-index
analyzer.analyze_project("./my_project")

# Search
results = analyzer.search("authentication logic")
```

### ChromaDB Setup

```python
from pbjrag.dsc import ChromaStore

chroma = ChromaStore(persist_directory="./chroma_db")
chroma.add_chunks(chunks)
results = chroma.search("error handling", top_k=5)
```

### Neo4j Graph Store

```python
from pbjrag.dsc import Neo4jStore

neo4j = Neo4jStore(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

neo4j.add_chunks_with_relationships(chunks)
related = neo4j.find_related_chunks(chunk_id)
```

---

## Exception Handling

```python
from pbjrag import DSCAnalyzer
from pbjrag.crown_jewel.error_handler import DSCError

try:
    analyzer = DSCAnalyzer()
    chunks = analyzer.analyze_file("file.py")
except DSCError as e:
    print(f"Analysis error: {e}")
except FileNotFoundError:
    print("File not found")
```

---

## Type Hints

PBJRAG is fully typed for IDE support:

```python
from typing import List, Dict, Any
from pbjrag import DSCAnalyzer, DSCChunk

def analyze_codebase(path: str) -> Dict[str, Any]:
    analyzer: DSCAnalyzer = DSCAnalyzer()
    chunks: List[DSCChunk] = analyzer.analyze_file(path)
    return {"chunks": len(chunks)}
```

---

## Examples

### Full Analysis Pipeline

```python
from pbjrag import DSCAnalyzer
from pbjrag.crown_jewel import PatternAnalyzer

# Initialize
analyzer = DSCAnalyzer(config={
    "enable_vector_store": True,
    "fractal_detection": True
})

# Analyze project
report = analyzer.analyze_project("./my_app")

# Extract high-quality code
phi_plus_chunks = [
    chunk for chunk in report["all_chunks"]
    if chunk.blessing.tier == "Φ+"
]

# Find patterns
pattern_analyzer = PatternAnalyzer()
patterns = pattern_analyzer.analyze_patterns(phi_plus_chunks)

# Generate summary
print(f"Total chunks: {len(report['all_chunks'])}")
print(f"Φ+ chunks: {len(phi_plus_chunks)}")
print(f"Patterns found: {len(patterns)}")
```

### Custom Blessing Calculation

```python
from pbjrag.crown_jewel import CoreMetrics

metrics = CoreMetrics(config={
    "pareto_alpha": 2.5,
    "stability_threshold": 0.6
})

blessing = metrics.create_blessing_vector(
    ethics=0.9,
    presence=0.85,
    contradiction=0.1
)

print(f"Tier: {blessing['tier']}")
print(f"EPC: {blessing['epc']:.3f}")
```
