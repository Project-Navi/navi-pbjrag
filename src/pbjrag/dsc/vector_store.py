#!/usr/bin/env python3
"""
DSC Vector Store - Migrated from PBJRAG-2 and integrated with Crown Jewel Core

This integrates the vector storage capabilities with Crown Jewel's field management
and phase-aware retrieval.
"""

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

# Optional dependencies with graceful fallback
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import NamedVector  # noqa: F401
    from qdrant_client.models import QueryRequest  # noqa: F401
    from qdrant_client.models import (
        Distance,
        FieldCondition,
        Filter,
        MatchAny,
        MatchValue,
        OptimizersConfigDiff,
        PointStruct,
        Range,
        VectorParams,
    )

    HAVE_QDRANT = True
except ImportError:
    HAVE_QDRANT = False
    QdrantClient = None  # type: ignore
    # type: ignore
    Distance = VectorParams = PointStruct = Filter = object
    FieldCondition = Range = MatchValue = MatchAny = OptimizersConfigDiff = object

from pbjrag.crown_jewel.field_container import FieldContainer
from pbjrag.crown_jewel.phase_manager import PhaseManager
from pbjrag.metrics import CoreMetrics

from .chunker import DSCChunk
from .embedding_adapter import EmbeddingAdapter

logger = logging.getLogger(__name__)


@dataclass
class DSCEmbeddedChunk:
    """A DSC chunk with embeddings"""

    chunk: DSCChunk
    embedding: list[float]
    field_embeddings: dict[str, list[float]]  # Separate embeddings per field


