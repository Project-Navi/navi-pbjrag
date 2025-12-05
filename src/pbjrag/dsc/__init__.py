"""
DSC (Differential Symbolic Calculus) Module

The DSC module provides code analysis tools based on field theory mathematics.
It segments code into chunks, calculates quality metrics, and stores embeddings
for semantic search and retrieval.

What It Does:
    DSC analyzes source code by treating it as symbolic field objects with
    measurable properties. It chunks code intelligently, computes quality
    metrics (coherence, entropy, coupling), and stores vector embeddings
    for similarity search.

Core Components:
    - DSCAnalyzer: Main analysis engine for computing field properties
    - DSCCodeChunker: Segments source code into semantically meaningful chunks
    - DSCVectorStore: In-memory vector storage for code embeddings
    - DSCChromaStore: ChromaDB integration for persistent storage (optional)
    - FieldState: Data class storing code fragment properties (coherence, entropy)
    - BlessingState: Data class tracking quality tier and metrics
    - DSCChunk: Container for code chunk with field and blessing states

Measured Properties:
    - Coherence: Internal consistency and logical structure (0.0-1.0)
    - Entropy: Complexity and information density (0.0-1.0)
    - Coupling: Dependencies and interconnections (0.0-1.0)
    - Efficacy: Functional correctness and effectiveness (0.0-1.0)
    - Purity: Code cleanliness and best practices adherence (0.0-1.0)

Use Cases:
    - Code quality assessment and monitoring
    - Semantic code search and retrieval
    - Dependency analysis and coupling detection
    - Technical debt identification
    - Code evolution tracking over time

Example Usage:
    >>> from pbjrag.dsc import DSCAnalyzer, DSCCodeChunker, DSCVectorStore
    >>>
    >>> # Chunk and analyze code
    >>> chunker = DSCCodeChunker()
    >>> chunks = chunker.chunk_code(source_code, language="python")
    >>>
    >>> # Compute field properties
    >>> analyzer = DSCAnalyzer()
    >>> for chunk in chunks:
    ...     field_state = analyzer.compute_field_state(chunk)
    ...     print(f"Coherence: {field_state.coherence:.3f}")
    ...     print(f"Entropy: {field_state.entropy:.3f}")
    ...     print(f"Blessing Tier: {chunk.blessing_state.tier}")
    >>>
    >>> # Store and search embeddings
    >>> vector_store = DSCVectorStore()
    >>> vector_store.add_chunks(chunks)
    >>> similar = vector_store.search("authentication logic", k=5)

Optional Integrations:
    - ChromaDB: Persistent vector storage (install with chromadb extra)
    - Neo4j: Graph-based relationship mapping (install with neo4j extra)
    - Custom embeddings: Pluggable embedding model adapters

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

# Optional ChromaDB support
try:
    from .chroma_store import DSCChromaStore

    HAVE_CHROMA = True
except ImportError:
    DSCChromaStore = None
    HAVE_CHROMA = False

__all__ = [
    "DSCCodeChunker",
    "DSCChunk",
    "FieldState",
    "BlessingState",
    "DSCVectorStore",
    "DSCEmbeddedChunk",
    "DSCAnalyzer",
]

# Add ChromaDB store if available
if HAVE_CHROMA:
    __all__.append("DSCChromaStore")
