"""
Tests for DSCVectorStore module.
"""

from dataclasses import asdict
from unittest.mock import MagicMock, PropertyMock, patch

import pytest


class TestDSCVectorStoreImports:
    """Test vector store imports and flags."""

    def test_have_qdrant_flag(self):
        """Test HAVE_QDRANT flag is defined."""
        from pbjrag.dsc.vector_store import HAVE_QDRANT

        assert isinstance(HAVE_QDRANT, bool)

    def test_dsc_embedded_chunk_dataclass(self):
        """Test DSCEmbeddedChunk dataclass."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCEmbeddedChunk

        # Create proper field state with numpy arrays
        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        # Create proper blessing state
        blessing = BlessingState(
            tier="Φ~",
            epc=0.5,
            ethical_alignment=0.7,
            contradiction_pressure=0.3,
            presence_density=0.6,
            resonance_score=0.8,
            phase="witness",
        )

        chunk = DSCChunk(
            content="def test(): pass",
            chunk_type="function",
            start_line=1,
            end_line=1,
            file_path="test.py",
            field_state=field_state,
            blessing=blessing,
            provides=["test"],
            depends_on=[],
        )

        embedded = DSCEmbeddedChunk(
            chunk=chunk, embedding=[0.1, 0.2, 0.3], field_embeddings={"semantic": [0.1, 0.2]}
        )

        assert embedded.chunk == chunk
        assert embedded.embedding == [0.1, 0.2, 0.3]
        assert "semantic" in embedded.field_embeddings


class TestDSCVectorStoreInitialization:
    """Test DSCVectorStore initialization."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_init_without_qdrant(self):
        """Test initialization when Qdrant is not available."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()
        assert store.client is None
        assert store.field_container is not None
        assert store.phase_manager is not None

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_init_with_qdrant_connection_failure(self, mock_qdrant):
        """Test initialization when Qdrant connection fails."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_qdrant.return_value.get_collections.side_effect = Exception("Connection failed")

        store = DSCVectorStore()
        assert store.client is None  # Falls back gracefully

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_init_with_qdrant_success(self, mock_qdrant):
        """Test successful initialization with Qdrant."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()
        assert store.client is not None
        assert store.collection_name == "crown_jewel_dsc"

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_init_with_custom_params(self, mock_qdrant):
        """Test initialization with custom parameters."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore(
            qdrant_host="custom-host",
            qdrant_port=6334,
            collection_name="custom_collection",
            embedding_backend="openai",
            embedding_dim=512,
        )

        assert store.collection_name == "custom_collection"
        assert store.embedding_dim == 512

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_init_with_existing_collection(self, mock_qdrant):
        """Test initialization with existing collection."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.name = "crown_jewel_dsc"
        mock_client.get_collections.return_value.collections = [mock_collection]
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()
        # Should not create collection
        mock_client.create_collection.assert_not_called()

    def test_init_with_custom_field_container(self):
        """Test initialization with custom FieldContainer."""
        from pbjrag.crown_jewel.field_container import FieldContainer
        from pbjrag.dsc.vector_store import HAVE_QDRANT, DSCVectorStore

        custom_container = FieldContainer({"decay_threshold": 0.5})

        with patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False):
            store = DSCVectorStore(field_container=custom_container)
            assert store.field_container == custom_container

    def test_init_with_custom_phase_manager(self):
        """Test initialization with custom PhaseManager."""
        from pbjrag.crown_jewel.phase_manager import PhaseManager
        from pbjrag.dsc.vector_store import DSCVectorStore

        custom_pm = PhaseManager()

        with patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False):
            store = DSCVectorStore(phase_manager=custom_pm)
            assert store.phase_manager == custom_pm


class TestDSCVectorStoreEmbedding:
    """Test embedding functionality."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_embedder_initialization(self):
        """Test embedding adapter is initialized."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore(
            embedding_backend="ollama",
            embedding_model="test-model",
            embedding_url="http://localhost:11434",
        )

        assert store.embedder is not None
        assert store.embedding_model == "test-model"
        assert store.embedding_url == "http://localhost:11434"


class TestDSCVectorStoreConfiguration:
    """Test configuration options."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_default_configuration(self):
        """Test default configuration values."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        assert store.collection_name == "crown_jewel_dsc"
        assert store.embedding_dim == 1024
        assert store.embedding_url == "http://localhost:11434"

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_embedding_dimension_config(self):
        """Test embedding dimension configuration."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        for dim in [256, 512, 768, 1024]:
            store = DSCVectorStore(embedding_dim=dim)
            assert store.embedding_dim == dim