class DSCVectorStore:
    """
    Enhanced vector store integrated with Crown Jewel Core's field and phase management.
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "crown_jewel_dsc",
        embedding_backend: str = "ollama",
        embedding_url: str = "http://localhost:11434",
        embedding_model: str = "snowflake-arctic-embed2:latest",
        embedding_dim: int = 1024,
        field_container: FieldContainer | None = None,
        phase_manager: PhaseManager | None = None,
    ):
        """
        Initialize DSC Vector Store with Qdrant and embedding support.

        Args:
            qdrant_host: Qdrant server hostname
            qdrant_port: Qdrant server port
            collection_name: Name of Qdrant collection
            embedding_backend: Backend type (ollama, openai, sentence_transformers)
            embedding_url: URL for embedding service
            embedding_model: Model name for embeddings
            embedding_dim: Embedding vector dimension
            field_container: Optional FieldContainer for Crown Jewel integration
            phase_manager: Optional PhaseManager for Crown Jewel integration
        """
        if not HAVE_QDRANT:
            logger.warning("Qdrant client not available. Vector storage will be limited.")
            self.client = None
        else:
            try:
                self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
                # Test connection
                self.client.get_collections()
                logger.info(f"Connected to Qdrant at {qdrant_host}:{qdrant_port}")
            except Exception as e:
                logger.warning(f"Could not connect to Qdrant at {qdrant_host}:{qdrant_port}: {e}")
                logger.warning("Vector storage will be disabled.")
                self.client = None

        self.embedding_url = embedding_url
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim

        # Integration with Crown Jewel Core
        self.field_container = field_container or FieldContainer()
        self.phase_manager = phase_manager or PhaseManager()
        self.metrics = CoreMetrics()

        # Initialize embedding adapter with explicit backend
        self.embedder = EmbeddingAdapter(
            backend=embedding_backend,
            model=embedding_model,
            base_url=embedding_url,
            dimension=embedding_dim,
        )
        logger.info(
            f"Embedding adapter: {embedding_backend} @ {embedding_url} using {embedding_model}"
        )

        # Initialize collection if Qdrant is available
        if self.client:
            self._setup_collection()

    def _setup_collection(self):
        """Create Qdrant collection with DSC-aware schema"""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if exists:
            logger.info(f"Collection '{self.collection_name}' already exists")
            return

        logger.info(f"Creating collection '{self.collection_name}'...")

        # Multiple vectors: main content + field-specific
        vectors_config = {
            "content": VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            # Field-specific vectors for field-aware search
            "semantic": VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            "ethical": VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            "relational": VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            # Crown Jewel specific: phase-aware vector
            "phase": VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
        }

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=vectors_config,
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=10000, memmap_threshold=20000
            ),
        )
        logger.info("✅ Collection created with multi-vector config!")

    def embed_chunk(self, chunk: DSCChunk) -> DSCEmbeddedChunk:
        """Generate embeddings for a DSC chunk using embedding adapter"""

        # Main content embedding
        content_embedding = self.embedder.embed(chunk.content, task="search_document")

        # Field-specific embeddings
        field_embeddings = {}

        # Semantic field: embed a text representation
        semantic_text = self._field_to_text(chunk, "semantic")
        field_embeddings["semantic"] = self.embedder.embed(semantic_text, task="search_document")

        # Ethical field: embed quality indicators
        ethical_text = self._field_to_text(chunk, "ethical")
        field_embeddings["ethical"] = self.embedder.embed(
            ethical_text, task="classification"  # Different task for field type
        )

        # Relational field: embed dependency info
        relational_text = self._field_to_text(chunk, "relational")
        field_embeddings["relational"] = self.embedder.embed(
            relational_text, task="clustering"  # Good for relationships
        )

        # Phase field: embed phase-specific context
        phase_text = self._phase_to_text(chunk)
        field_embeddings["phase"] = self.embedder.embed(phase_text, task="classification")

        return DSCEmbeddedChunk(
            chunk=chunk, embedding=content_embedding, field_embeddings=field_embeddings
        )

    def _field_to_text(self, chunk: DSCChunk, field_name: str) -> str:
        """Convert a field state to searchable text"""
        if field_name == "semantic":
            return (
                f"{chunk.chunk_type} {' '.join(chunk.provides)} "
                f"complexity:{chunk.field_state.semantic[1]:.2f} "
                f"documented:{chunk.field_state.semantic[2]:.2f}"
            )
        if field_name == "ethical":
            return (
                f"ethical_alignment:{chunk.blessing.ethical_alignment:.2f} "
                f"error_handling:{chunk.field_state.ethical[0]:.2f} "
                f"validation:{chunk.field_state.ethical[1]:.2f} "
                f"type_hints:{chunk.field_state.ethical[2]:.2f} "
                f"blessing:{chunk.blessing.tier}"
            )
        if field_name == "relational":
            return (
                f"depends_on:{' '.join(chunk.depends_on)} "
                f"provides:{' '.join(chunk.provides)} "
                f"coupling:{chunk.field_state.relational[2]:.2f}"
            )
        return chunk.content[:200]  # Fallback

    def _phase_to_text(self, chunk: DSCChunk) -> str:
        """Convert phase information to searchable text"""
        return (
            f"phase:{chunk.blessing.phase} "
            f"epc:{chunk.blessing.epc:.2f} "
            f"resonance:{chunk.blessing.resonance_score:.2f} "
            f"tier:{chunk.blessing.tier}"
        )

    def index_chunks(self, chunks: list[DSCChunk], batch_size: int = 100):
        """Index DSC chunks with Crown Jewel integration"""
        logger.info(f"Indexing {len(chunks)} chunks...")

        # Add chunks to field container first
        for chunk in chunks:
            fragment = chunk.to_fragment()
            self.field_container.add_fragment(fragment)

        # If no Qdrant client, skip vector indexing
        if not self.client:
            logger.warning("No Qdrant client available, skipping vector indexing")
            return

        # Generate embeddings
        embedded_chunks = []
        for i, chunk in enumerate(chunks):
            if i % 10 == 0:
                logger.info(f"  Embedding chunk {i+1}/{len(chunks)}...")
            embedded = self.embed_chunk(chunk)
            embedded_chunks.append(embedded)

        # Create points for Qdrant
        points = []
        for i, echunk in enumerate(embedded_chunks):
            chunk = echunk.chunk

            # Multi-vector point
            vectors = {
                "content": echunk.embedding,
                "semantic": echunk.field_embeddings["semantic"],
                "ethical": echunk.field_embeddings["ethical"],
                "relational": echunk.field_embeddings["relational"],
                "phase": echunk.field_embeddings["phase"],
            }

            # Rich metadata payload with Crown Jewel integration
            payload = {
                # Basic info
                "content": chunk.content,
                "chunk_type": chunk.chunk_type,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "provides": chunk.provides,
                "depends_on": chunk.depends_on,
                "file_path": chunk.file_path or "",
                # Blessing state
                "blessing_tier": chunk.blessing.tier,
                "blessing_epc": chunk.blessing.epc,
                "blessing_ethical": chunk.blessing.ethical_alignment,
                "blessing_contradiction": chunk.blessing.contradiction_pressure,
                "blessing_presence": chunk.blessing.presence_density,
                "blessing_resonance": chunk.blessing.resonance_score,
                "blessing_phase": chunk.blessing.phase,
                # Field summaries for filtering
                "semantic_complexity": float(chunk.field_state.semantic[1]),
                "ethical_mean": float(np.mean(chunk.field_state.ethical)),
                "contradiction_mean": float(np.mean(chunk.field_state.contradiction)),
                "temporal_stability": float(chunk.field_state.temporal[2]),
                # Crown Jewel specific
                "current_phase": self.phase_manager.current_phase or "witness",
                "field_coherence": self.field_container.field_coherence,
                # Searchable text versions
                "semantic_text": self._field_to_text(chunk, "semantic"),
                "ethical_text": self._field_to_text(chunk, "ethical"),
                "relational_text": self._field_to_text(chunk, "relational"),
                "phase_text": self._phase_to_text(chunk),
            }

            point = PointStruct(id=i, vector=vectors, payload=payload)
            points.append(point)

            # Upload in batches
            if len(points) >= batch_size:
                self.client.upsert(collection_name=self.collection_name, points=points)
                logger.info(f"  Uploaded {len(points)} points...")
                points = []

        # Upload remaining
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

        # Update field coherence after indexing
        self.field_container.calculate_field_coherence()

        logger.info("✅ All chunks indexed!")

    def search(
        self,
        query: str,
        search_mode: str = "hybrid",
        blessing_filter: str | None = None,
        phase_filter: list[str] | None = None,
        purpose: str | None = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Enhanced search with Crown Jewel phase and purpose awareness.

        Args:
            query: Search query
            search_mode: "content", "semantic", "ethical", "relational", "phase", or "hybrid"
            blessing_filter: Filter by blessing tier (Φ+, Φ~, Φ-)
            phase_filter: Filter by phases
            purpose: Optional purpose context (stability, emergence, coherence, innovation)
            top_k: Number of results
        """

        # If no Qdrant client, search in field container only
        if not self.client:
            return self._search_field_container(query, blessing_filter, phase_filter, top_k)

        # Build filter conditions
        must_conditions = []

        if blessing_filter:
            must_conditions.append(
                FieldCondition(key="blessing_tier", match=MatchValue(value=blessing_filter))
            )

        if phase_filter:
            must_conditions.append(
                FieldCondition(key="blessing_phase", match=MatchAny(any=phase_filter))
            )

        # Add purpose-specific filters
        if purpose:
            if purpose == "stability":
                # Prefer low contradiction, high ethical alignment
                must_conditions.append(
                    FieldCondition(key="blessing_contradiction", range=Range(lte=0.3))
                )
            elif purpose == "emergence":
                # Prefer emerging phases
                must_conditions.append(
                    FieldCondition(
                        key="blessing_phase",
                        match=MatchAny(any=["becoming", "turning", "emergent"]),
                    )
                )
            elif purpose == "coherence":
                # Prefer high resonance
                must_conditions.append(
                    FieldCondition(key="blessing_resonance", range=Range(gte=0.7))
                )

        filter_query = Filter(must=must_conditions) if must_conditions else None

        # Get appropriate embedding using adapter
        if search_mode == "content":
            query_embedding = self.embedder.embed(query, task="search_query")
            vector_name = "content"
        elif search_mode in ["semantic", "ethical", "relational", "phase"]:
            query_embedding = self.embedder.embed(query, task="search_query")
            vector_name = search_mode
        else:  # hybrid
            # Search across multiple vectors
            return self._hybrid_search(query, filter_query, purpose, top_k)

        # Single vector search using query_points (qdrant-client >= 1.7)
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            using=vector_name,
            query_filter=filter_query,
            limit=top_k,
            with_payload=True,
        )

        return self._format_results(results.points, purpose)

    def _search_field_container(
        self,
        query: str,
        blessing_filter: str | None,
        phase_filter: list[str] | None,
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Fallback search in field container when Qdrant is not available"""
        fragments = self.field_container.get_fragments()

        # Filter by blessing
        if blessing_filter:
            fragments = [f for f in fragments if f.get("blessing", {}).get("Φ") == blessing_filter]

        # Filter by phase
        if phase_filter:
            fragments = [
                f for f in fragments if f.get("dsc_blessing", {}).get("phase") in phase_filter
            ]

        # Simple text matching (could be enhanced)
        query_lower = query.lower()
        scored_fragments = []

        for fragment in fragments:
            content = fragment.get("content", "").lower()
            score = content.count(query_lower) / max(len(content.split()), 1)

            if score > 0:
                scored_fragments.append((score, fragment))

        # Sort by score and return top k
        scored_fragments.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, fragment in scored_fragments[:top_k]:
            results.append(
                {
                    "score": score,
                    "content": fragment.get("content", ""),
                    "chunk_type": fragment.get("chunk_type", ""),
                    "provides": fragment.get("provides", []),
                    "depends_on": fragment.get("depends_on", []),
                    "blessing": fragment.get("dsc_blessing", {}),
                    "metrics": {
                        "complexity": fragment.get("semantic_complexity", 0.5),
                        "ethical_mean": fragment.get("ethical_mean", 0.5),
                        "contradiction": fragment.get("contradiction_mean", 0.5),
                    },
                }
            )

        return results

    def _hybrid_search(
        self,
        query: str,
        filter_query: Filter | None,
        purpose: str | None,
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Hybrid search with purpose-aware weighting"""

        # Get embeddings for different aspects
        code_embedding = self.embedder.embed(query, task="search_query")
        text_embedding = self.embedder.embed(query, task="search_query")

        # Adjust weights based on purpose
        if purpose == "stability":
            weights = {
                "content": 0.3,
                "semantic": 0.2,
                "ethical": 0.4,  # Emphasize ethics for stability
                "relational": 0.1,
            }
        elif purpose == "emergence":
            weights = {
                "content": 0.2,
                "semantic": 0.4,  # Emphasize semantics for emergence
                "ethical": 0.2,
                "phase": 0.2,  # Include phase for emergence
            }
        elif purpose == "coherence":
            weights = {
                "content": 0.25,
                "semantic": 0.25,
                "ethical": 0.25,
                "relational": 0.25,  # Balanced for coherence
            }
        else:  # Default weights
            weights = {
                "content": 0.4,
                "semantic": 0.3,
                "ethical": 0.2,
                "relational": 0.1,
            }

        # Search in different vector spaces
        search_configs = []
        if "content" in weights:
            search_configs.append(("content", code_embedding, weights["content"]))
        for vec_name in ["semantic", "ethical", "relational", "phase"]:
            if vec_name in weights:
                search_configs.append((vec_name, text_embedding, weights[vec_name]))

        # Collect results from each vector space
        all_results = {}
        for vector_name, embedding, weight in search_configs:
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                using=vector_name,
                query_filter=filter_query,
                limit=top_k * 2,  # Get more for merging
                with_payload=True,
            )

            for result in response.points:
                point_id = result.id
                if point_id not in all_results:
                    all_results[point_id] = {
                        "payload": result.payload,
                        "scores": {},
                        "weighted_score": 0.0,
                    }
                all_results[point_id]["scores"][vector_name] = result.score
                all_results[point_id]["weighted_score"] += result.score * weight

        # Sort by weighted score
        sorted_results = sorted(
            all_results.items(), key=lambda x: x[1]["weighted_score"], reverse=True
        )[:top_k]

        # Format results
        formatted = []
        for point_id, data in sorted_results:
            payload = data["payload"]
            formatted.append(
                {
                    "id": point_id,
                    "score": data["weighted_score"],
                    "scores_breakdown": data["scores"],
                    "content": payload["content"],
                    "chunk_type": payload["chunk_type"],
                    "provides": payload["provides"],
                    "depends_on": payload["depends_on"],
                    "file_path": payload.get("file_path", ""),
                    "blessing": {
                        "tier": payload["blessing_tier"],
                        "epc": payload["blessing_epc"],
                        "phase": payload["blessing_phase"],
                        "ethical": payload["blessing_ethical"],
                        "resonance": payload["blessing_resonance"],
                    },
                    "metrics": {
                        "complexity": payload["semantic_complexity"],
                        "ethical_mean": payload["ethical_mean"],
                        "contradiction": payload["contradiction_mean"],
                    },
                }
            )

        return formatted

    def _format_results(self, results, purpose: str | None = None) -> list[dict[str, Any]]:
        """Format search results with purpose-aware enhancements"""
        formatted = []

        for result in results:
            payload = result.payload

            # Base result
            result_dict = {
                "id": result.id,
                "score": result.score,
                "content": payload["content"],
                "chunk_type": payload["chunk_type"],
                "provides": payload["provides"],
                "depends_on": payload["depends_on"],
                "file_path": payload.get("file_path", ""),
                "blessing": {
                    "tier": payload["blessing_tier"],
                    "epc": payload["blessing_epc"],
                    "phase": payload["blessing_phase"],
                    "ethical": payload["blessing_ethical"],
                    "resonance": payload["blessing_resonance"],
                },
                "metrics": {
                    "complexity": payload["semantic_complexity"],
                    "ethical_mean": payload["ethical_mean"],
                    "contradiction": payload["contradiction_mean"],
                },
            }

            # Add purpose-specific recommendations
            if purpose:
                recommendations = self._get_purpose_recommendations(payload, purpose)
                result_dict["recommendations"] = recommendations

            formatted.append(result_dict)

        return formatted

    def _get_purpose_recommendations(self, payload: dict[str, Any], purpose: str) -> list[str]:
        """Generate purpose-specific recommendations for a chunk"""
        recommendations = []

        blessing_tier = payload["blessing_tier"]
        phase = payload["blessing_phase"]
        epc = payload["blessing_epc"]

        if purpose == "stability":
            if blessing_tier != "Φ+":
                recommendations.append("Consider improving error handling and documentation")
            if payload["blessing_contradiction"] > 0.5:
                recommendations.append("Reduce complexity to improve stability")

        elif purpose == "emergence":
            if phase in ["compost", "stillness"]:
                recommendations.append("This code may be ready for transformation")
            if epc > 0.7:
                recommendations.append(
                    "High emergence potential - consider as seed for new patterns"
                )

        elif purpose == "coherence":
            if payload["blessing_resonance"] < 0.5:
                recommendations.append("Low resonance - may need alignment with other components")
            if blessing_tier == "Φ-":
                recommendations.append("Improve blessing to enhance field coherence")

        return recommendations

    def find_resonant_chunks(
        self, chunk_id: int, min_resonance: float = 0.7
    ) -> list[dict[str, Any]]:
        """Find chunks that resonate with a given chunk"""

        if not self.client:
            logger.warning("No Qdrant client available for resonance search")
            return []

        # Get the reference chunk
        reference = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[chunk_id],
            with_payload=True,
            with_vectors=True,
        )[0]

        # Search using each vector type
        resonant_chunks = []

        for vector_name in ["semantic", "ethical", "relational", "phase"]:
            if vector_name in reference.vector:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=(vector_name, reference.vector[vector_name]),
                    limit=20,
                    with_payload=True,
                )

                for result in results:
                    if result.id != chunk_id and result.score >= min_resonance:
                        resonant_chunks.append(
                            {
                                "resonance_type": vector_name,
                                "resonance_score": result.score,
                                **result.payload,
                            }
                        )

        # Sort by resonance score
        resonant_chunks.sort(key=lambda x: x["resonance_score"], reverse=True)

        # Add to capacitor for potential emergence
        if resonant_chunks and self.field_container:
            for chunk in resonant_chunks[:3]:  # Top 3 resonant chunks
                self.field_container.hold_in_capacitor(
                    {"resonant_chunk": chunk},
                    reason=f"High resonance ({chunk['resonance_score']:.2f}) with chunk {chunk_id}",
                )

        return resonant_chunks

    def evolve_chunks_by_phase(self, target_phase: str) -> list[dict[str, Any]]:
        """Find chunks ready to evolve to a target phase"""

        if not self.client:
            logger.warning("No Qdrant client available for phase evolution")
            return []

        # Map phases to evolution readiness
        evolution_map = {
            "reflection": {"from": ["compost"], "min_epc": 0.3},
            "becoming": {"from": ["reflection"], "min_epc": 0.4},
            "stillness": {"from": ["becoming"], "min_epc": 0.5},
            "turning": {"from": ["stillness"], "min_epc": 0.65},
            "emergent": {"from": ["turning"], "min_epc": 0.8},
        }

        evolution_config = evolution_map.get(target_phase, {})
        from_phases = evolution_config.get("from", [])
        min_epc = evolution_config.get("min_epc", 0.5)

        if not from_phases:
            return []

        # Find chunks in source phases with sufficient EPC
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(key="blessing_phase", match=MatchAny(any=from_phases)),
                    FieldCondition(key="blessing_epc", range=Range(gte=min_epc)),
                ]
            ),
            limit=100,
            with_payload=True,
        )[0]

        # Format as evolution candidates
        candidates = []
        for result in results:
            candidates.append(
                {
                    "current_phase": result.payload["blessing_phase"],
                    "target_phase": target_phase,
                    "epc": result.payload["blessing_epc"],
                    "tier": result.payload["blessing_tier"],
                    "evolution_readiness": self._calculate_evolution_readiness(
                        result.payload, target_phase
                    ),
                    **result.payload,
                }
            )

        # Sort by evolution readiness
        candidates.sort(key=lambda x: x["evolution_readiness"], reverse=True)

        # Track phase transitions in phase manager
        if candidates and self.phase_manager:
            self.phase_manager.update_phase_data(
                {
                    "evolution_candidates": len(candidates),
                    "target_phase": target_phase,
                    "from_phases": from_phases,
                }
            )

        return candidates

    def _calculate_evolution_readiness(self, payload: dict[str, Any], target_phase: str) -> float:
        """Calculate how ready a chunk is to evolve to target phase"""

        epc = payload["blessing_epc"]
        ethical = payload["blessing_ethical"]

        # Base readiness on EPC
        readiness = epc

        # Adjust based on target phase requirements
        if target_phase == "stillness":
            # Stillness requires ethical alignment
            readiness = readiness * 0.7 + ethical * 0.3
        elif target_phase == "emergent":
            # Emergence requires high EPC and resonance
            resonance = payload.get("blessing_resonance", 0.5)
            readiness = readiness * 0.6 + resonance * 0.4

        return readiness
