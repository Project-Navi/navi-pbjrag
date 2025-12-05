#!/usr/bin/env python3
"""
ChromaDB Vector Store for PBJRAG v3

This provides ChromaDB integration as an alternative to Qdrant,
designed to work with MCP Memory Service setups.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import numpy as np

# ChromaDB imports
try:
    import chromadb
    import torch
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions

    HAVE_CHROMA = True
except ImportError:
    HAVE_CHROMA = False
    chromadb = None
    Settings = None
    embedding_functions = None
    torch = None

from ..crown_jewel.field_container import FieldContainer
from ..crown_jewel.phase_manager import PhaseManager
from ..metrics import CoreMetrics
from .chunker import DSCChunk
from .vector_store import DSCEmbeddedChunk, DSCVectorStore

logger = logging.getLogger(__name__)


class DSCChromaStore(DSCVectorStore):
    """
    ChromaDB adapter for DSC Vector Store, designed to work with MCP Memory Service.
    Inherits from DSCVectorStore to maintain API compatibility.
    """

    def __init__(
        self,
        chroma_path: str = "/app/chroma_db",
        collection_name: str = "crown_jewel_dsc",
        embedding_model: str = "all-mpnet-base-v2",
        batch_size: int = 32,
        field_container: Optional[FieldContainer] = None,
        phase_manager: Optional[PhaseManager] = None,
        device: str = "cuda",
    ):

        if not HAVE_CHROMA:
            logger.warning("ChromaDB not available. Vector storage will be limited.")
            self.client = None
            self.collection = None
        else:
            try:
                # Initialize ChromaDB client
                self.client = chromadb.PersistentClient(
                    path=chroma_path,
                    settings=Settings(anonymized_telemetry=False, allow_reset=True),
                )

                # Use the same embedding model as MCP Memory Service
                self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_model,
                    device=device if torch and torch.cuda.is_available() else "cpu",
                )

                logger.info(f"✅ ChromaDB initialized at {chroma_path}")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                self.client = None
                self.collection = None

        self.collection_name = collection_name
        self.batch_size = batch_size
        self.embedding_model = embedding_model
        self.device = device

        # Integration with Crown Jewel Core
        self.field_container = field_container or FieldContainer()
        self.phase_manager = phase_manager or PhaseManager()
        self.metrics = CoreMetrics()

        # ChromaDB doesn't use Infinity, so override these
        self.infinity_url = None
        self.embedding_dim = 768  # Standard for all-mpnet-base-v2

        # Initialize collection if ChromaDB is available
        if self.client:
            self._setup_collection()

    def _setup_collection(self):
        """Create or get ChromaDB collection with DSC-aware schema"""
        try:
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"✅ ChromaDB collection '{self.collection_name}' ready!")
        except Exception as e:
            logger.error(f"Failed to setup ChromaDB collection: {e}")
            self.collection = None

    def _get_embedding(self, text: str, model: str = None) -> List[float]:
        """Get embedding using ChromaDB's embedding function"""
        if not self.collection:
            # Fallback to random if no collection
            return np.random.rand(self.embedding_dim).tolist()

        try:
            # Use ChromaDB's embedding function
            embeddings = self.embedding_function([text])
            return embeddings[0]
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return np.random.rand(self.embedding_dim).tolist()

    def embed_chunk(self, chunk: DSCChunk) -> DSCEmbeddedChunk:
        """Generate embeddings for a DSC chunk using ChromaDB"""

        # For ChromaDB, we'll create a single embedding from all field texts
        # This is different from the multi-vector approach in Qdrant

        # Combine all field representations
        combined_text = f"""
        {chunk.content}

        TYPE: {chunk.chunk_type} PROVIDES: {' '.join(chunk.provides)}
        SEMANTIC: {self._field_to_text(chunk, "semantic")}
        ETHICAL: {self._field_to_text(chunk, "ethical")}
        RELATIONAL: {self._field_to_text(chunk, "relational")}
        PHASE: {self._phase_to_text(chunk)}
        """

        # Get single embedding
        embedding = self._get_embedding(combined_text)

        # For compatibility, create field embeddings too (same embedding)
        field_embeddings = {
            "semantic": embedding,
            "ethical": embedding,
            "relational": embedding,
            "phase": embedding,
        }

        return DSCEmbeddedChunk(chunk=chunk, embedding=embedding, field_embeddings=field_embeddings)

    def index_chunks(self, chunks: List[DSCChunk], batch_size: Optional[int] = None):
        """Index DSC chunks into ChromaDB with Crown Jewel integration"""
        logger.info(f"Indexing {len(chunks)} chunks into ChromaDB...")

        if not self.collection:
            logger.warning("No ChromaDB collection available, using field container only")
            # Still add to field container
            for chunk in chunks:
                fragment = chunk.to_fragment()
                self.field_container.add_fragment(fragment)
            return

        batch_size = batch_size or self.batch_size

        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            # Add to field container
            fragment = chunk.to_fragment()
            self.field_container.add_fragment(fragment)

            # Prepare for ChromaDB
            # Use content as document
            documents.append(chunk.content)

            # Create rich metadata
            metadata = {
                # Basic info
                "chunk_type": chunk.chunk_type,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "provides": json.dumps(chunk.provides),
                "depends_on": json.dumps(chunk.depends_on),
                "file_path": chunk.file_path or "",
                # Blessing state (ChromaDB requires string/number values)
                "blessing_tier": chunk.blessing.tier,
                "blessing_epc": float(chunk.blessing.epc),
                "blessing_ethical": float(chunk.blessing.ethical_alignment),
                "blessing_contradiction": float(chunk.blessing.contradiction_pressure),
                "blessing_presence": float(chunk.blessing.presence_density),
                "blessing_resonance": float(chunk.blessing.resonance_score),
                "blessing_phase": chunk.blessing.phase,
                # Field summaries for filtering
                "semantic_complexity": float(chunk.field_state.semantic[1]),
                "ethical_mean": float(np.mean(chunk.field_state.ethical)),
                "contradiction_mean": float(np.mean(chunk.field_state.contradiction)),
                "temporal_stability": float(chunk.field_state.temporal[2]),
                # Crown Jewel specific
                "current_phase": self.phase_manager.current_phase or "witness",
                "field_coherence": float(self.field_container.field_coherence),
                # Searchable text (for hybrid search)
                "semantic_text": self._field_to_text(chunk, "semantic"),
                "ethical_text": self._field_to_text(chunk, "ethical"),
                "phase_text": self._phase_to_text(chunk),
            }

            metadatas.append(metadata)
            ids.append(f"chunk_{i}_{chunk.chunk_type}_{hash(chunk.content) % 1000000}")

        # Add in batches
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))

            try:
                self.collection.add(
                    documents=documents[i:batch_end],
                    metadatas=metadatas[i:batch_end],
                    ids=ids[i:batch_end],
                )
                logger.info(
                    f"  Indexed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}"
                )
            except Exception as e:
                logger.error(f"Failed to index batch: {e}")

        # Update field coherence after indexing
        self.field_container.calculate_field_coherence()

        logger.info("✅ All chunks indexed into ChromaDB!")

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
        Enhanced search using ChromaDB with Crown Jewel phase and purpose awareness.
        """

        if not self.collection:
            logger.warning("No ChromaDB collection available")
            return self._search_field_container(query, blessing_filter, phase_filter, top_k)

        # Build where clause for ChromaDB
        where_clause = {}

        if blessing_filter:
            where_clause["blessing_tier"] = blessing_filter

        if phase_filter:
            where_clause["blessing_phase"] = {"$in": phase_filter}

        # Add purpose-specific filters
        if purpose:
            if purpose == "stability":
                # Prefer low contradiction, high ethical alignment
                where_clause["$and"] = [
                    {"blessing_contradiction": {"$lte": 0.3}},
                    {"blessing_ethical": {"$gte": 0.7}},
                ]
            elif purpose == "emergence":
                # Prefer emerging phases
                where_clause["blessing_phase"] = {"$in": ["becoming", "turning", "emergent"]}
            elif purpose == "coherence":
                # Prefer high resonance
                where_clause["blessing_resonance"] = {"$gte": 0.7}

        # Perform search
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_clause if where_clause else None,
            )

            # Format results
            formatted = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    metadata = results["metadatas"][0][i]

                    formatted.append(
                        {
                            "id": results["ids"][0][i],
                            "score": 1.0
                            - results["distances"][0][i],  # Convert distance to similarity
                            "content": results["documents"][0][i],
                            "chunk_type": metadata.get("chunk_type", ""),
                            "provides": json.loads(metadata.get("provides", "[]")),
                            "depends_on": json.loads(metadata.get("depends_on", "[]")),
                            "file_path": metadata.get("file_path", ""),
                            "blessing": {
                                "tier": metadata.get("blessing_tier", "Φ-"),
                                "epc": metadata.get("blessing_epc", 0.0),
                                "phase": metadata.get("blessing_phase", "unknown"),
                                "ethical": metadata.get("blessing_ethical", 0.0),
                                "resonance": metadata.get("blessing_resonance", 0.0),
                            },
                            "metrics": {
                                "complexity": metadata.get("semantic_complexity", 0.5),
                                "ethical_mean": metadata.get("ethical_mean", 0.5),
                                "contradiction": metadata.get("contradiction_mean", 0.5),
                            },
                        }
                    )

                    # Add purpose-specific recommendations if requested
                    if purpose:
                        recommendations = self._get_purpose_recommendations(metadata, purpose)
                        formatted[-1]["recommendations"] = recommendations

            return formatted

        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []

    def find_resonant_chunks(
        self, chunk_content: str, min_resonance: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find chunks that resonate with given content using ChromaDB"""

        if not self.collection:
            logger.warning("No ChromaDB collection available")
            return []

        try:
            # Search for similar chunks
            results = self.collection.query(query_texts=[chunk_content], n_results=20)

            resonant_chunks = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    similarity = 1.0 - results["distances"][0][i]

                    if similarity >= min_resonance:
                        metadata = results["metadatas"][0][i]
                        resonant_chunks.append(
                            {
                                "resonance_score": similarity,
                                "id": results["ids"][0][i],
                                "content": results["documents"][0][i],
                                **metadata,
                            }
                        )

            # Add top resonant chunks to capacitor
            if resonant_chunks and self.field_container:
                for chunk in resonant_chunks[:3]:
                    self.field_container.hold_in_capacitor(
                        {"resonant_chunk": chunk},
                        reason=f"High resonance ({chunk['resonance_score']:.2f})",
                    )

            return resonant_chunks

        except Exception as e:
            logger.error(f"Resonance search failed: {e}")
            return []

    def evolve_chunks_by_phase(self, target_phase: str) -> List[Dict[str, Any]]:
        """Find chunks ready to evolve to a target phase using ChromaDB"""

        if not self.collection:
            logger.warning("No ChromaDB collection available")
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

        # Build where clause for ChromaDB
        where_clause = {
            "$and": [
                {"blessing_phase": {"$in": from_phases}},
                {"blessing_epc": {"$gte": min_epc}},
            ]
        }

        try:
            # Get all matching chunks
            results = self.collection.get(where=where_clause, limit=100)

            # Format as evolution candidates
            candidates = []
            if results["ids"]:
                for i in range(len(results["ids"])):
                    metadata = results["metadatas"][i]
                    candidates.append(
                        {
                            "id": results["ids"][i],
                            "content": results["documents"][i],
                            "current_phase": metadata.get("blessing_phase"),
                            "target_phase": target_phase,
                            "epc": metadata.get("blessing_epc", 0.0),
                            "tier": metadata.get("blessing_tier", "Φ-"),
                            "evolution_readiness": self._calculate_evolution_readiness(
                                metadata, target_phase
                            ),
                            **metadata,
                        }
                    )

            # Sort by evolution readiness
            candidates.sort(key=lambda x: x["evolution_readiness"], reverse=True)

            return candidates

        except Exception as e:
            logger.error(f"Evolution search failed: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the ChromaDB collection"""

        if not self.collection:
            return {"error": "No collection available"}

        try:
            # Get collection count
            count = self.collection.count()

            # Sample some documents to get blessing distribution
            sample_size = min(100, count)
            sample = self.collection.get(limit=sample_size) if count > 0 else {"metadatas": []}

            blessing_dist = {"Φ+": 0, "Φ~": 0, "Φ-": 0}
            phase_dist = {}

            for metadata in sample.get("metadatas", []):
                tier = metadata.get("blessing_tier", "Φ-")
                blessing_dist[tier] += 1

                phase = metadata.get("blessing_phase", "unknown")
                phase_dist[phase] = phase_dist.get(phase, 0) + 1

            return {
                "total_chunks": count,
                "blessing_distribution": blessing_dist,
                "phase_distribution": phase_dist,
                "collection_name": self.collection_name,
                "embedding_model": self.embedding_model,
                "chroma_path": (self.client._settings.persist_directory if self.client else None),
            }

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