class TestDSCVectorStoreIntegration:
    """Test integration with Crown Jewel components."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_field_container_integration(self):
        """Test integration with FieldContainer."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()
        assert store.field_container is not None

        # Field container should be usable
        store.field_container.add_fragment({"id": "test"})
        fragments = store.field_container.get_fragments()
        assert len(fragments) >= 1

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_phase_manager_integration(self):
        """Test integration with PhaseManager."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()
        assert store.phase_manager is not None

        # Phase manager should be usable - it might be None initially
        # Just verify the phase_manager object exists and is functional
        assert hasattr(store.phase_manager, "current_phase")

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_metrics_integration(self):
        """Test integration with CoreMetrics."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()
        assert store.metrics is not None


class TestDSCVectorStoreCollectionSetup:
    """Test collection setup functionality."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_setup_collection_creates_new(self, mock_qdrant):
        """Test collection setup creates new collection."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        # Collection should be created
        mock_client.create_collection.assert_called_once()

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_setup_collection_multi_vector(self, mock_qdrant):
        """Test collection is created with multi-vector config."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        # Check create_collection was called with vectors_config
        call_args = mock_client.create_collection.call_args
        assert "vectors_config" in call_args.kwargs


class TestDSCVectorStoreGracefulFallback:
    """Test graceful fallback behavior."""

    def test_fallback_without_qdrant(self):
        """Test store works without Qdrant."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        with patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False):
            store = DSCVectorStore()

            # Store should be created
            assert store is not None

            # Should have no client
            assert store.client is None

            # But should have other components
            assert store.field_container is not None
            assert store.phase_manager is not None
            assert store.embedder is not None

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_fallback_on_connection_error(self, mock_qdrant):
        """Test store handles connection errors gracefully."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_qdrant.return_value.get_collections.side_effect = ConnectionError("No connection")

        # Should not raise
        store = DSCVectorStore()
        assert store.client is None


class TestDSCVectorStoreDSCChunkIntegration:
    """Test DSCChunk integration."""

    def test_chunk_embedding_dataclass(self):
        """Test DSCEmbeddedChunk stores chunk correctly."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCEmbeddedChunk

        # Create proper field state with numpy arrays
        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        # Create proper blessing state
        blessing = BlessingState(
            tier="Φ+",
            epc=0.8,
            ethical_alignment=0.9,
            contradiction_pressure=0.1,
            presence_density=0.7,
            resonance_score=0.85,
            phase="emergent",
        )

        chunk = DSCChunk(
            content="def hello(): print('hi')",
            chunk_type="function",
            start_line=1,
            end_line=2,
            file_path="hello.py",
            field_state=field_state,
            blessing=blessing,
            provides=["hello"],
            depends_on=[],
        )

        embedded = DSCEmbeddedChunk(
            chunk=chunk,
            embedding=[0.5] * 1024,
            field_embeddings={"semantic": [0.3] * 1024, "ethical": [0.4] * 1024},
        )

        assert embedded.chunk.content == "def hello(): print('hi')"
        assert embedded.chunk.blessing.tier == "Φ+"
        assert len(embedded.embedding) == 1024
        assert "semantic" in embedded.field_embeddings
        assert "ethical" in embedded.field_embeddings


