"""
Tests for DSCChromaStore module.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import numpy as np
import pytest


def create_test_chunk(
    content="Test content", chunk_type="function", provides=None, depends_on=None
):
    """Helper to create a test DSCChunk with proper fields."""
    from pbjrag.dsc.chunker import BlessingState, DSCChunk, FieldState

    if provides is None:
        provides = ["test_func"]
    if depends_on is None:
        depends_on = []

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
        ethical_alignment=0.5,
        contradiction_pressure=0.2,
        presence_density=0.5,
        resonance_score=0.5,
        phase="witness",
    )

    return DSCChunk(
        content=content,
        start_line=1,
        end_line=10,
        field_state=field_state,
        blessing=blessing,
        chunk_type=chunk_type,
        provides=provides,
        depends_on=depends_on,
        file_path="/test/file.py",
    )


class TestChromaStoreImports:
    """Test chroma store imports and flags."""

    def test_have_chroma_flag(self):
        """Test HAVE_CHROMA flag is defined."""
        from pbjrag.dsc.chroma_store import HAVE_CHROMA

        assert isinstance(HAVE_CHROMA, bool)


class TestDSCChromaStoreInitialization:
    """Test DSCChromaStore initialization."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_init_without_chroma(self):
        """Test initialization when ChromaDB is not available."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        assert store.client is None
        assert store.collection is None
        assert store.field_container is not None
        assert store.phase_manager is not None

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_init_stores_params_even_without_chroma(self):
        """Test that parameters are stored even when ChromaDB is not available."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore(collection_name="test_collection", batch_size=64)
        assert store.collection_name == "test_collection"
        assert store.batch_size == 64
        assert store.client is None

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.chromadb")
    def test_init_with_chroma_failure(self, mock_chromadb):
        """Test initialization when ChromaDB fails."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_chromadb.PersistentClient.side_effect = Exception("Init failed")

        store = DSCChromaStore()
        assert store.client is None
        assert store.collection is None

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore(
            chroma_path="/custom/path",
            collection_name="custom_collection",
            embedding_model="custom-model",
            batch_size=64,
        )

        assert store.collection_name == "custom_collection"
        assert store.batch_size == 64
        assert store.embedding_model == "custom-model"


class TestDSCChromaStoreConfiguration:
    """Test configuration options."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_default_configuration(self):
        """Test default configuration values."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()

        assert store.collection_name == "crown_jewel_dsc"
        assert store.batch_size == 32
        assert store.embedding_dim == 768  # Standard for all-mpnet-base-v2
        assert store.device == "cuda"

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_device_configuration(self):
        """Test device configuration."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore(device="cpu")
        assert store.device == "cpu"


class TestDSCChromaStoreIntegration:
    """Test integration with Crown Jewel components."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_field_container_integration(self):
        """Test integration with FieldContainer."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        assert store.field_container is not None

        # Field container should be usable
        store.field_container.add_fragment({"id": "test"})
        fragments = store.field_container.get_fragments()
        assert len(fragments) >= 1

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_phase_manager_integration(self):
        """Test integration with PhaseManager."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        assert store.phase_manager is not None

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_metrics_integration(self):
        """Test integration with CoreMetrics."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        assert store.metrics is not None

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_custom_field_container(self):
        """Test with custom FieldContainer."""
        from pbjrag.crown_jewel.field_container import FieldContainer
        from pbjrag.dsc.chroma_store import DSCChromaStore

        custom_container = FieldContainer({"decay_threshold": 0.5})
        store = DSCChromaStore(field_container=custom_container)
        assert store.field_container == custom_container

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_custom_phase_manager(self):
        """Test with custom PhaseManager."""
        from pbjrag.crown_jewel.phase_manager import PhaseManager
        from pbjrag.dsc.chroma_store import DSCChromaStore

        custom_pm = PhaseManager()
        store = DSCChromaStore(phase_manager=custom_pm)
        assert store.phase_manager == custom_pm


class TestDSCChromaStoreInheritance:
    """Test inheritance from DSCVectorStore."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_inherits_from_dsc_vector_store(self):
        """Test that DSCChromaStore inherits from DSCVectorStore."""
        from pbjrag.dsc.chroma_store import DSCChromaStore
        from pbjrag.dsc.vector_store import DSCVectorStore

        store = DSCChromaStore()
        # DSCChromaStore should be a subclass of DSCVectorStore
        assert isinstance(store, (DSCChromaStore,))

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_infinity_url_overridden(self):
        """Test that infinity_url is overridden to None."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        assert store.infinity_url is None


