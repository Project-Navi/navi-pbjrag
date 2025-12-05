# PBJRAG WebUI Architecture

## System Overview

PBJRAG WebUI is a Docker-based application stack that provides a web interface for analyzing codebases using the Phenomenological Bayesian Justified RAG (PBJRAG) framework with Crown Jewel Core integration.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                       │
│              Streamlit WebUI (Port 8501)                │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│   │  1. Analyze  │ │  2. Explore  │ │  3. Search   │  │
│   │   Page       │ │    Page      │ │    Page      │  │
│   └──────┬───────┘ └──────┬───────┘ └──────┬───────┘  │
└──────────┼────────────────┼────────────────┼───────────┘
           │                │                │
           │   Streamlit Session State       │
           │   (analyzer, vector_store)      │
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│              Application Layer (Python)                  │
│                                                           │
│   ┌──────────────────────────────────────────────────┐  │
│   │           DSCAnalyzer (PBJRAG Core)              │  │
│   │  ┌──────────────┐  ┌──────────────────────────┐ │  │
│   │  │ DSCChunker   │  │  Crown Jewel Core        │ │  │
│   │  │ - Dependency │  │  - FieldContainer        │ │  │
│   │  │   Analysis   │  │  - PhaseManager          │ │  │
│   │  │ - Code       │  │  - Blessing System       │ │  │
│   │  │   Chunking   │  │  - Field States          │ │  │
│   │  └──────┬───────┘  └──────────┬───────────────┘ │  │
│   │         │                     │                  │  │
│   │         └─────────┬───────────┘                  │  │
│   │                   ▼                              │  │
│   │         ┌──────────────────┐                     │  │
│   │         │  DSCVectorStore  │                     │  │
│   │         │  - Embedding     │                     │  │
│   │         │  - Multi-vector  │                     │  │
│   │         │  - Hybrid search │                     │  │
│   │         └─────────┬────────┘                     │  │
│   └───────────────────┼──────────────────────────────┘  │
└───────────────────────┼──────────────────────────────────┘
                        │
                        │ HTTP/gRPC (6333/6334)
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│         Qdrant Vector Database (Port 6333/6334)         │
│                                                           │
│   Multi-Vector Collections (configurable dimension):    │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│   │   Content    │ │   Semantic   │ │   Ethical    │  │
│   │   Vectors    │ │   Vectors    │ │   Vectors    │  │
│   │   (N-dim)    │ │   (N-dim)    │ │   (N-dim)    │  │
│   └──────────────┘ └──────────────┘ └──────────────┘  │
│                                                           │
│   ┌──────────────┐ ┌──────────────┐                    │
│   │  Relational  │ │    Phase     │                    │
│   │   Vectors    │ │   Vectors    │                    │
│   │   (N-dim)    │ │   (N-dim)    │                    │
│   └──────────────┘ └──────────────┘                    │
│                                                           │
│   Persistent Storage: /qdrant/storage                   │
└─────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Container Services

#### Qdrant Container
- **Image**: `qdrant/qdrant:latest`
- **Ports**:
  - 6333 (HTTP API)
  - 6334 (gRPC API)
- **Volumes**: `qdrant_storage` (persistent vector data)
- **Health Check**: HTTP endpoint `/healthz`
- **Purpose**: Vector database for semantic search

#### WebUI Container
- **Base Image**: `python:3.11-slim`
- **Ports**: 8501 (Streamlit server)
- **Volumes**:
  - `./webui` → `/app/webui` (hot-reload development)
  - `./src` → `/app/src` (PBJRAG package source)
  - `./examples` → `/app/examples` (sample codebases)
  - `uploaded_codebases` (user uploads)
- **Dependencies**: Qdrant service health
- **Purpose**: Web interface and application logic

### 2. Application Layer

