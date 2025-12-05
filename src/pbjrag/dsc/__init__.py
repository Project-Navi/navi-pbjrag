"""
DSC (Differential Symbolic Calculus) Module

The DSC module provides code analysis tools based on field theory mathematics.
It segments code into chunks, calculates quality metrics, and stores embeddings
for semantic search and retrieval.

PBJRAG v3 is Qdrant-native - Qdrant is the only actively maintained vector store.
See docs/adapters/ for legacy adapter templates if you need custom integrations.

What It Does:
    DSC analyzes source code by treating it as symbolic field objects with
    measurable properties. It chunks code intelligently, computes quality
    metrics (coherence, entropy, coupling), and stores vector embeddings
    for similarity search.

Core Components:
    - DSCAnalyzer: Main analysis engine for computing field properties
    - DSCCodeChunker: Segments source code into semantically meaningful chunks
    - DSCVectorStore: Qdrant-native vector storage with multi-vector support
    - FieldState: Data class storing code fragment properties (9-dimensional)
    - BlessingState: Data class tracking quality tier and metrics
    - DSCChunk: Container for code chunk with field and blessing states

Measured Properties (9 Dimensions):
    - Semantic: Pattern complexity and logical structure (0.0-1.0)
    - Emotional: Affective context and intent (0.0-1.0)
    - Ethical: Alignment with best practices (0.0-1.0)
    - Temporal: Time stability and evolution (0.0-1.0)
    - Entropic: Chaos/order balance (0.0-1.0)
    - Rhythmic: Structural patterns (0.0-1.0)
    - Contradiction: Tension points (0.0-1.0)
    - Relational: Dependency connections (0.0-1.0)
    - Emergent: Evolution potential (0.0-1.0)

Use Cases:
    - Code quality assessment and monitoring
    - Semantic code search and retrieval
    - Dependency analysis and coupling detection
    - Technical debt identification
    - Code evolution tracking over time

Example Usage:
    >>> from pbjrag.dsc import DSCAnalyzer, DSCCodeChunker, DSCVectorStore
    >>>
    >>> # Chunk code
    >>> chunker = DSCCodeChunker()
    >>> chunks = chunker.chunk_code(source_code, filepath="example.py")
    >>>
    >>> # Analyze and print blessing info
    >>> for chunk in chunks:
    ...     print(f"Type: {chunk.chunk_type}")
    ...     print(f"Blessing Tier: {chunk.blessing.tier}")
    ...     print(f"Phase: {chunk.blessing.phase}")
    >>>
    >>> # Or use DSCAnalyzer for file/project analysis
    >>> analyzer = DSCAnalyzer()
    >>> results = analyzer.analyze_file("my_code.py")
    >>>
    >>> # With Qdrant vector store
    >>> vector_store = DSCVectorStore()  # Connects to Qdrant at localhost:6333
    >>> vector_store.index_chunks(chunks)
    >>> results = vector_store.search("authentication logic", top_k=5)

Vector Store:
    - Primary: Qdrant (localhost:6333) - multi-vector support for 9D fields
    - Legacy: ChromaDB adapter available in dsc.legacy (not maintained)
    - Custom: See docs/adapters/CUSTOM_ADAPTER_TEMPLATE.md

Embedding:
    - Backend: Ollama (snowflake-arctic-embed2)
    - Dimensions: 1024

Field Theory Background:
    DSC applies differential operators from mathematical field theory:
    - Gradients measure semantic relationship directions
    - Derivatives track code evolution over time
    - Integrals aggregate properties over code regions
    - Field equations govern quality state transitions
"""

from .analyzer import DSCAnalyzer
from .chunker import BlessingState, DSCChunk, DSCCodeChunker, FieldState
from .vector_store import DSCEmbeddedChunk, DSCVectorStore

# Legacy ChromaDB support (archived - use Qdrant instead)
# Import from pbjrag.dsc.legacy.chroma_store if needed
HAVE_CHROMA = False  # Deprecated - Qdrant is now the default

__all__ = [
    "DSCCodeChunker",
    "DSCChunk",
    "FieldState",
    "BlessingState",
    "DSCVectorStore",
    "DSCEmbeddedChunk",
    "DSCAnalyzer",
]
