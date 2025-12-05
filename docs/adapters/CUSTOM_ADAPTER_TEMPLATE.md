# Custom Vector Store Adapter Template

PBJRAG v3 is **Qdrant-native** - meaning Qdrant is the only actively maintained and tested vector store. However, the architecture supports custom adapters for teams with specific requirements.

## Quick Facts

| Aspect | Details |
|--------|---------|
| Default Store | Qdrant (localhost:6333) |
| Embedding Backend | Ollama (snowflake-arctic-embed2) |
| Collection | `crown_jewel_dsc` |
| Vector Dimensions | 1024 (Arctic) / 768 (mpnet) |

## Why Qdrant-Native?

1. **Multi-vector support** - DSC's 9-dimensional field states require named vectors
2. **Advanced filtering** - Blessing tiers, phases, and purpose-based queries
3. **Performance** - HNSW indexing optimized for high-dimensional semantic search
4. **Hybrid search** - Combined dense + sparse vector retrieval

## Adapter Interface

If you need to implement a custom adapter, your class must extend `DSCVectorStore`:

```python
from typing import Any, Dict, List, Optional
from pbjrag.dsc.vector_store import DSCVectorStore, DSCEmbeddedChunk
from pbjrag.dsc.chunker import DSCChunk
from pbjrag.crown_jewel.field_container import FieldContainer
from pbjrag.crown_jewel.phase_manager import PhaseManager


class MyCustomVectorStore(DSCVectorStore):
    """
    Custom vector store adapter for [Your Database].

    Implements the DSCVectorStore interface for Crown Jewel integration.
    """

    def __init__(
        self,
        # Your connection parameters
        host: str = "localhost",
        port: int = 1234,
        collection_name: str = "crown_jewel_dsc",
        # Crown Jewel integration
        field_container: Optional[FieldContainer] = None,
        phase_manager: Optional[PhaseManager] = None,
    ):
        # Initialize your client
        self.client = self._connect(host, port)
        self.collection_name = collection_name

        # Required Crown Jewel components
        self.field_container = field_container or FieldContainer()
        self.phase_manager = phase_manager or PhaseManager()

        # Setup collection/index
        self._setup_collection()

    def _connect(self, host: str, port: int):
        """Establish connection to your vector database."""
        raise NotImplementedError("Implement connection logic")

    def _setup_collection(self):
        """Create collection with DSC-aware schema."""
        # Must support these metadata fields:
        # - blessing_tier: str ("Φ+", "Φ~", "Φ-")
        # - blessing_phase: str (witness, reflection, becoming, etc.)
        # - blessing_epc: float (0.0 to 1.0)
        # - chunk_type: str (function, class, etc.)
        # - file_path: str
        raise NotImplementedError("Implement collection setup")

    def embed_chunk(self, chunk: DSCChunk) -> DSCEmbeddedChunk:
        """
        Generate embeddings for a DSC chunk.

        CRITICAL: DSC uses 9-dimensional field states. Your adapter should
        either support multi-vector storage or combine fields appropriately.
        """
        # Get embedding for content
        embedding = self._get_embedding(chunk.content)

        # Optional: Create field-specific embeddings for multi-vector search
        field_embeddings = {
            "semantic": self._get_embedding(self._field_to_text(chunk, "semantic")),
            "ethical": self._get_embedding(self._field_to_text(chunk, "ethical")),
            "relational": self._get_embedding(self._field_to_text(chunk, "relational")),
            "phase": self._get_embedding(self._phase_to_text(chunk)),
        }

        return DSCEmbeddedChunk(
            chunk=chunk,
            embedding=embedding,
            field_embeddings=field_embeddings
        )

    def index_chunks(self, chunks: List[DSCChunk], batch_size: Optional[int] = None):
        """
        Index DSC chunks into your vector store.

        MUST:
        1. Add chunks to field_container for Crown Jewel integration
        2. Store blessing metadata for filtering
        3. Update field_coherence after indexing
        """
        for chunk in chunks:
            # Crown Jewel integration - REQUIRED
            fragment = chunk.to_fragment()
            self.field_container.add_fragment(fragment)

            # Your indexing logic here
            embedded = self.embed_chunk(chunk)
            self._store_in_database(embedded)

        # Update coherence - REQUIRED
        self.field_container.calculate_field_coherence()

    def search(
        self,
        query: str,
        search_mode: str = "hybrid",
        blessing_filter: Optional[str] = None,
        phase_filter: Optional[List[str]] = None,
        purpose: Optional[str] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search with Crown Jewel phase and purpose awareness.

        Args:
            query: Search query text
            search_mode: "content", "semantic", "ethical", "hybrid"
            blessing_filter: Filter by tier ("Φ+", "Φ~", "Φ-")
            phase_filter: Filter by phases ["witness", "reflection", ...]
            purpose: Adjust scoring for purpose ("stability", "emergence", "coherence")
            top_k: Number of results

        Returns:
            List of result dicts with required fields:
            - id: str
            - score: float
            - content: str
            - chunk_type: str
            - blessing: dict (tier, phase, epc, etc.)
        """
        raise NotImplementedError("Implement search logic")

    def find_resonant_chunks(
        self,
        chunk_content: str,
        min_resonance: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find chunks that resonate with given content."""
        raise NotImplementedError("Implement resonance search")

    def evolve_chunks_by_phase(self, target_phase: str) -> List[Dict[str, Any]]:
        """Find chunks ready to evolve to target phase."""
        raise NotImplementedError("Implement phase evolution")


# Helper methods inherited from DSCVectorStore:
# - _field_to_text(chunk, field_name) -> str
# - _phase_to_text(chunk) -> str
# - _calculate_evolution_readiness(metadata, target_phase) -> float
# - _get_purpose_recommendations(metadata, purpose) -> List[str]
# - _search_field_container(query, blessing_filter, phase_filter, top_k) -> List[Dict]
```