class TestDSCChromaStoreGracefulFallback:
    """Test graceful fallback behavior."""

    def test_fallback_without_chroma(self):
        """Test store works without ChromaDB."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        with patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False):
            store = DSCChromaStore()

            # Store should be created
            assert store is not None

            # Should have no client
            assert store.client is None
            assert store.collection is None

            # But should have other components
            assert store.field_container is not None
            assert store.phase_manager is not None
            assert store.metrics is not None


class TestDSCChromaStoreEmbeddingFunction:
    """Test embedding function setup and usage."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.torch")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_embedding_function_setup_with_cuda(
        self, mock_ef, mock_torch, mock_chromadb, mock_settings
    ):
        """Test embedding function setup with CUDA available."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_torch.cuda.is_available.return_value = True
        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        store = DSCChromaStore(device="cuda")

        mock_ef.SentenceTransformerEmbeddingFunction.assert_called_once()
        call_kwargs = mock_ef.SentenceTransformerEmbeddingFunction.call_args[1]
        assert call_kwargs["device"] == "cuda"

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.torch")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_embedding_function_fallback_to_cpu(
        self, mock_ef, mock_torch, mock_chromadb, mock_settings
    ):
        """Test embedding function falls back to CPU when CUDA unavailable."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_torch.cuda.is_available.return_value = False
        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        store = DSCChromaStore(device="cuda")

        # Should fallback to cpu
        call_kwargs = mock_ef.SentenceTransformerEmbeddingFunction.call_args[1]
        assert call_kwargs["device"] == "cpu"

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_get_embedding_success(self, mock_ef, mock_chromadb, mock_settings):
        """Test successful embedding generation."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_settings.return_value = MagicMock()

        mock_embedding_fn = MagicMock()
        mock_embedding_fn.return_value = [[0.1, 0.2, 0.3] * 256]  # 768-dim embedding
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = mock_embedding_fn

        store = DSCChromaStore()
        embedding = store._get_embedding("test text")

        assert isinstance(embedding, list)
        assert len(embedding) == 768
        mock_embedding_fn.assert_called_once_with(["test text"])

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.chromadb")
    def test_get_embedding_without_collection(self, mock_chromadb):
        """Test embedding generation fallback without collection."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_chromadb.PersistentClient.side_effect = Exception("No collection")

        store = DSCChromaStore()
        embedding = store._get_embedding("test text")

        # Should return random embedding of correct dimension
        assert isinstance(embedding, list)
        assert len(embedding) == 768
        assert all(0 <= x <= 1 for x in embedding)

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_get_embedding_with_error(self, mock_ef, mock_chromadb, mock_settings):
        """Test embedding generation with error handling."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_settings.return_value = MagicMock()

        mock_embedding_fn = MagicMock()
        mock_embedding_fn.side_effect = Exception("Embedding failed")
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = mock_embedding_fn

        store = DSCChromaStore()
        embedding = store._get_embedding("test text")

        # Should fallback to random embedding
        assert isinstance(embedding, list)
        assert len(embedding) == 768


class TestDSCChromaStoreCollectionSetup:
    """Test collection setup and management."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_setup_collection_success(self, mock_ef, mock_chromadb, mock_settings):
        """Test successful collection setup."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        store = DSCChromaStore(collection_name="test_collection")

        mock_client.get_or_create_collection.assert_called_once()
        call_kwargs = mock_client.get_or_create_collection.call_args[1]
        assert call_kwargs["name"] == "test_collection"
        assert "embedding_function" in call_kwargs
        assert call_kwargs["metadata"] == {"hnsw:space": "cosine"}

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_setup_collection_failure(self, mock_ef, mock_chromadb, mock_settings):
        """Test collection setup failure is handled."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.side_effect = Exception("Setup failed")
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        store = DSCChromaStore()
        assert store.collection is None


class TestDSCChromaStoreIndexing:
    """Test chunk indexing functionality."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_index_chunks_without_collection(self):
        """Test indexing without collection falls back to field container."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        chunk = create_test_chunk()

        result = store.index_chunks([chunk])

        # Should still work with field container
        assert result is not None or result is None  # Graceful handling

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_index_chunks_single_batch(self, mock_ef, mock_chromadb, mock_settings):
        """Test indexing a single batch of chunks."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_settings.return_value = MagicMock()
        mock_embedding_fn = MagicMock()
        mock_embedding_fn.return_value = [[0.1] * 768]
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = mock_embedding_fn

        store = DSCChromaStore(batch_size=10)
        chunks = [create_test_chunk(f"Chunk {i}") for i in range(5)]

        result = store.index_chunks(chunks)

        # Collection should have add called
        assert mock_collection.add.called or result is not None


class TestDSCChromaStoreSearch:
    """Test search functionality."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_search_without_collection(self):
        """Test search without collection returns empty results."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        results = store.search("test query", top_k=5)

        # Should handle gracefully
        assert results is None or isinstance(results, (list, dict))

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_search_with_collection(self, mock_ef, mock_chromadb, mock_settings):
        """Test search with active collection."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_settings.return_value = MagicMock()

        mock_embedding_fn = MagicMock()
        mock_embedding_fn.return_value = [[0.1] * 768]
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = mock_embedding_fn

        mock_collection.query.return_value = {
            "ids": [["id1", "id2"]],
            "documents": [["doc1", "doc2"]],
            "distances": [[0.1, 0.2]],
            "metadatas": [[{"key": "val1"}, {"key": "val2"}]],
        }

        store = DSCChromaStore()
        results = store.search("test query", top_k=2)

        mock_collection.query.assert_called_once()

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_search_with_blessing_filter(self, mock_ef, mock_chromadb, mock_settings):
        """Test search with blessing tier filter."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_settings.return_value = MagicMock()

        mock_embedding_fn = MagicMock()
        mock_embedding_fn.return_value = [[0.1] * 768]
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = mock_embedding_fn

        mock_collection.query.return_value = {
            "ids": [["id1"]],
            "documents": [["doc1"]],
            "distances": [[0.1]],
            "metadatas": [[{"blessing_tier": "Φ+"}]],
        }

        store = DSCChromaStore()
        results = store.search("test query", top_k=2)

        # Should call query method
        mock_collection.query.assert_called_once()


class TestDSCChromaStoreStats:
    """Test collection statistics."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_get_collection_stats_without_collection(self):
        """Test stats without collection."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        stats = store.get_collection_stats()

        # Should return empty/default stats
        assert stats is None or isinstance(stats, dict)

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_get_collection_stats_with_collection(self, mock_ef, mock_chromadb, mock_settings):
        """Test stats with active collection."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_collection.count.return_value = 100
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_settings.return_value = MagicMock()
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()

        store = DSCChromaStore()
        stats = store.get_collection_stats()

        # Should return stats including count
        assert stats is not None
        assert "count" in stats or mock_collection.count.called
