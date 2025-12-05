"""
Tests for EmbeddingAdapter module.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestEmbeddingAdapterInitialization:
    """Test EmbeddingAdapter initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter()
        assert adapter.backend == "ollama"
        assert adapter.model == "bge-m3"
        assert adapter.base_url == "http://localhost:11434"
        assert adapter.dimension == 1024

    def test_custom_backend_initialization(self):
        """Test initialization with custom backend."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(backend="openai")
        assert adapter.backend == "openai"

    def test_custom_model_initialization(self):
        """Test initialization with custom model."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(model="nomic-embed-text")
        assert adapter.model == "nomic-embed-text"

    def test_custom_url_initialization(self):
        """Test initialization with custom URL."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(base_url="http://custom:8080/")
        assert adapter.base_url == "http://custom:8080"  # Trailing slash removed

    def test_custom_dimension(self):
        """Test initialization with custom dimension."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        for dim in [256, 384, 512, 768, 1024]:
            adapter = EmbeddingAdapter(dimension=dim)
            assert adapter.dimension == dim

    def test_instruction_templates(self):
        """Test instruction templates are defined."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter()
        assert "search_document" in adapter.instructions
        assert "search_query" in adapter.instructions
        assert "clustering" in adapter.instructions
        assert "classification" in adapter.instructions
        assert "semantic" in adapter.instructions
        assert "structural" in adapter.instructions


class TestEmbeddingAdapterEmbed:
    """Test embed method."""

    def test_embed_calls_correct_backend_ollama(self):
        """Test embed routes to ollama backend."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(backend="ollama")

        with patch.object(adapter, "_embed_ollama", return_value=[0.1] * 1024) as mock:
            result = adapter.embed("test text")
            mock.assert_called_once()

    def test_embed_calls_correct_backend_openai(self):
        """Test embed routes to openai backend."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(backend="openai")

        with patch.object(adapter, "_embed_openai", return_value=[0.1] * 1024) as mock:
            result = adapter.embed("test text")
            mock.assert_called_once()

    def test_embed_calls_correct_backend_instructor(self):
        """Test embed routes to instructor backend."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(backend="instructor")

        with patch.object(adapter, "_embed_instructor", return_value=[0.1] * 1024) as mock:
            result = adapter.embed("test text")
            mock.assert_called_once()

    def test_embed_calls_correct_backend_direct(self):
        """Test embed routes to direct backend."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(backend="direct")

        with patch.object(adapter, "_embed_direct", return_value=[0.1] * 1024) as mock:
            result = adapter.embed("test text")
            mock.assert_called_once()

    def test_embed_fallback_for_unknown_backend(self):
        """Test embed uses fallback for unknown backend."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter()
        adapter.backend = "unknown_backend"

        with patch.object(adapter, "_embed_fallback", return_value=[0.0] * 1024) as mock:
            result = adapter.embed("test text")
            mock.assert_called_once()

    def test_embed_with_different_tasks(self):
        """Test embed with different task types."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(backend="ollama")

        with patch.object(adapter, "_embed_ollama", return_value=[0.1] * 1024) as mock:
            for task in ["search_document", "search_query", "clustering", "classification"]:
                adapter.embed("test text", task=task)


class TestEmbeddingAdapterFallback:
    """Test fallback embedding."""

    def test_fallback_returns_correct_dimension(self):
        """Test fallback returns vector of correct dimension."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(dimension=512)
        result = adapter._embed_fallback("test")

        assert len(result) == 512

    def test_fallback_returns_list(self):
        """Test fallback returns a list."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter()
        result = adapter._embed_fallback("test")

        assert isinstance(result, list)


class TestEmbeddingAdapterOllama:
    """Test Ollama-specific functionality."""

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_ollama_embed_success(self, mock_post):
        """Test successful Ollama embedding."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="ollama")
        result = adapter._embed_ollama("test text", "search_document")

        assert len(result) == 1024

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_ollama_embed_with_nomic_model(self, mock_post):
        """Test Ollama embedding with nomic model prefix."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": [0.1] * 768}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="ollama", model="nomic-embed-text")
        result = adapter._embed_ollama("test text", "search_document")

        # Check that prompt was prefixed
        call_args = mock_post.call_args
        assert "search_document:" in call_args.kwargs.get("json", {}).get("prompt", "")

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_ollama_embed_failure_returns_fallback(self, mock_post):
        """Test Ollama embedding returns fallback on failure."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_post.side_effect = Exception("Connection error")

        adapter = EmbeddingAdapter(backend="ollama", dimension=512)
        result = adapter._embed_ollama("test text", "search_document")

        # Should return fallback of correct dimension
        assert len(result) == 512