#### Main Entry Point (`webui/app.py`)
```python
Responsibilities:
- Page configuration (layout, theme, metadata)
- Session state initialization
- Sidebar navigation and configuration
- System status monitoring
- Welcome page with quick start guide

Session State Variables:
- analyzer: DSCAnalyzer instance
- vector_store: DSCVectorStore instance
- chunks: List[DSCChunk]
- indexed: bool (whether chunks are in Qdrant)
- qdrant_host: str
- qdrant_port: int
```

#### Page Structure (Multi-Page App)
1. **Home Page** (`app.py`)
   - Quick start guide
   - System status dashboard
   - Architecture overview
   - Quick statistics

2. **Analyze Page** (`pages/1_analyze.py`)
   - Codebase upload (directory/file)
   - DSC analysis execution
   - Chunk generation
   - Blessing assessment
   - Vector indexing to Qdrant

3. **Explore Page** (`pages/2_explore.py`)
   - Interactive visualizations
   - Chunk browsing with pagination
   - Dependency graphs
   - Field state analysis
   - Phase distribution

4. **Search Page** (`pages/3_search.py`)
   - Semantic search interface
   - Hybrid search modes
   - Field-specific queries
   - Purpose-aware retrieval
   - Result ranking and filtering

#### Component Library

**Charts Module** (`components/charts.py`)
```python
Functions:
- plot_blessing_distribution(chunks) → Pie chart
- plot_field_state_radar(chunk) → Radar chart
- plot_phase_timeline(chunks) → Bar chart
- plot_chunk_complexity_scatter(chunks) → Scatter plot
- plot_dependency_graph(chunks) → Network graph

Library: Plotly (interactive, exportable)
```

**Chunk Viewer Module** (`components/chunk_viewer.py`)
```python
Functions:
- render_chunk(chunk, show_metrics, show_code)
- render_chunk_list(chunks, page_size)
- render_chunk_details(chunk)

Features:
- Syntax highlighting (Pygments)
- Collapsible sections
- Tabbed interfaces
- Blessing color coding
```

### 3. Data Layer

#### Vector Collections Schema

**Collection Name**: `crown_jewel_dsc`

**Vector Configuration**:
```python
vectors_config = {
    "content": VectorParams(size=1024, distance=COSINE),
    "semantic": VectorParams(size=1024, distance=COSINE),
    "ethical": VectorParams(size=1024, distance=COSINE),
    "relational": VectorParams(size=1024, distance=COSINE),
    "phase": VectorParams(size=1024, distance=COSINE)
}
```

**Payload Structure**:
```python
{
    # Basic info
    "content": str,
    "chunk_type": str,
    "start_line": int,
    "end_line": int,
    "provides": List[str],
    "depends_on": List[str],
    "file_path": str,

    # Blessing state
    "blessing_tier": str,  # Φ+/Φ~/Φ-
    "blessing_epc": float,
    "blessing_ethical": float,
    "blessing_contradiction": float,
    "blessing_presence": float,
    "blessing_resonance": float,
    "blessing_phase": str,

    # Field summaries (for filtering)
    "semantic_complexity": float,
    "ethical_mean": float,
    "contradiction_mean": float,
    "temporal_stability": float,

    # Crown Jewel specific
    "current_phase": str,
    "field_coherence": float,

    # Searchable text
    "semantic_text": str,
    "ethical_text": str,
    "relational_text": str,
    "phase_text": str
}
```

## Data Flow

### Analysis Workflow
```
1. User uploads codebase
   ↓
2. DSCAnalyzer.analyze_directory()
   ↓
3. DSCCodeChunker creates chunks
   - Extracts functions, classes, methods
   - Analyzes dependencies (imports, calls)
   - Computes AST-based metrics
   ↓
4. Blessing system assesses each chunk
   - Ethical alignment (error handling, types)
   - Presence density (documentation)
   - Contradiction pressure (complexity)
   - Phase assignment (lifecycle stage)
   - Tier assignment (Φ+/Φ~/Φ-)
   ↓
5. Field states computed
   - Semantic: clarity, complexity, docs
   - Ethical: validation, error handling
   - Relational: coupling, independence
   - Contradiction: tensions, alignments
   - Temporal: consistency, evolution
   ↓
6. Chunks stored in session state
   ↓
7. User triggers indexing
   ↓
8. EmbeddingAdapter generates embeddings
   - Content embedding (code)
   - Field embeddings (metadata)
   - Multiple vector spaces
   - Dimension varies by model: BGE-M3 (1024), Jina-v2 (768)
   ↓
9. DSCVectorStore.index_chunks()
   - Batch upload to Qdrant
   - Rich payload with all metadata
   ↓
10. Chunks indexed and searchable
```

