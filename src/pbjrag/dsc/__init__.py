"""
DSC (Differential Symbolic Calculus) Module

Translation note: DSC analyzes code as multi-dimensional fields
- For DevOps: Think of it as advanced code quality metrics
- For scholars: Mathematical field theory applied to code
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