class TestDSCVectorStoreEmbedChunk:
    """Test chunk embedding functionality."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_embed_chunk_basic(self):
        """Test basic chunk embedding."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        # Create test chunk
        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        blessing = BlessingState(
            tier="Φ~",
            epc=0.5,
            ethical_alignment=0.7,
            contradiction_pressure=0.3,
            presence_density=0.6,
            resonance_score=0.8,
            phase="witness",
        )

        chunk = DSCChunk(
            content="def test(): pass",
            chunk_type="function",
            start_line=1,
            end_line=1,
            file_path="test.py",
            field_state=field_state,
            blessing=blessing,
            provides=["test"],
            depends_on=[],
        )

        # Mock embedder
        with patch.object(store.embedder, "embed") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            embedded = store.embed_chunk(chunk)

            assert embedded.chunk == chunk
            assert embedded.embedding == [0.1] * 1024
            assert "semantic" in embedded.field_embeddings
            assert "ethical" in embedded.field_embeddings
            assert "relational" in embedded.field_embeddings
            assert "phase" in embedded.field_embeddings

            # Verify embedder was called with different tasks
            assert mock_embed.call_count >= 5

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_field_to_text_semantic(self):
        """Test semantic field to text conversion."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        dim = 8
        semantic_field = np.array([0.5, 0.7, 0.9, 0.3, 0.4, 0.6, 0.8, 0.2])
        field_state = FieldState(
            semantic=semantic_field,
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        blessing = BlessingState(
            tier="Φ+",
            epc=0.8,
            ethical_alignment=0.9,
            contradiction_pressure=0.1,
            presence_density=0.7,
            resonance_score=0.85,
            phase="emergent",
        )

        chunk = DSCChunk(
            content="def complex_function(): pass",
            chunk_type="function",
            start_line=1,
            end_line=2,
            file_path="test.py",
            field_state=field_state,
            blessing=blessing,
            provides=["complex_function"],
            depends_on=["utils"],
        )

        text = store._field_to_text(chunk, "semantic")
        assert "function" in text
        assert "complex_function" in text
        assert "complexity:" in text

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_field_to_text_ethical(self):
        """Test ethical field to text conversion."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.array([0.8, 0.9, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        blessing = BlessingState(
            tier="Φ+",
            epc=0.8,
            ethical_alignment=0.9,
            contradiction_pressure=0.1,
            presence_density=0.7,
            resonance_score=0.85,
            phase="emergent",
        )

        chunk = DSCChunk(
            content="def safe_function(): pass",
            chunk_type="function",
            start_line=1,
            end_line=2,
            file_path="test.py",
            field_state=field_state,
            blessing=blessing,
            provides=["safe_function"],
            depends_on=[],
        )

        text = store._field_to_text(chunk, "ethical")
        assert "ethical_alignment:" in text
        assert "blessing:Φ+" in text

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_field_to_text_relational(self):
        """Test relational field to text conversion."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.2]),
            emergent=np.random.rand(dim),
        )

        blessing = BlessingState(
            tier="Φ~",
            epc=0.5,
            ethical_alignment=0.7,
            contradiction_pressure=0.3,
            presence_density=0.6,
            resonance_score=0.8,
            phase="witness",
        )

        chunk = DSCChunk(
            content="def connected(): pass",
            chunk_type="function",
            start_line=1,
            end_line=2,
            file_path="test.py",
            field_state=field_state,
            blessing=blessing,
            provides=["connected"],
            depends_on=["module_a", "module_b"],
        )

        text = store._field_to_text(chunk, "relational")
        assert "depends_on:" in text
        assert "provides:" in text
        assert "coupling:" in text

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_phase_to_text(self):
        """Test phase to text conversion."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        blessing = BlessingState(
            tier="Φ+",
            epc=0.85,
            ethical_alignment=0.92,
            contradiction_pressure=0.08,
            presence_density=0.75,
            resonance_score=0.88,
            phase="emergent",
        )

        chunk = DSCChunk(
            content="def emergent_code(): pass",
            chunk_type="function",
            start_line=1,
            end_line=2,
            file_path="test.py",
            field_state=field_state,
            blessing=blessing,
            provides=["emergent_code"],
            depends_on=[],
        )

        text = store._phase_to_text(chunk)
        assert "phase:emergent" in text
        assert "epc:0.85" in text
        assert "tier:Φ+" in text