### Search Workflow
```
1. User enters query + filters
   ↓
2. Query parameters:
   - search_mode: content/semantic/ethical/relational/phase/hybrid
   - blessing_filter: Φ+/Φ~/Φ-
   - phase_filter: List[phase names]
   - purpose: stability/emergence/coherence
   - top_k: number of results
   ↓
3. DSCVectorStore.search()
   ↓
4. Build Qdrant filters
   - Blessing tier match
   - Phase match
   - Purpose-specific ranges
   ↓
5. Generate query embeddings
   - Task-specific embedding types
   - Weighted hybrid search
   ↓
6. Execute vector search
   - Single vector or multi-vector
   - Apply filters
   - Rank by similarity
   ↓
7. Format results
   - Extract payload
   - Add recommendations
   - Score breakdown
   ↓
8. Display in Streamlit
   - Render chunks
   - Show metrics
   - Highlight matches
```

## Scalability Design

### Horizontal Scaling

**WebUI Service**:
- Stateless design (state in session)
- Can run multiple replicas behind load balancer
- Shared Qdrant backend
- No inter-replica coordination needed

**Qdrant Service**:
- Supports clustering (enterprise)
- Sharding by collection
- Read replicas for scaling reads
- Write operations serialized

### Performance Optimizations

**Batch Operations**:
- Chunk indexing: 100 chunks per batch
- Embedding generation: Batch API calls
- Search: Prefetch and cache

**Caching Strategy**:
- Session state caches analyzer/vector_store
- Streamlit caches component renders
- Qdrant indexes for fast retrieval

**Resource Limits**:
```yaml
webui:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G

qdrant:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
      reservations:
        cpus: '2'
        memory: 4G
```

## Security Architecture

### Container Security
- Non-root user in containers
- Read-only root filesystem where possible
- Minimal base images (python:3.11-slim)
- No unnecessary packages

### Network Security
- Internal bridge network
- Only necessary ports exposed
- No direct Qdrant access from outside
- WebUI as API gateway

### Data Security
- Uploaded files isolated in volumes
- No hardcoded credentials
- Environment variable configuration
- Temporary file cleanup

## Deployment

### Development Setup
```bash
# Clone repository
git clone <repo>
cd navi-pbjrag

# Start stack
./quickstart.sh

# Access
open http://localhost:8501
```

### Production Considerations
1. **Reverse Proxy**: Nginx/Traefik with TLS
2. **Authentication**: OAuth/OIDC integration
3. **Monitoring**: Prometheus + Grafana
4. **Logging**: ELK stack or Loki
5. **Backups**: Qdrant volume snapshots
6. **Secrets**: HashiCorp Vault or AWS Secrets Manager

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit 1.40.0 | Web interface |
| Visualization | Plotly 5.24.1 | Interactive charts |
| Data Processing | Pandas 2.2.3 | DataFrame operations |
| Vector DB | Qdrant 1.12.1 | Semantic search |
| Syntax Highlighting | Pygments | Code display |
| Embeddings | BGE-M3 (1024-dim) / Jina-v2 (768-dim) | Text vectorization |
| Container Runtime | Docker 24+ | Containerization |
| Orchestration | Docker Compose | Multi-container |
| Language | Python 3.11 | Application logic |

## File Structure

