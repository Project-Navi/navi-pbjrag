"""
Extended tests for DSCChromaStore covering uncovered methods.
This extends coverage from 21% to target 80%.
"""

from unittest.mock import MagicMock, patch

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

    field_state = FieldState(
        semantic=np.array([0.5, 0.5, 0.5]),
        emotional=np.array([0.5, 0.5, 0.5]),
        ethical=np.array([0.5, 0.5, 0.5]),
        temporal=np.array([0.0, 1.0, 0.5]),
        entropic=np.array([0.2, 0.2]),
        rhythmic=np.array([0.5, 0.5]),
        contradiction=np.array([0.1, 0.1]),
        relational=np.array([0.5, 0.5, 0.5]),  # 3 values expected
        emergent=np.array([0.3, 0.3]),
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


class TestDSCChromaStoreEmbedding:
    """Test embedding function and generation."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.torch")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_embedding_setup_with_cuda(self, mock_ef, mock_torch, mock_chromadb, mock_settings):
        """Test embedding function setup with CUDA."""
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
        assert call_kwargs["model_name"] == "all-mpnet-base-v2"
        assert call_kwargs["device"] == "cuda"

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
        mock_embedding_fn.return_value = [[0.1] * 768]
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = mock_embedding_fn

        store = DSCChromaStore()
        embedding = store._get_embedding("test text")

        assert isinstance(embedding, list)
        assert len(embedding) == 768
        mock_embedding_fn.assert_called_once_with(["test text"])

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_get_embedding_fallback(self):
        """Test embedding fallback without ChromaDB."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        embedding = store._get_embedding("test text")

        assert isinstance(embedding, list)
        assert len(embedding) == 768


class TestDSCChromaStoreIndexing:
    """Test document indexing."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_index_chunks_without_collection(self):
        """Test indexing without ChromaDB."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        chunk = create_test_chunk()
        store.index_chunks([chunk])

        fragments = store.field_container.get_fragments()
        assert len(fragments) >= 1

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_index_chunks_with_collection(self, mock_ef, mock_chromadb, mock_settings):
        """Test indexing with ChromaDB collection."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        store = DSCChromaStore()
        chunks = [create_test_chunk(f"Content {i}") for i in range(5)]
        store.index_chunks(chunks)

        assert mock_collection.add.call_count == 1
        call_kwargs = mock_collection.add.call_args[1]
        assert len(call_kwargs["documents"]) == 5
        assert len(call_kwargs["metadatas"]) == 5


class TestDSCChromaStoreSearch:
    """Test search functionality."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", False)
    def test_search_without_collection(self):
        """Test search without collection."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        store = DSCChromaStore()
        results = store.search("test query")
        assert isinstance(results, list)

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_search_basic_query(self, mock_ef, mock_chromadb, mock_settings):
        """Test basic search query."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        mock_collection.query.return_value = {
            "ids": [["chunk_1"]],
            "distances": [[0.1]],
            "documents": [["Doc 1"]],
            "metadatas": [
                [
                    {
                        "chunk_type": "function",
                        "provides": '["func1"]',
                        "depends_on": "[]",
                        "file_path": "/test.py",
                        "blessing_tier": "Φ+",
                        "blessing_epc": 0.8,
                        "blessing_phase": "emergent",
                    }
                ]
            ],
        }

        store = DSCChromaStore()
        results = store.search("test query", top_k=5)

        assert len(results) == 1
        assert results[0]["id"] == "chunk_1"
        assert results[0]["score"] == 0.9  # 1.0 - 0.1

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_search_with_filters(self, mock_ef, mock_chromadb, mock_settings):
        """Test search with filters."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        mock_collection.query.return_value = {
            "ids": [[]],
            "distances": [[]],
            "documents": [[]],
            "metadatas": [[]],
        }

        store = DSCChromaStore()
        store.search("test", blessing_filter="Φ+", phase_filter=["emergent"])

        call_kwargs = mock_collection.query.call_args[1]
        assert "where" in call_kwargs


class TestDSCChromaStoreResonantSearch:
    """Test resonant chunk finding."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_find_resonant_chunks(self, mock_ef, mock_chromadb, mock_settings):
        """Test resonant chunk finding."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        mock_collection.query.return_value = {
            "ids": [["chunk_1", "chunk_2"]],
            "distances": [[0.1, 0.4]],  # Similarities: 0.9, 0.6
            "documents": [["Doc 1", "Doc 2"]],
            "metadatas": [[{"chunk_type": "function"}, {"chunk_type": "class"}]],
        }

        store = DSCChromaStore()
        results = store.find_resonant_chunks("test", min_resonance=0.7)

        assert len(results) == 1  # Only first meets threshold
        assert results[0]["resonance_score"] == 0.9


class TestDSCChromaStorePhaseEvolution:
    """Test phase evolution."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_evolve_chunks_valid_phase(self, mock_ef, mock_chromadb, mock_settings):
        """Test chunk evolution for valid phase."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        mock_collection.get.return_value = {
            "ids": ["chunk_1"],
            "documents": ["Doc 1"],
            "metadatas": [
                {
                    "blessing_phase": "turning",
                    "blessing_epc": 0.85,
                    "blessing_tier": "Φ+",
                    "blessing_ethical": 0.8,
                    "blessing_resonance": 0.7,
                    "blessing_contradiction": 0.2,
                }
            ],
        }

        store = DSCChromaStore()
        results = store.evolve_chunks_by_phase("emergent")

        assert len(results) == 1
        assert results[0]["target_phase"] == "emergent"


class TestDSCChromaStoreStats:
    """Test collection statistics."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_get_collection_stats(self, mock_ef, mock_chromadb, mock_settings):
        """Test collection statistics."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_collection.count.return_value = 50
        mock_collection.get.return_value = {
            "metadatas": [
                {"blessing_tier": "Φ+", "blessing_phase": "emergent"},
                {"blessing_tier": "Φ~", "blessing_phase": "becoming"},
            ]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = MagicMock()
        mock_settings.return_value = MagicMock()

        store = DSCChromaStore(collection_name="test")
        stats = store.get_collection_stats()

        assert stats["total_chunks"] == 50
        assert stats["collection_name"] == "test"
        assert "blessing_distribution" in stats


class TestDSCChromaStoreEmbedChunk:
    """Test chunk embedding."""

    @patch("pbjrag.dsc.chroma_store.HAVE_CHROMA", True)
    @patch("pbjrag.dsc.chroma_store.Settings")
    @patch("pbjrag.dsc.chroma_store.chromadb")
    @patch("pbjrag.dsc.chroma_store.embedding_functions")
    def test_embed_chunk(self, mock_ef, mock_chromadb, mock_settings):
        """Test chunk embedding."""
        from pbjrag.dsc.chroma_store import DSCChromaStore

        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_embedding_fn = MagicMock()
        mock_embedding_fn.return_value = [[0.1] * 768]
        mock_ef.SentenceTransformerEmbeddingFunction.return_value = mock_embedding_fn
        mock_settings.return_value = MagicMock()

        store = DSCChromaStore()
        chunk = create_test_chunk()
        embedded = store.embed_chunk(chunk)

        assert embedded.chunk == chunk
        assert len(embedded.embedding) == 768
        assert "semantic" in embedded.field_embeddings