class TestDSCVectorStoreSearch:
    """Test search functionality."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_search_without_qdrant(self):
        """Test search fallback without Qdrant."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        # Add a chunk to field container
        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        blessing = BlessingState(
            tier="Φ+",
            epc=0.8,
            ethical_alignment=0.9,
            contradiction_pressure=0.1,
            presence_density=0.7,
            resonance_score=0.85,
            phase="emergent",
        )

        chunk = DSCChunk(
            content="def search_test(): pass",
            chunk_type="function",
            start_line=1,
            end_line=2,
            file_path="test.py",
            field_state=field_state,
            blessing=blessing,
            provides=["search_test"],
            depends_on=[],
        )

        fragment = chunk.to_fragment()
        store.field_container.add_fragment(fragment)

        results = store.search("search", top_k=5)
        assert isinstance(results, list)

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_search_with_qdrant_content_mode(self, mock_qdrant):
        """Test search with Qdrant in content mode."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []

        # Mock query response
        mock_point = MagicMock()
        mock_point.id = 1
        mock_point.score = 0.95
        mock_point.payload = {
            "content": "test content",
            "chunk_type": "function",
            "provides": ["test"],
            "depends_on": [],
            "file_path": "test.py",
            "blessing_tier": "Φ+",
            "blessing_epc": 0.8,
            "blessing_phase": "emergent",
            "blessing_ethical": 0.9,
            "blessing_resonance": 0.85,
            "semantic_complexity": 0.5,
            "ethical_mean": 0.8,
            "contradiction_mean": 0.2,
        }

        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_client.query_points.return_value = mock_response
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        with patch.object(store.embedder, "embed") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            results = store.search("test query", search_mode="content", top_k=5)

            assert isinstance(results, list)
            assert len(results) > 0
            assert results[0]["content"] == "test content"
            assert results[0]["blessing"]["tier"] == "Φ+"

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_search_with_blessing_filter(self, mock_qdrant):
        """Test search with blessing tier filter."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []

        mock_point = MagicMock()
        mock_point.id = 1
        mock_point.score = 0.95
        mock_point.payload = {
            "content": "test",
            "chunk_type": "function",
            "provides": [],
            "depends_on": [],
            "file_path": "test.py",
            "blessing_tier": "Φ+",
            "blessing_epc": 0.8,
            "blessing_phase": "emergent",
            "blessing_ethical": 0.9,
            "blessing_resonance": 0.85,
            "semantic_complexity": 0.5,
            "ethical_mean": 0.8,
            "contradiction_mean": 0.2,
        }

        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_client.query_points.return_value = mock_response
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        with patch.object(store.embedder, "embed") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            results = store.search("test", search_mode="content", blessing_filter="Φ+", top_k=5)

            assert len(results) > 0
            mock_client.query_points.assert_called_once()

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_search_with_phase_filter(self, mock_qdrant):
        """Test search with phase filter."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []

        mock_point = MagicMock()
        mock_point.id = 1
        mock_point.score = 0.95
        mock_point.payload = {
            "content": "test",
            "chunk_type": "function",
            "provides": [],
            "depends_on": [],
            "file_path": "test.py",
            "blessing_tier": "Φ+",
            "blessing_epc": 0.8,
            "blessing_phase": "emergent",
            "blessing_ethical": 0.9,
            "blessing_resonance": 0.85,
            "semantic_complexity": 0.5,
            "ethical_mean": 0.8,
            "contradiction_mean": 0.2,
        }

        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_client.query_points.return_value = mock_response
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        with patch.object(store.embedder, "embed") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            results = store.search(
                "test", search_mode="semantic", phase_filter=["emergent", "turning"], top_k=5
            )

            assert len(results) > 0

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_search_with_purpose_stability(self, mock_qdrant):
        """Test search with stability purpose."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []

        mock_point = MagicMock()
        mock_point.id = 1
        mock_point.score = 0.95
        mock_point.payload = {
            "content": "test",
            "chunk_type": "function",
            "provides": [],
            "depends_on": [],
            "file_path": "test.py",
            "blessing_tier": "Φ+",
            "blessing_epc": 0.8,
            "blessing_phase": "witness",
            "blessing_ethical": 0.9,
            "blessing_resonance": 0.85,
            "blessing_contradiction": 0.1,
            "semantic_complexity": 0.5,
            "ethical_mean": 0.8,
            "contradiction_mean": 0.2,
        }

        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_client.query_points.return_value = mock_response
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        with patch.object(store.embedder, "embed") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            results = store.search("test", search_mode="ethical", purpose="stability", top_k=5)

            assert len(results) > 0

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_hybrid_search(self, mock_qdrant):
        """Test hybrid search mode."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []

        mock_point = MagicMock()
        mock_point.id = 1
        mock_point.score = 0.95
        mock_point.payload = {
            "content": "test content",
            "chunk_type": "function",
            "provides": ["test"],
            "depends_on": [],
            "file_path": "test.py",
            "blessing_tier": "Φ+",
            "blessing_epc": 0.8,
            "blessing_phase": "emergent",
            "blessing_ethical": 0.9,
            "blessing_resonance": 0.85,
            "semantic_complexity": 0.5,
            "ethical_mean": 0.8,
            "contradiction_mean": 0.2,
        }

        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_client.query_points.return_value = mock_response
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        with patch.object(store.embedder, "embed") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            results = store.search("test query", search_mode="hybrid", purpose="coherence", top_k=5)

            assert isinstance(results, list)

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_search_field_container_with_filters(self):
        """Test field container search with filters."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        # Add fragments with different blessings
        store.field_container.add_fragment(
            {
                "content": "good code test",
                "chunk_type": "function",
                "provides": ["test"],
                "depends_on": [],
                "blessing": {"Φ": "Φ+"},
                "dsc_blessing": {"phase": "emergent"},
            }
        )

        store.field_container.add_fragment(
            {
                "content": "bad code test",
                "chunk_type": "function",
                "provides": ["test"],
                "depends_on": [],
                "blessing": {"Φ": "Φ-"},
                "dsc_blessing": {"phase": "compost"},
            }
        )

        # Search with blessing filter
        results = store._search_field_container(
            "test", blessing_filter="Φ+", phase_filter=None, top_k=5
        )

        assert len(results) > 0