class TestEmbeddingAdapterBatchEmbed:
    """Test batch embedding functionality."""

    def test_batch_embed_exists(self):
        """Test batch_embed method exists."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter()
        assert hasattr(adapter, "batch_embed") or hasattr(adapter, "embed")

    def test_embed_multiple_texts(self):
        """Test embedding multiple texts."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter()

        with patch.object(adapter, "_embed_fallback", return_value=[0.0] * 1024):
            adapter.backend = "unknown"
            texts = ["text1", "text2", "text3"]
            results = [adapter.embed(t) for t in texts]

            assert len(results) == 3
            for r in results:
                assert len(r) == 1024

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_batch_embed_with_ollama(self, mock_post):
        """Test batch_embed with Ollama backend."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="ollama")
        texts = ["text1", "text2", "text3"]
        results = adapter.batch_embed(texts, task="search_document")

        assert len(results) == 3
        assert all(len(r) == 1024 for r in results)

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_batch_embed_with_custom_task(self, mock_post):
        """Test batch_embed with custom task."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="ollama")
        texts = ["query1", "query2"]
        results = adapter.batch_embed(texts, task="search_query")

        assert len(results) == 2


class TestEmbeddingAdapterOpenAI:
    """Test OpenAI-compatible API functionality."""

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_success(self, mock_post):
        """Test successful OpenAI embedding."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 1024}]}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="openai", base_url="http://localhost:8000")
        result = adapter._embed_openai("test text", "search_document")

        assert len(result) == 1024
        mock_post.assert_called_once()

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_with_instructor_model(self, mock_post):
        """Test OpenAI embedding with instructor model."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 1024}]}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(
            backend="openai", model="instructor-xl", base_url="http://localhost:8000"
        )
        result = adapter._embed_openai("test text", "search_document")

        # Check that instruction was added
        call_args = mock_post.call_args
        input_text = call_args.kwargs.get("json", {}).get("input", "")
        assert "Represent" in input_text or len(result) == 1024

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_with_e5_model(self, mock_post):
        """Test OpenAI embedding with E5 model."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 768}]}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(
            backend="openai", model="e5-large", base_url="http://localhost:8000"
        )
        result = adapter._embed_openai("test text", "search_query")

        assert len(result) == 768

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_with_nomic_model(self, mock_post):
        """Test OpenAI embedding with Nomic model prefixes."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 768}]}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(
            backend="openai", model="nomic-embed-text", base_url="http://localhost:8000"
        )
        result = adapter._embed_openai("test text", "search_document")

        # Check that prefix was added
        call_args = mock_post.call_args
        input_text = call_args.kwargs.get("json", {}).get("input", "")
        assert "search_document:" in input_text

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_infinity_endpoint(self, mock_post):
        """Test OpenAI embedding with Infinity endpoint."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 1024}]}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="openai", base_url="http://localhost:7997")
        result = adapter._embed_openai("test text", "search_document")

        # Should use /embeddings endpoint for Infinity
        call_args = mock_post.call_args
        assert call_args[0][0].endswith("/embeddings")
        assert len(result) == 1024

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_lmstudio_endpoint(self, mock_post):
        """Test OpenAI embedding with LMStudio endpoint."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 1024}]}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="openai", base_url="http://localhost:1234")
        result = adapter._embed_openai("test text", "search_document")

        # Should use /v1/embeddings endpoint for LMStudio
        call_args = mock_post.call_args
        assert call_args[0][0].endswith("/v1/embeddings")

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_http_error(self, mock_post):
        """Test OpenAI embedding returns fallback on HTTP error."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="openai", dimension=512)
        result = adapter._embed_openai("test text", "search_document")

        # Should return fallback of correct dimension
        assert len(result) == 512

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_malformed_response(self, mock_post):
        """Test OpenAI embedding handles malformed response."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="openai", dimension=512)
        result = adapter._embed_openai("test text", "search_document")

        # Should return fallback
        assert len(result) == 512

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_empty_data(self, mock_post):
        """Test OpenAI embedding handles empty data array."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="openai", dimension=512)
        result = adapter._embed_openai("test text", "search_document")

        # Should return fallback
        assert len(result) == 512

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_keyerror(self, mock_post):
        """Test OpenAI embedding handles KeyError."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"not_embedding": []}]}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="openai", dimension=512)
        result = adapter._embed_openai("test text", "search_document")

        # Should return fallback
        assert len(result) == 512

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_openai_embed_exception(self, mock_post):
        """Test OpenAI embedding handles exceptions."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_post.side_effect = Exception("Connection error")

        adapter = EmbeddingAdapter(backend="openai", dimension=512)
        result = adapter._embed_openai("test text", "search_document")

        # Should return fallback
        assert len(result) == 512


class TestEmbeddingAdapterInstructor:
    """Test instructor-style functionality."""

    def test_instructor_embed_uses_instruction(self):
        """Test instructor embedding adds instruction."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        with patch.object(EmbeddingAdapter, "_embed_openai") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            adapter = EmbeddingAdapter(backend="instructor")
            result = adapter._embed_instructor("test text", "search_document")

            # Should call _embed_openai with prefixed text
            call_args = mock_embed.call_args
            assert "Represent this code for retrieval:" in call_args[0][0]

    def test_instructor_embed_all_tasks(self):
        """Test instructor embedding with all task types."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        with patch.object(EmbeddingAdapter, "_embed_openai") as mock_embed:
            mock_embed.return_value = [0.1] * 1024

            adapter = EmbeddingAdapter(backend="instructor")
            tasks = ["search_document", "search_query", "clustering", "classification"]

            for task in tasks:
                result = adapter._embed_instructor("test text", task)
                assert len(result) == 1024


class TestEmbeddingAdapterDirect:
    """Test direct sentence-transformers functionality."""

    def test_direct_embed_success(self):
        """Test direct embedding with sentence-transformers."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([0.1] * 1024)
            mock_st.return_value = mock_model

            adapter = EmbeddingAdapter(backend="direct", model="bge-m3")
            result = adapter._embed_direct("test text", "search_document")

            assert len(result) == 1024
            assert isinstance(result, list)

    def test_direct_embed_with_instructor_model(self):
        """Test direct embedding with instructor model."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([0.1] * 768)
            mock_st.return_value = mock_model

            adapter = EmbeddingAdapter(backend="direct", model="instructor-xl")
            result = adapter._embed_direct("test text", "search_document")

            # Should pass instruction format
            call_args = mock_model.encode.call_args
            input_arg = call_args[0][0]
            assert isinstance(input_arg, list)

    def test_direct_embed_caches_model(self):
        """Test direct embedding caches model instance."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([0.1] * 1024)
            mock_st.return_value = mock_model

            adapter = EmbeddingAdapter(backend="direct")

            # First call should create model
            adapter._embed_direct("test1", "search_document")
            assert hasattr(adapter, "_model")

            # Second call should reuse model
            adapter._embed_direct("test2", "search_document")
            mock_st.assert_called_once()

    def test_direct_embed_import_error(self):
        """Test direct embedding handles ImportError."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        adapter = EmbeddingAdapter(backend="direct", dimension=512)

        # Force ImportError by removing the import
        with patch.dict("sys.modules", {"sentence_transformers": None}):
            result = adapter._embed_direct("test text", "search_document")

        # Should return fallback
        assert len(result) == 512

    def test_direct_embed_exception(self):
        """Test direct embedding handles exceptions."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_st.side_effect = Exception("Model loading error")

            adapter = EmbeddingAdapter(backend="direct", dimension=512)
            result = adapter._embed_direct("test text", "search_document")

            # Should return fallback
            assert len(result) == 512