## Required Metadata Schema

Your vector store must support filtering on these fields:

```python
metadata = {
    # Basic chunk info
    "chunk_type": str,        # "function", "class", "method", etc.
    "file_path": str,         # Source file path
    "start_line": int,
    "end_line": int,
    "provides": List[str],    # Symbols this chunk provides
    "depends_on": List[str],  # Dependencies

    # Blessing state - CRITICAL for DSC
    "blessing_tier": str,     # "Φ+", "Φ~", "Φ-"
    "blessing_epc": float,    # 0.0 to 1.0
    "blessing_phase": str,    # witness, reflection, becoming, stillness, turning, emergent
    "blessing_ethical": float,
    "blessing_resonance": float,

    # Field metrics (optional but recommended)
    "semantic_complexity": float,
    "ethical_mean": float,
    "contradiction_mean": float,
    "temporal_stability": float,
}
```

## Multi-Vector Support (Recommended)

For full DSC functionality, your adapter should support named vectors:

| Vector Name | Purpose | Source |
|-------------|---------|--------|
| `content` | Primary semantic content | chunk.content |
| `semantic` | Complexity/patterns | field_state.semantic |
| `ethical` | Alignment signals | field_state.ethical |
| `relational` | Dependencies | field_state.relational |
| `phase` | Evolution stage | blessing.phase context |

## Testing Your Adapter

Your adapter should pass these test categories:

```bash
# Initialization tests
pytest tests/test_your_adapter.py::TestInit -v

# Indexing tests
pytest tests/test_your_adapter.py::TestIndexing -v

# Search tests with blessing filters
pytest tests/test_your_adapter.py::TestSearch -v

# Phase evolution tests
pytest tests/test_your_adapter.py::TestEvolution -v
```

## Reference Implementation

See `src/pbjrag/dsc/legacy/chroma_store.py` for a complete (archived) implementation using ChromaDB. While no longer maintained, it demonstrates all required interface methods.

## Support

For custom adapter development questions, open an issue on the repository. Note that only Qdrant is officially supported for production use.

---

*PBJRAG v3 - Qdrant Native | Crown Jewel Core*
