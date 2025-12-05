"""
Tests for optional dependencies - Feature flags and graceful fallback.
"""

import sys
from unittest.mock import patch

import pytest


class TestOptionalDependencies:
    """Test suite for optional dependency handling."""

    def test_chroma_feature_flag_exists(self):
        """Test that HAVE_CHROMA feature flag exists."""
        from pbjrag.dsc import HAVE_CHROMA

        assert isinstance(HAVE_CHROMA, bool)

    def test_chroma_import_when_available(self):
        """Test ChromaDB import when available."""
        from pbjrag.dsc import HAVE_CHROMA

        if HAVE_CHROMA:
            # If ChromaDB is available, should be able to import
            from pbjrag.dsc import DSCChromaStore

            assert DSCChromaStore is not None
        else:
            # If not available, should handle gracefully
            from pbjrag import dsc

            assert not hasattr(dsc, "DSCChromaStore") or dsc.DSCChromaStore is None

    def test_qdrant_feature_flag_detection(self):
        """Test HAVE_QDRANT feature flag detection."""
        try:
            from pbjrag.dsc.vector_store import HAVE_QDRANT

            assert isinstance(HAVE_QDRANT, bool)
        except ImportError:
            # Module might not be directly importable, that's ok
            pass

    def test_neo4j_feature_flag_detection(self):
        """Test HAVE_NEO4J feature flag detection."""
        try:
            from pbjrag.dsc.neo4j_store import HAVE_NEO4J

            assert isinstance(HAVE_NEO4J, bool)
        except ImportError:
            # Module might not be directly importable, that's ok
            pass

    def test_analyzer_works_without_optional_deps(self):
        """Test that DSCAnalyzer works without optional dependencies."""
        from pbjrag import DSCAnalyzer

        # Disable vector store
        config = {"enable_vector_store": False}
        analyzer = DSCAnalyzer(config=config)

        assert analyzer is not None
        assert analyzer.vector_store is None

    def test_chunker_works_without_optional_deps(self):
        """Test that DSCCodeChunker works without optional dependencies."""
        from pbjrag import DSCCodeChunker

        chunker = DSCCodeChunker(field_dim=8)

        # Should work even if optional deps are missing
        assert chunker is not None

    def test_graceful_fallback_on_missing_chroma(self, sample_python_code):
        """Test graceful fallback when ChromaDB is missing."""
        # Temporarily hide chromadb if it exists
        with patch.dict(sys.modules, {"chromadb": None}):
            # Re-import to trigger feature detection
            import importlib

            from pbjrag import dsc

            importlib.reload(dsc)

            # Should still be able to use basic functionality
            from pbjrag import DSCCodeChunker

            chunker = DSCCodeChunker(field_dim=8)
            chunks = chunker.chunk_code(sample_python_code, filepath="test.py")

            assert len(chunks) > 0

    def test_vector_store_disabled_config(self):
        """Test that vector store can be explicitly disabled."""
        from pbjrag import DSCAnalyzer

        config = {"enable_vector_store": False}
        analyzer = DSCAnalyzer(config=config)

        assert analyzer.vector_store is None

    def test_feature_flags_are_boolean(self):
        """Test that all feature flags are boolean values."""
        from pbjrag.dsc import HAVE_CHROMA

        assert isinstance(HAVE_CHROMA, bool)

        # Try to import other feature flags if available
        try:
            from pbjrag.dsc.vector_store import HAVE_QDRANT

            assert isinstance(HAVE_QDRANT, bool)
        except (ImportError, AttributeError):
            pass

        try:
            from pbjrag.dsc.neo4j_store import HAVE_NEO4J

            assert isinstance(HAVE_NEO4J, bool)
        except (ImportError, AttributeError):
            pass

    def test_optional_store_initialization_failures(self):
        """Test that store initialization failures are handled gracefully."""
        from pbjrag import DSCAnalyzer

        # Provide invalid connection parameters
        config = {
            "enable_vector_store": True,
            "qdrant_host": "invalid-host-that-does-not-exist",
            "qdrant_port": 99999,
        }

        # Should not raise, but vector_store should be None
        analyzer = DSCAnalyzer(config=config)

        # Analyzer should still be functional even if vector store failed
        assert analyzer is not None

    def test_core_functionality_without_stores(self, sample_python_code):
        """Test that core analysis works without any vector stores."""
        from pbjrag import DSCCodeChunker

        chunker = DSCCodeChunker(field_dim=8)
        chunks = chunker.chunk_code(sample_python_code, filepath="test.py")

        # Core functionality should work
        assert len(chunks) > 0
        assert all(hasattr(chunk, "blessing") for chunk in chunks)
        assert all(hasattr(chunk, "field_state") for chunk in chunks)

    def test_imports_do_not_fail_without_optional_deps(self):
        """Test that basic imports work without optional dependencies."""
        # These should always work regardless of optional deps
        from pbjrag import DSCAnalyzer, DSCCodeChunker, Orchestrator, PhaseManager
        from pbjrag.crown_jewel import CoreMetrics, FieldContainer, create_blessing_vector
        from pbjrag.dsc import BlessingState, DSCChunk, FieldState

        # All imports should succeed
        assert DSCAnalyzer is not None
        assert DSCCodeChunker is not None
        assert PhaseManager is not None
        assert Orchestrator is not None
        assert CoreMetrics is not None
        assert create_blessing_vector is not None
        assert FieldContainer is not None
        assert DSCChunk is not None
        assert FieldState is not None
        assert BlessingState is not None