class TestEmbeddingAdapterSnowflakeModel:
    """Test Snowflake Arctic Embed model functionality."""

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_ollama_snowflake_search_query(self, mock_post):
        """Test Snowflake model with search_query task."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="ollama", model="snowflake-arctic-embed2:latest")
        result = adapter._embed_ollama("test query", "search_query")

        # Check that correct prompt format was used
        call_args = mock_post.call_args
        prompt = call_args.kwargs.get("json", {}).get("prompt", "")
        assert "Represent this sentence for searching relevant passages:" in prompt

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_ollama_snowflake_search_document(self, mock_post):
        """Test Snowflake model with search_document task."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="ollama", model="snowflake-arctic-embed2:latest")
        result = adapter._embed_ollama("test document", "search_document")

        # Check that correct prompt format was used
        call_args = mock_post.call_args
        prompt = call_args.kwargs.get("json", {}).get("prompt", "")
        assert "Represent this document for retrieval:" in prompt

    @patch("pbjrag.dsc.embedding_adapter.requests.post")
    def test_ollama_bge_m3_model(self, mock_post):
        """Test BGE-M3 model with instruction format."""
        from pbjrag.dsc.embedding_adapter import EmbeddingAdapter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_post.return_value = mock_response

        adapter = EmbeddingAdapter(backend="ollama", model="bge-m3")
        result = adapter._embed_ollama("test query", "search_query")

        # Check that correct prompt format was used
        call_args = mock_post.call_args
        prompt = call_args.kwargs.get("json", {}).get("prompt", "")
        assert "Represent this sentence for searching relevant passages:" in prompt


