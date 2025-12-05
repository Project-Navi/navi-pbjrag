#!/usr/bin/env python3
"""
Flexible embedding adapter that supports multiple backends
including instruction-following models
"""
import logging
from typing import Any, Literal

import numpy as np
import requests

logger = logging.getLogger(__name__)


class EmbeddingAdapter:
    """
    Unified embedding interface supporting multiple backends:
    - Ollama (nomic-embed-text, mxbai-embed-large)
    - OpenAI-compatible APIs (vLLM, text-embeddings-inference)
    - Instructor models (with task instructions)
    - Direct sentence-transformers
    """

    def __init__(
        self,
        backend: Literal["ollama", "openai", "instructor", "direct"] = "ollama",
        model: str = "bge-m3",
        base_url: str = "http://localhost:11434",
        dimension: int = 1024,
    ):
        """
        Initialize embedding adapter

        Args:
            backend: Which backend to use
            model: Model name
            base_url: API base URL
            dimension: Embedding dimension (for fallback)
        """
        self.backend = backend
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.dimension = dimension
        self._warned = False

        # Instruction templates for different tasks
        self.instructions = {
            "search_document": "Represent this code for retrieval:",
            "search_query": "Represent this query for searching code:",
            "clustering": "Represent this code for clustering:",
            "classification": "Represent this code for classification:",
            "semantic": "Represent the semantic meaning:",
            "structural": "Represent the code structure:",
        }

    def embed(
        self,
        text: str,
        task: Literal[
            "search_document", "search_query", "clustering", "classification"
        ] = "search_document",
    ) -> list[float]:
        """
        Get embedding for text with optional task instruction

        Args:
            text: Text to embed
            task: Task type for instruction-following models

        Returns:
            Embedding vector
        """
        if self.backend == "ollama":
            return self._embed_ollama(text, task)
        if self.backend == "openai":
            return self._embed_openai(text, task)
        if self.backend == "instructor":
            return self._embed_instructor(text, task)
        if self.backend == "direct":
            return self._embed_direct(text, task)
        return self._embed_fallback(text)

    def _embed_ollama(self, text: str, task: str) -> list[float]:
        """Embed using Ollama API"""
        try:
            # For models that support instructions
            if self.model in ["nomic-embed-text", "nomic-embed-text:latest"]:
                # Nomic uses prefixes
                if task == "search_document":
                    prompt = f"search_document: {text}"
                elif task == "search_query":
                    prompt = f"search_query: {text}"
                else:
                    prompt = f"{task}: {text}"
            elif "snowflake" in self.model.lower() or "arctic" in self.model.lower():
                # Snowflake Arctic Embed2 - best performing, instruction-aware
                if task == "search_query":
                    prompt = f"Represent this sentence for searching relevant passages: {text}"
                elif task == "search_document":
                    prompt = f"Represent this document for retrieval: {text}"
                else:
                    prompt = text
            elif "bge-m3" in self.model.lower():
                # BGE-M3 can use Instruction format for better performance
                if task == "search_query":
                    prompt = f"Represent this sentence for searching relevant passages: {text}"
                else:
                    prompt = text
            else:
                # For other models, just use the text
                prompt = text

            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": prompt},
                timeout=30,  # Increased timeout for larger models
            )

            if response.status_code == 200:
                return response.json()["embedding"]
            if not self._warned:
                logger.warning(f"Ollama embedding failed: {response.status_code}")
                self._warned = True

        except Exception as e:
            if not self._warned:
                logger.warning(f"Ollama embedding error: {e}")
                self._warned = True

        return self._embed_fallback(text)

    def _embed_openai(self, text: str, task: str) -> list[float]:
        """Embed using OpenAI-compatible API (vLLM, TEI)"""
        try:
            # Build input based on model capabilities
            if "instructor" in self.model.lower() or "e5" in self.model.lower():
                # Models that use instruction prefixes
                instruction = self.instructions.get(task, "")
                input_text = f"{instruction} {text}" if instruction else text
            elif "nomic" in self.model.lower():
                # Nomic style prefixes
                if task == "search_document":
                    input_text = f"search_document: {text}"
                elif task == "search_query":
                    input_text = f"search_query: {text}"
                else:
                    input_text = text
            else:
                input_text = text

            # Use correct endpoint based on service
            if "7997" in self.base_url:  # Infinity
                endpoint = f"{self.base_url}/embeddings"
            else:  # LMStudio and others use /v1/embeddings
                endpoint = f"{self.base_url}/v1/embeddings"

            response = requests.post(
                endpoint,
                json={"input": input_text, "model": self.model},
                timeout=2,
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    if "data" in data and len(data["data"]) > 0:
                        return data["data"][0]["embedding"]
                    logger.error("OpenAI API unexpected response format")
                    return self._embed_fallback(text)
                except KeyError as e:
                    logger.error(f"OpenAI API embedding error: {e}")
                    return self._embed_fallback(text)
            else:
                if not self._warned:
                    logger.warning(f"OpenAI API embedding failed: {response.status_code}")
                    self._warned = True

        except Exception as e:
            if not self._warned:
                logger.warning(f"OpenAI API embedding error: {e}")
                self._warned = True

        return self._embed_fallback(text)

    def _embed_instructor(self, text: str, task: str) -> list[float]:
        """Embed using instructor-style models"""
        # This could use sentence-transformers or a custom API
        instruction = self.instructions.get(task, "Represent this text:")
        return self._embed_openai(f"{instruction} {text}", "search_document")

    def _embed_direct(self, text: str, task: str) -> list[float]:
        """Direct embedding using sentence-transformers (if installed)"""
        try:
            from sentence_transformers import SentenceTransformer

            if not hasattr(self, "_model"):
                self._model = SentenceTransformer(self.model)

            # Handle instruction for compatible models
            if "instructor" in self.model.lower():
                instruction = self.instructions.get(task, "")
                input_text = [[instruction, text]]
            else:
                input_text = text

            embedding = self._model.encode(input_text)
            return embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)

        except ImportError:
            logger.warning("sentence-transformers not installed, using fallback")
            return self._embed_fallback(text)
        except Exception as e:
            logger.warning(f"Direct embedding error: {e}")
            return self._embed_fallback(text)

    def _embed_fallback(self, text: str) -> list[float]:
        """Fallback to random embeddings for testing"""
        if not self._warned:
            logger.warning("Using random embeddings as fallback")
            self._warned = True

        # Generate deterministic pseudo-random embedding based on text
        np.random.seed(hash(text) % 2**32)
        return np.random.rand(self.dimension).tolist()

    def batch_embed(self, texts: list[str], task: str = "search_document") -> list[list[float]]:
        """Embed multiple texts efficiently"""
        # For now, just loop - could optimize with batch APIs
        return [self.embed(text, task) for text in texts]


# Convenience functions
def create_embedding_adapter(config: dict[str, Any]) -> EmbeddingAdapter:
    """Create embedding adapter from config"""

    # Try to auto-detect best backend
    backend = config.get("embedding_backend", "ollama")
    model = config.get("embedding_model", "bge-m3")
    base_url = config.get("embedding_url", "http://localhost:11434")

    # Auto-detect based on URL
    if "11434" in base_url:
        backend = "ollama"
    elif "8000" in base_url or "8080" in base_url:
        backend = "openai"

    # Set dimension based on model
    default_dim = 1024 if "bge" in model.lower() else 768

    return EmbeddingAdapter(
        backend=backend,
        model=model,
        base_url=base_url,
        dimension=config.get("embedding_dimension", default_dim),
    )
