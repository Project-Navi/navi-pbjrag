"""
Tests for DSCCodeChunker - Code chunking with field analysis.
"""

import pytest
import numpy as np
from pbjrag.dsc import DSCCodeChunker, DSCChunk, FieldState, BlessingState
from pbjrag.crown_jewel import FieldContainer


class TestDSCCodeChunker:
    """Test suite for DSCCodeChunker."""

    def test_chunker_initialization(self):
        """Test that DSCCodeChunker initializes correctly."""
        chunker = DSCCodeChunker(field_dim=8)

        assert chunker is not None
        assert chunker.field_dim == 8

    def test_chunker_with_field_container(self):
        """Test chunker initialization with a FieldContainer."""
        field_container = FieldContainer()
        chunker = DSCCodeChunker(field_dim=8, field_container=field_container)

        assert chunker.field_container is field_container

    def test_chunk_code_produces_chunks(self, sample_python_code):
        """Test that chunk_code produces DSCChunk objects."""
        chunker = DSCCodeChunker(field_dim=8)

        chunks = chunker.chunk_code(sample_python_code, filepath="test.py")

        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Verify all chunks are DSCChunk instances
        for chunk in chunks:
            assert isinstance(chunk, DSCChunk)

    def test_chunk_has_required_fields(self, sample_python_code):
        """Test that DSCChunk has all required fields."""
        chunker = DSCCodeChunker(field_dim=8)

        chunks = chunker.chunk_code(sample_python_code, filepath="test.py")
        chunk = chunks[0]

        assert isinstance(chunk.content, str)
        assert isinstance(chunk.start_line, int)
        assert isinstance(chunk.end_line, int)
        assert isinstance(chunk.field_state, FieldState)
        assert isinstance(chunk.blessing, BlessingState)
        assert isinstance(chunk.chunk_type, str)
        assert isinstance(chunk.provides, list)
        assert isinstance(chunk.depends_on, list)

    def test_field_state_structure(self, sample_python_code):
        """Test that FieldState has correct structure."""
        chunker = DSCCodeChunker(field_dim=8)

        chunks = chunker.chunk_code(sample_python_code, filepath="test.py")
        field_state = chunks[0].field_state

        # Check all field dimensions exist
        assert isinstance(field_state.semantic, np.ndarray)
        assert isinstance(field_state.emotional, np.ndarray)
        assert isinstance(field_state.ethical, np.ndarray)
        assert isinstance(field_state.temporal, np.ndarray)
        assert isinstance(field_state.entropic, np.ndarray)
        assert isinstance(field_state.rhythmic, np.ndarray)
        assert isinstance(field_state.contradiction, np.ndarray)
        assert isinstance(field_state.relational, np.ndarray)
        assert isinstance(field_state.emergent, np.ndarray)

        # Check dimension
        assert field_state.dimension == 8

    def test_blessing_state_structure(self, sample_python_code):
        """Test that BlessingState has correct structure."""
        chunker = DSCCodeChunker(field_dim=8)

        chunks = chunker.chunk_code(sample_python_code, filepath="test.py")
        blessing = chunks[0].blessing

        assert isinstance(blessing.tier, str)
        assert blessing.tier in ["Φ+", "Φ~", "Φ-"]
        assert isinstance(blessing.epc, float)
        assert isinstance(blessing.ethical_alignment, float)
        assert isinstance(blessing.contradiction_pressure, float)
        assert isinstance(blessing.presence_density, float)
        assert isinstance(blessing.resonance_score, float)
        assert isinstance(blessing.phase, str)

    def test_chunk_serialization(self, sample_python_code):
        """Test that chunks can be serialized to dict."""
        chunker = DSCCodeChunker(field_dim=8)

        chunks = chunker.chunk_code(sample_python_code, filepath="test.py")
        chunk = chunks[0]

        # Test fragment conversion
        fragment = chunk.to_fragment()
        assert isinstance(fragment, dict)
        assert "content" in fragment
        assert "start_line" in fragment
        assert "end_line" in fragment

        # Test field state serialization
        field_dict = chunk.field_state.to_dict()
        assert isinstance(field_dict, dict)
        assert "semantic" in field_dict

        # Test blessing state serialization
        blessing_dict = chunk.blessing.to_dict()
        assert isinstance(blessing_dict, dict)
        assert "tier" in blessing_dict
        assert "epc" in blessing_dict

    def test_empty_code_handling(self):
        """Test chunker handles empty code gracefully."""
        chunker = DSCCodeChunker(field_dim=8)

        chunks = chunker.chunk_code("", filepath="empty.py")

        # Should either return empty list or handle gracefully
        assert isinstance(chunks, list)

    def test_chunk_type_detection(self, sample_python_code):
        """Test that chunk types are correctly detected."""
        chunker = DSCCodeChunker(field_dim=8)

        chunks = chunker.chunk_code(sample_python_code, filepath="test.py")

        # Find function and class chunks
        chunk_types = {chunk.chunk_type for chunk in chunks}

        # Should detect different types of code structures
        assert len(chunk_types) > 0
        assert all(isinstance(ct, str) for ct in chunk_types)