class TestDSCVectorStoreIndexing:
    """Test chunk indexing functionality."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_index_chunks_without_qdrant(self):
        """Test indexing chunks without Qdrant."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        blessing = BlessingState(
            tier="Φ+",
            epc=0.8,
            ethical_alignment=0.9,
            contradiction_pressure=0.1,
            presence_density=0.7,
            resonance_score=0.85,
            phase="emergent",
        )

        chunks = [
            DSCChunk(
                content=f"def test_{i}(): pass",
                chunk_type="function",
                start_line=i,
                end_line=i + 1,
                file_path="test.py",
                field_state=field_state,
                blessing=blessing,
                provides=[f"test_{i}"],
                depends_on=[],
            )
            for i in range(3)
        ]

        # Should not raise even without Qdrant
        store.index_chunks(chunks)

        # Chunks should be in field container
        fragments = store.field_container.get_fragments()
        assert len(fragments) >= 3

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_index_chunks_with_qdrant(self, mock_qdrant):
        """Test indexing chunks with Qdrant."""
        import numpy as np

        from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_client.upsert.return_value = None
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        dim = 8
        field_state = FieldState(
            semantic=np.random.rand(dim),
            emotional=np.random.rand(dim),
            ethical=np.random.rand(dim),
            temporal=np.random.rand(dim),
            entropic=np.random.rand(dim),
            rhythmic=np.random.rand(dim),
            contradiction=np.random.rand(dim),
            relational=np.random.rand(dim),
            emergent=np.random.rand(dim),
        )

        blessing = BlessingState(
            tier="Φ~",
            epc=0.5,
            ethical_alignment=0.7,
            contradiction_pressure=0.3,
            presence_density=0.6,
            resonance_score=0.8,
            phase="witness",
        )

        chunks = [
            DSCChunk(
                content=f"def func_{i}(): pass",
                chunk_type="function",
                start_line=i,
                end_line=i + 1,
                file_path="module.py",
                field_state=field_state,
                blessing=blessing,
                provides=[f"func_{i}"],
                depends_on=[],
            )
            for i in range(5)
        ]

        with patch.object(store.embedder, "embed") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            store.index_chunks(chunks, batch_size=2)

            # Verify upsert was called
            assert mock_client.upsert.call_count > 0


