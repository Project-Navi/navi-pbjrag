"""
DSC (Differential Symbolic Calculus) Module

The DSC module implements differential symbolic calculus for code analysis,
treating code as multi-dimensional symbolic fields that can be differentiated,
integrated, and analyzed using field theory principles.

Core Concepts:
    Differential Symbolic Calculus applies mathematical field theory to code:
    - Code fragments exist as points in a symbolic field space
    - Field properties (coherence, entropy, coupling) evolve over time
    - Semantic relationships form field gradients and potentials
    - Analysis operations are differential transformations in field space

Key Components:
    - DSCAnalyzer: Main analysis engine using differential symbolic calculus
    - DSCCodeChunker: Intelligent code segmentation with field-aware boundaries
    - DSCVectorStore: Vector storage with field-theoretic embeddings
    - DSCChromaStore: ChromaDB integration for persistent vector storage
    - FieldState: Represents code fragment field properties (coherence, entropy)
    - BlessingState: Tracks blessing tier and quality metrics
    - DSCChunk: Code chunk with field state and blessing information

Field Properties:
    - Coherence: Measure of internal consistency and logical structure
    - Entropy: Measure of complexity and information density
    - Coupling: Measure of dependencies and interconnections
    - Efficacy: Measure of functional correctness and effectiveness
    - Purity: Measure of code cleanliness and best practices

Translation Guide:
    - For DevOps: Advanced code quality metrics with semantic understanding
    - For Researchers: Mathematical field theory applied to software analysis
    - For Developers: Intelligent code chunking and quality assessment
    - For Architects: Semantic relationship mapping and dependency analysis

Example Usage:
    >>> from pbjrag.dsc import DSCAnalyzer, DSCCodeChunker, DSCVectorStore
    >>>
    >>> # Chunk and analyze code
    >>> chunker = DSCCodeChunker()
    >>> chunks = chunker.chunk_code(source_code, language="python")
    >>>
    >>> # Analyze field properties
    >>> analyzer = DSCAnalyzer()
    >>> for chunk in chunks:
    ...     field_state = analyzer.compute_field_state(chunk)
    ...     print(f"Coherence: {field_state.coherence:.3f}")
    ...     print(f"Entropy: {field_state.entropy:.3f}")
    ...     print(f"Blessing: {chunk.blessing_state.tier}")
    >>>
    >>> # Store embeddings
    >>> vector_store = DSCVectorStore()
    >>> vector_store.add_chunks(chunks)
    >>> similar = vector_store.search("authentication logic", k=5)

Optional Integrations:
    - ChromaDB: Persistent vector storage (import DSCChromaStore)
    - Neo4j: Graph-based relationship mapping (requires neo4j extra)
    - Custom embeddings: Pluggable embedding adapters

Mathematical Foundation:
    DSC uses differential operators on symbolic field spaces:
    - ∇ (gradient): Semantic relationship direction
    - ∂/∂t (derivative): Code evolution over time
    - ∫ (integral): Aggregate field properties over regions
    - Field equations govern blessing state evolution
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
