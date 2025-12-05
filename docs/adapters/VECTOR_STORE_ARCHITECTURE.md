# Vector Store Architecture

## Overview

PBJRAG v3 uses a **Qdrant-native architecture** for vector storage and semantic search. This document explains the design decisions and architecture.

## Default Configuration

```yaml
vector_store:
  backend: qdrant
  host: localhost
  port: 6333
  collection: crown_jewel_dsc

embedding:
  backend: ollama
  model: snowflake-arctic-embed2
  host: 0.0.0.0
  port: 11434
  dimensions: 1024
```

## Why Qdrant?

### 1. Multi-Vector Support

DSC (Differential Symbolic Calculus) chunks have **9-dimensional field states**:

```
FieldState:
├── semantic     [8 dims] → pattern complexity
├── emotional    [8 dims] → affective context
├── ethical      [8 dims] → alignment signals
├── temporal     [8 dims] → time stability
├── entropic     [8 dims] → chaos/order balance
├── rhythmic     [8 dims] → structural patterns
├── contradiction [8 dims] → tension points
├── relational   [8 dims] → dependency graph
└── emergent     [8 dims] → evolution potential
```

Qdrant's **named vectors** allow separate indexing and searching across these dimensions:

```python
# Qdrant collection setup
client.create_collection(
    collection_name="crown_jewel_dsc",
    vectors_config={
        "content": models.VectorParams(size=1024, distance=models.Distance.COSINE),
        "semantic": models.VectorParams(size=1024, distance=models.Distance.COSINE),
        "ethical": models.VectorParams(size=1024, distance=models.Distance.COSINE),
        "relational": models.VectorParams(size=1024, distance=models.Distance.COSINE),
        "phase": models.VectorParams(size=1024, distance=models.Distance.COSINE),
    }
)
```

### 2. Advanced Filtering

Crown Jewel's blessing system requires complex metadata filtering:

```python
# Search for high-quality code ready for emergence
results = store.search(
    query="authentication handler",
    blessing_filter="Φ+",           # Only blessed code
    phase_filter=["turning"],        # Ready to evolve
    purpose="emergence",             # Emergence-optimized ranking
    top_k=10
)
```

### 3. Hybrid Search

Combine dense vectors with sparse keyword matching:

```python
# Qdrant hybrid search
results = client.search(
    collection_name="crown_jewel_dsc",
    query_vector=("content", content_embedding),
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="blessing_tier",
                match=models.MatchValue(value="Φ+")
            )
        ]
    ),
    with_payload=True,
    limit=10
)
```

## Data Flow

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Source Code    │────▶│  DSC Chunker │────▶│  Embeddings │
└─────────────────┘     └──────────────┘     └──────┬──────┘
                                                    │
                        ┌──────────────────────────▼──────────────────────────┐
                        │                      Qdrant                          │
                        │  ┌────────────────────────────────────────────────┐  │
                        │  │  Collection: crown_jewel_dsc                   │  │
                        │  │                                                │  │
                        │  │  Named Vectors:                                │  │
                        │  │  ├── content   [1024]                          │  │
                        │  │  ├── semantic  [1024]                          │  │
                        │  │  ├── ethical   [1024]                          │  │
                        │  │  ├── relational [1024]                         │  │
                        │  │  └── phase     [1024]                          │  │
                        │  │                                                │  │
                        │  │  Payload (metadata):                           │  │
                        │  │  ├── blessing_tier: "Φ+"                       │  │
                        │  │  ├── blessing_phase: "witness"                 │  │
                        │  │  ├── blessing_epc: 0.85                        │  │
                        │  │  ├── chunk_type: "function"                    │  │
                        │  │  └── file_path: "/src/auth.py"                 │  │
                        │  └────────────────────────────────────────────────┘  │
                        └──────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                        ┌──────────────────────────────────────────────────────┐
                        │                 Crown Jewel Core                      │
                        │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
                        │  │FieldContainer│  │PhaseManager  │  │  Metrics   │  │
                        │  └──────────────┘  └──────────────┘  └────────────┘  │
                        └──────────────────────────────────────────────────────┘
```

## Embedding Pipeline

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Content   │────▶│  Ollama Server   │────▶│  1024-dim vec   │
└─────────────┘     │  (Arctic Embed2) │     └─────────────────┘
                    └──────────────────┘
```

**Ollama Configuration:**
- Model: `snowflake-arctic-embed2:latest`
- Host: `0.0.0.0:11434`
- Dimensions: 1024
- Advantages: Local inference, no API costs, fast batch processing

## Legacy Adapters

The following adapters are **archived** and no longer maintained:

| Adapter | Location | Status |
|---------|----------|--------|
| ChromaDB | `src/pbjrag/dsc/legacy/chroma_store.py` | Archived |

These are preserved for reference only. See `docs/adapters/CUSTOM_ADAPTER_TEMPLATE.md` if you need to implement your own adapter.

## Production Deployment

### Qdrant Docker (Recommended)

```bash
# Quick start
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# With persistence
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### Ollama Setup

```bash
# Install ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull embedding model
ollama pull snowflake-arctic-embed2

# Verify
curl http://localhost:11434/api/embeddings \
    -d '{"model": "snowflake-arctic-embed2", "prompt": "test"}'
```

## Performance Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| Single embedding | ~15ms | Ollama local |
| Batch embed (100) | ~800ms | Ollama batch |
| Vector search | ~5ms | Qdrant HNSW |
| Hybrid search | ~12ms | With filters |
| Index 1000 chunks | ~3s | Full pipeline |

## Security Considerations

1. **Qdrant API Key** - Enable authentication in production
2. **Ollama Network** - Bind to localhost unless needed externally
3. **Collection Access** - Use Qdrant's access control for multi-tenant setups

---

*PBJRAG v3 - Qdrant Native Architecture*
