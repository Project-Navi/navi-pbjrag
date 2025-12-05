# PBJRAG Configuration Guide

This guide explains how to configure PBJRAG v3 for different environments and use cases.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)
- [Configuration Options](#configuration-options)
- [Common Setups](#common-setups)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Minimal Setup (No Dependencies)

```bash
# Run with default settings, vector store disabled
pbjrag analyze ./myproject --no-vector
```

### Full Setup (With Vector Store)

```bash
# 1. Start Qdrant (Docker)
docker run -p 6333:6333 qdrant/qdrant

# 2. Start Infinity embedding service
docker run -p 7997:7997 michaelf34/infinity:latest

# 3. Run analysis
pbjrag analyze ./myproject
```

## Configuration Files

PBJRAG looks for configuration in the following order (later overrides earlier):

1. **Default config**: `config/default.yaml` (built-in defaults)
2. **Custom config file**: Specified via `--config` flag or `PBJRAG_CONFIG` env var
3. **Environment variables**: Override specific settings (see below)
4. **CLI arguments**: Override configuration on the command line

### Using a Custom Config File

```bash
# Via CLI flag
pbjrag analyze ./project --config my-config.yaml

# Via environment variable
export PBJRAG_CONFIG=/path/to/my-config.yaml
pbjrag analyze ./project
```

### Custom Config Example

Create `my-config.yaml`:

```yaml
core:
  field_dim: 16  # Higher granularity
  purpose: "stability"
  output_dir: "custom_output"

vector_store:
  qdrant:
    host: "qdrant.example.com"
    port: 6333

analysis:
  enable_pattern_detection: true
  complexity_threshold: 15
```

## Environment Variables

All configuration options can be overridden with environment variables. The naming convention is:

**Format**: `PBJRAG_<SECTION>_<OPTION>` (uppercase, underscore-separated)

### Core Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `PBJRAG_CORE_FIELD_DIM` | Field dimension for DSC analysis | `8` |
| `PBJRAG_CORE_PURPOSE` | Analysis purpose (stability/emergence/coherence/innovation) | `coherence` |
| `PBJRAG_CORE_OUTPUT_DIR` | Output directory for results | `pbjrag_output` |
| `PBJRAG_CORE_LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `PBJRAG_CORE_ENABLE_VECTOR_STORE` | Enable vector store | `true` |

### Vector Store (Qdrant)

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_HOST` | Qdrant server hostname | `localhost` |
| `QDRANT_PORT` | Qdrant server port | `6333` |
| `PBJRAG_VECTOR_STORE_COLLECTION_NAME` | Collection name | `crown_jewel_dsc` |
| `INFINITY_URL` | Infinity embedding service URL | `http://127.0.0.1:7997` |

### Neo4j Graph Store

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | **Neo4j password (REQUIRED if using Neo4j)** | *(none)* |

### ChromaDB (Alternative Vector Store)

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROMA_DB_PATH` | ChromaDB persistence directory | `/app/chroma_db` |
| `PBJRAG_CORE_ENABLE_CHROMA` | Enable ChromaDB instead of Qdrant | `false` |

### Example: Environment Variables

```bash
# Development setup
export PBJRAG_CORE_LOG_LEVEL=DEBUG
export PBJRAG_CORE_OUTPUT_DIR=/tmp/pbjrag_dev
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# Production setup
export PBJRAG_CORE_LOG_LEVEL=INFO
export PBJRAG_CORE_PURPOSE=stability
export QDRANT_HOST=qdrant.prod.example.com
export QDRANT_PORT=6333
export NEO4J_URI=bolt://neo4j.prod.example.com:7687
export NEO4J_PASSWORD=secure_password_here
```

## Configuration Options

### Core Settings

- **field_dim**: Dimension of the field analysis (8, 16, 32). Higher = more granular but slower.
- **purpose**: Analysis focus (`stability`, `emergence`, `coherence`, `innovation`)
- **output_dir**: Where to save analysis results
- **enable_vector_store**: Enable semantic search via vector embeddings

### Vector Store Options

- **qdrant.host/port**: Qdrant server connection
- **collection_name**: Name of the vector collection
- **infinity_url**: Embedding service endpoint
- **embedding_model**: Model for generating embeddings

### Analysis Options

- **coherence_method**: How to calculate field coherence
- **blessing_tiers**: Thresholds for categorizing code quality
- **pattern_confidence_threshold**: Minimum confidence for pattern detection
- **complexity_threshold**: Max cyclomatic complexity before warnings

### Performance Options

- **worker_threads**: Parallel processing threads (0 = auto)
- **max_parallel_files**: Maximum files to process simultaneously
- **memory_optimization**: Trade speed for lower memory usage

## Common Setups

### 1. Development (Local, Minimal Dependencies)

```yaml
# dev-config.yaml
core:
  field_dim: 8
  output_dir: "./dev_output"
  enable_vector_store: false
  log_level: "DEBUG"

analysis:
  enable_pattern_detection: true
  complexity_threshold: 10
```

```bash
pbjrag analyze ./myproject --config dev-config.yaml
# OR
pbjrag analyze ./myproject --no-vector
```

### 2. CI/CD Pipeline

```yaml
# ci-config.yaml
core:
  field_dim: 8
  output_dir: "./ci_reports"
  enable_vector_store: false
  log_level: "WARNING"

analysis:
  complexity_threshold: 15
  blessing_tiers:
    positive: 0.75  # Stricter standards

report:
  format: "json"
  include_snippets: false
```

```bash
# In CI pipeline
export PBJRAG_CONFIG=ci-config.yaml
pbjrag analyze ./src --no-vector
```

### 3. Production (Full Features)

```yaml
# prod-config.yaml
core:
  field_dim: 16
  purpose: "stability"
  output_dir: "/var/pbjrag/reports"
  enable_vector_store: true
  enable_neo4j: true

vector_store:
  qdrant:
    host: "qdrant.prod.internal"
    port: 6333
  infinity_url: "http://infinity.prod.internal:7997"

neo4j:
  uri: "bolt://neo4j.prod.internal:7687"
  # Password via NEO4J_PASSWORD env var

analysis:
  enable_pattern_detection: true
  enable_complexity_analysis: true
  enable_dependency_analysis: true

performance:
  worker_threads: 8
  max_parallel_files: 10
```

```bash
# Set secrets via environment
export NEO4J_PASSWORD=secure_prod_password

# Run analysis
pbjrag analyze /app/codebase --config prod-config.yaml
```

### 4. Docker Setup

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  infinity:
    image: michaelf34/infinity:latest
    ports:
      - "7997:7997"

  pbjrag:
    build: .
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - INFINITY_URL=http://infinity:7997
      - PBJRAG_CORE_OUTPUT_DIR=/app/output
    volumes:
      - ./myproject:/app/code
      - ./output:/app/output
    command: pbjrag analyze /app/code

volumes:
  qdrant_data:
```

**Config for Docker** (`docker-config.yaml`):

```yaml
core:
  field_dim: 8
  output_dir: "/app/output"
  enable_vector_store: true

vector_store:
  qdrant:
    host: "qdrant"  # Service name in docker-compose
    port: 6333
  infinity_url: "http://infinity:7997"

chroma:
  path: "/app/chroma_db"  # Docker volume mount
```

### 5. ChromaDB Alternative (No Qdrant)

```yaml
# chroma-config.yaml
core:
  enable_vector_store: false  # Disable Qdrant
  enable_chroma: true          # Enable ChromaDB

chroma:
  path: "./chroma_storage"
  embedding_model: "all-mpnet-base-v2"
  batch_size: 32
```

```bash
export PBJRAG_CORE_ENABLE_CHROMA=true
export CHROMA_DB_PATH=/path/to/chroma/storage
pbjrag analyze ./project --config chroma-config.yaml
```

## Troubleshooting

### "Vector store initialization failed"

**Cause**: Can't connect to Qdrant or Infinity service

**Solutions**:
1. Check if services are running:
   ```bash
   curl http://localhost:6333  # Qdrant
   curl http://localhost:7997  # Infinity
   ```

2. Disable vector store:
   ```bash
   pbjrag analyze ./project --no-vector
   # OR
   export PBJRAG_CORE_ENABLE_VECTOR_STORE=false
   ```

3. Use ChromaDB alternative:
   ```bash
   export PBJRAG_CORE_ENABLE_CHROMA=true
   pip install chromadb
   ```

### "Neo4j connection failed"

**Cause**: Neo4j not running or password not set

**Solutions**:
1. Set password:
   ```bash
   export NEO4J_PASSWORD=your_password
   ```

2. Disable Neo4j:
   ```yaml
   # config.yaml
   core:
     enable_neo4j: false
   ```

### Configuration Not Being Picked Up

**Check priority order**:
1. CLI arguments (highest)
2. Environment variables
3. Custom config file
4. Default config (lowest)

**Debug**:
```bash
# Enable debug logging to see configuration loading
export PBJRAG_CORE_LOG_LEVEL=DEBUG
pbjrag analyze ./project
```

### Performance Issues

**Large codebases**:

```yaml
# performance-config.yaml
performance:
  worker_threads: 8  # Increase parallelism
  max_parallel_files: 10
  memory_optimization: false  # Prefer speed

chunking:
  max_lines: 50  # Smaller chunks
  strategy: "function"  # More granular
```

**Memory constraints**:

```yaml
# memory-optimized-config.yaml
performance:
  worker_threads: 2  # Reduce parallelism
  max_parallel_files: 2
  memory_optimization: true
  max_memory_mb: 2048  # 2GB limit

vector_store:
  batch_size: 16  # Smaller batches
```

## Advanced Topics

### Custom Embedding Models

```yaml
embedding:
  adapter: "sentence_transformers"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  dimension: 384
  normalize: true
  enable_cache: true
```

### Pattern Detection Tuning

```yaml
analysis:
  enable_pattern_detection: true
  pattern_confidence_threshold: 0.7  # Higher = fewer but more confident patterns
  enable_complexity_analysis: true
  complexity_threshold: 10  # Cyclomatic complexity limit
```

### Multiple Output Formats

```yaml
report:
  format: "all"  # Generate markdown, json, and html
  include_snippets: true
  max_snippet_length: 300
  persona: "devops"  # Use DevOps terminology
```

## Getting Help

- **Documentation**: https://github.com/Project-Navi/navi-pbjrag#readme
- **Issues**: https://github.com/Project-Navi/navi-pbjrag/issues
- **Debug mode**: `export PBJRAG_CORE_LOG_LEVEL=DEBUG`

## Configuration Schema

For a complete reference of all configuration options, see `config/default.yaml`.
