"""
Legacy Vector Store Adapters

This module contains archived vector store implementations that are no longer
actively maintained. PBJRAG is now Qdrant-native.

The ChromaStore adapter is preserved here as a reference for those who wish
to implement their own vector store adapter.

See docs/adapters/CUSTOM_ADAPTER_TEMPLATE.md for implementation guidance.
"""

# Legacy imports (use with caution - not actively maintained)
try:
    from .chroma_store import DSCChromaStore
except ImportError:
    DSCChromaStore = None

__all__ = ["DSCChromaStore"]