class TestDSCVectorStoreResonance:
    """Test resonance finding functionality."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_find_resonant_chunks_without_qdrant(self):
        """Test resonance search without Qdrant."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        results = store.find_resonant_chunks(1, min_resonance=0.7)
        assert isinstance(results, list)
        assert len(results) == 0

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_find_resonant_chunks_with_qdrant(self, mock_qdrant):
        """Test resonance search with Qdrant."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []

        # Mock retrieve response
        mock_reference = MagicMock()
        mock_reference.id = 1
        mock_reference.vector = {
            "semantic": [0.1] * 1024,
            "ethical": [0.2] * 1024,
            "relational": [0.3] * 1024,
            "phase": [0.4] * 1024,
        }
        mock_reference.payload = {"content": "reference"}
        mock_client.retrieve.return_value = [mock_reference]

        # Mock search response
        mock_result = MagicMock()
        mock_result.id = 2
        mock_result.score = 0.85
        mock_result.payload = {"content": "resonant code", "resonance_score": 0.85}
        mock_client.search.return_value = [mock_result]

        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        results = store.find_resonant_chunks(1, min_resonance=0.7)

        assert isinstance(results, list)
        assert mock_client.retrieve.called
        assert mock_client.search.called


class TestDSCVectorStorePhaseEvolution:
    """Test phase evolution functionality."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_evolve_chunks_without_qdrant(self):
        """Test phase evolution without Qdrant."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        candidates = store.evolve_chunks_by_phase("becoming")
        assert isinstance(candidates, list)
        assert len(candidates) == 0

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_evolve_chunks_by_phase(self, mock_qdrant):
        """Test finding chunks ready for phase evolution."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []

        # Mock scroll response
        mock_result = MagicMock()
        mock_result.payload = {
            "content": "evolving code",
            "blessing_phase": "compost",
            "blessing_epc": 0.4,
            "blessing_tier": "Φ~",
            "blessing_ethical": 0.7,
            "blessing_resonance": 0.6,
        }
        mock_client.scroll.return_value = ([mock_result], None)

        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        candidates = store.evolve_chunks_by_phase("reflection")

        assert isinstance(candidates, list)
        if len(candidates) > 0:
            assert "evolution_readiness" in candidates[0]
            assert "target_phase" in candidates[0]

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", True)
    @patch("pbjrag.dsc.vector_store.QdrantClient")
    def test_calculate_evolution_readiness(self, mock_qdrant):
        """Test evolution readiness calculation."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_qdrant.return_value = mock_client

        store = DSCVectorStore()

        payload = {"blessing_epc": 0.7, "blessing_ethical": 0.8, "blessing_resonance": 0.75}

        # Test stillness target
        readiness = store._calculate_evolution_readiness(payload, "stillness")
        assert 0.0 <= readiness <= 1.0

        # Test emergent target
        readiness = store._calculate_evolution_readiness(payload, "emergent")
        assert 0.0 <= readiness <= 1.0


class TestDSCVectorStorePurposeRecommendations:
    """Test purpose-specific recommendations."""

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_get_purpose_recommendations_stability(self):
        """Test stability recommendations."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        payload = {
            "blessing_tier": "Φ-",
            "blessing_phase": "compost",
            "blessing_epc": 0.3,
            "blessing_contradiction": 0.6,
            "blessing_resonance": 0.4,
        }

        recommendations = store._get_purpose_recommendations(payload, "stability")
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_get_purpose_recommendations_emergence(self):
        """Test emergence recommendations."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        payload = {
            "blessing_tier": "Φ+",
            "blessing_phase": "compost",
            "blessing_epc": 0.8,
            "blessing_contradiction": 0.2,
            "blessing_resonance": 0.85,
        }

        recommendations = store._get_purpose_recommendations(payload, "emergence")
        assert isinstance(recommendations, list)

    @patch("pbjrag.dsc.vector_store.HAVE_QDRANT", False)
    def test_get_purpose_recommendations_coherence(self):
        """Test coherence recommendations."""
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCVectorStore()

        payload = {
            "blessing_tier": "Φ-",
            "blessing_phase": "witness",
            "blessing_epc": 0.5,
            "blessing_contradiction": 0.3,
            "blessing_resonance": 0.3,
        }

        recommendations = store._get_purpose_recommendations(payload, "coherence")
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