```
navi-pbjrag/
├── docker-compose.yml      # Service orchestration
├── Dockerfile              # WebUI container image
├── quickstart.sh           # One-command launcher
├── src/                    # PBJRAG package
│   └── pbjrag/
│       ├── dsc/           # DSC analysis
│       │   ├── analyzer.py
│       │   ├── chunker.py
│       │   ├── vector_store.py
│       │   └── embedding_adapter.py
│       └── crown_jewel/   # Crown Jewel Core
│           ├── field_container.py
│           └── phase_manager.py
├── webui/                  # Streamlit application
│   ├── app.py             # Main entry point
│   ├── pages/             # Multi-page navigation
│   │   ├── 1_analyze.py
│   │   ├── 2_explore.py
│   │   └── 3_search.py
│   ├── components/        # Reusable components
│   │   ├── __init__.py
│   │   ├── charts.py
│   │   └── chunk_viewer.py
│   └── requirements.txt   # WebUI dependencies
├── docs/                   # Documentation
│   └── ARCHITECTURE.md    # This file
└── examples/              # Sample codebases
```

## Key Design Decisions

### 1. Multi-Page Streamlit App
**Rationale**: Separates concerns (analyze/explore/search), allows independent page development, cleaner navigation.

**Alternative**: Single-page with tabs (more state management complexity).

### 2. Session State for Context
**Rationale**: Preserves analyzer/vector_store across page navigation, avoids re-initialization.

**Alternative**: Global singletons (less Streamlit-idiomatic, harder to clear).

### 3. Qdrant Multi-Vector Collections
**Rationale**: Enables field-specific search (semantic/ethical/relational), hybrid retrieval, purpose-aware ranking.

**Alternative**: Single vector with metadata filtering (less semantic precision).

### 4. Docker Compose Stack
**Rationale**: One-command deployment, consistent environments, easy scaling to production Kubernetes.

**Alternative**: Local installation (dependency hell, platform-specific issues).

### 5. Hot-Reload Development Volumes
**Rationale**: Fast iteration during development, no container rebuilds for code changes.

**Alternative**: Rebuild container per change (slow feedback loop).

### 6. Plotly for Visualization
**Rationale**: Interactive charts, export capabilities, Streamlit integration, modern aesthetics.

**Alternative**: Matplotlib (static images, less interactive).

## Future Enhancements

### Phase 2
- [ ] User authentication and multi-tenancy
- [ ] Saved analysis sessions
- [ ] Custom blessing configuration
- [ ] Advanced search DSL
- [ ] Real-time collaboration

### Phase 3
- [ ] GitHub integration (analyze repos)
- [ ] API endpoints (headless mode)
- [ ] CLI companion tool
- [ ] Custom embedding models
- [ ] Batch analysis jobs

### Phase 4
- [ ] AI-powered refactoring suggestions
- [ ] Code evolution tracking
- [ ] Team analytics dashboard
- [ ] Integration with IDEs
- [ ] Plugin ecosystem

## Maintenance

### Monitoring
- Health checks on both services
- Qdrant collection size tracking
- WebUI response times
- Memory usage patterns

### Backup Strategy
- Qdrant volume snapshots (daily)
- Configuration backup (version controlled)
- Uploaded codebase retention policy

### Update Procedure
1. Pull latest images
2. Backup Qdrant volume
3. Run `docker-compose pull`
4. Run `docker-compose up -d`
5. Verify health checks
6. Test core workflows

## Troubleshooting

### Qdrant Connection Failed
- Check Docker network: `docker network inspect navi-pbjrag_pbjrag-network`
- Verify Qdrant health: `curl http://localhost:6333/healthz`
- Check logs: `docker-compose logs qdrant`

### WebUI Won't Start
- Check dependencies: `docker-compose logs webui`
- Verify port 8501 not in use: `lsof -i :8501`
- Check Dockerfile build: `docker-compose build webui`

### Slow Search Performance
- Check Qdrant index: `curl http://localhost:6333/collections/crown_jewel_dsc`
- Reduce top_k parameter
- Add more specific filters
- Consider Qdrant HNSW tuning

---

**Last Updated**: 2025-12-05
**Architecture Version**: 1.0.0
**Author**: SPARC Architecture Agent