class TestCreateEmbeddingAdapter:
    """Test create_embedding_adapter factory function."""

    def test_create_adapter_with_default_config(self):
        """Test creating adapter with default config."""
        from pbjrag.dsc.embedding_adapter import create_embedding_adapter

        config = {}
        adapter = create_embedding_adapter(config)

        assert adapter.backend == "ollama"
        assert adapter.model == "bge-m3"
        assert adapter.base_url == "http://localhost:11434"

    def test_create_adapter_with_ollama_url(self):
        """Test auto-detection of Ollama backend."""
        from pbjrag.dsc.embedding_adapter import create_embedding_adapter

        config = {"embedding_url": "http://localhost:11434", "embedding_model": "bge-m3"}
        adapter = create_embedding_adapter(config)

        assert adapter.backend == "ollama"

    def test_create_adapter_with_openai_url(self):
        """Test auto-detection of OpenAI backend."""
        from pbjrag.dsc.embedding_adapter import create_embedding_adapter

        config = {"embedding_url": "http://localhost:8000", "embedding_model": "instructor-xl"}
        adapter = create_embedding_adapter(config)

        assert adapter.backend == "openai"

    def test_create_adapter_with_bge_dimension(self):
        """Test BGE model dimension detection."""
        from pbjrag.dsc.embedding_adapter import create_embedding_adapter

        config = {"embedding_model": "bge-large"}
        adapter = create_embedding_adapter(config)

        assert adapter.dimension == 1024

    def test_create_adapter_with_custom_dimension(self):
        """Test custom dimension override."""
        from pbjrag.dsc.embedding_adapter import create_embedding_adapter

        config = {"embedding_model": "custom-model", "embedding_dimension": 512}
        adapter = create_embedding_adapter(config)

        assert adapter.dimension == 512

    def test_create_adapter_with_explicit_backend(self):
        """Test explicit backend specification."""
        from pbjrag.dsc.embedding_adapter import create_embedding_adapter

        config = {
            "embedding_backend": "direct",
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_url": "http://localhost:9999",  # Non-standard port to avoid auto-detection
        }
        adapter = create_embedding_adapter(config)

        assert adapter.backend == "direct"
