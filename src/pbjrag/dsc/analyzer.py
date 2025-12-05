#!/usr/bin/env python3
"""DSC Analyzer - Unified analysis interface integrating PBJRAG-2 with Crown Jewel Core.

This module provides a high-level interface that combines Deep Semantic Chunking (DSC),
vector storage, and Crown Jewel's orchestration capabilities for comprehensive codebase
analysis. The analyzer implements a six-phase workflow following the Crown Jewel
methodology:

1. Witness: Initial file discovery and caching
2. Recognition: Per-file DSC chunking and metric calculation
3. Compost: Identification of low-quality code regions
4. Emergence: Fractal pattern detection across chunks
5. Blessing: Quality tier assignment (Φ+, Φ~, Φ-)
6. Expression: Report generation and recommendations

The analyzer integrates with Qdrant for vector storage and supports semantic search,
resonance detection, and phase-based evolution tracking.

Typical Usage:
    >>> config = {
    ...     "field_dim": 8,
    ...     "enable_vector_store": True,
    ...     "output_dir": "dsc_analysis"
    ... }
    >>> analyzer = DSCAnalyzer(config)
    >>> results = analyzer.analyze_project("/path/to/project", max_depth=3)
    >>> report = analyzer.generate_report()

Mathematical Context:
    Field coherence (Φ-field): Measures alignment between code fragments using
    cosine similarity in embedding space. Coherence ∈ [0, 1] where higher values
    indicate stronger structural and semantic consistency.

    EPC (Emergence Potential Coefficient): Composite metric combining:
    - Structural complexity (AST depth)
    - Dependency strength (imports/references)
    - Documentation quality (docstring presence/length)
    - Error handling robustness (try/except coverage)
"""

import ast
from collections import defaultdict
import json
import logging
import os
from pathlib import Path
from typing import Any

from pbjrag.crown_jewel.field_container import FieldContainer
from pbjrag.crown_jewel.metrics import CoreMetrics
from pbjrag.crown_jewel.orchestrator import Orchestrator
from pbjrag.crown_jewel.pattern_analyzer import PatternAnalyzer
from pbjrag.crown_jewel.phase_manager import PhaseManager

from .chunker import DSCChunk, DSCCodeChunker
from .vector_store import DSCVectorStore

logger = logging.getLogger(__name__)


class DSCAnalyzer:
    """Unified analyzer integrating DSC capabilities with Crown Jewel orchestration.

    This class serves as the main entry point for analyzing codebases using the
    PBJRAG-2 methodology. It coordinates between DSC chunking, vector storage,
    field coherence tracking, and phase-based evolution.

    Attributes:
        config: Configuration dictionary with keys:
            - field_dim: Field dimension for Φ-field calculations (default: 8)
            - enable_vector_store: Enable Qdrant vector storage (default: True)
            - output_dir: Directory for analysis results (default: "dsc_analysis")
            - vector_store: Nested config for Qdrant connection
            - embedding: Nested config for embedding model
        field_container: Manages Φ-field state and fragment storage
        phase_manager: Tracks progression through Crown Jewel phases
        metrics: Calculates EPC, coherence, and blessing metrics
        chunker: DSC code chunker for semantic decomposition
        vector_store: Optional Qdrant vector store for similarity search
        pattern_analyzer: Detects structural and semantic patterns
        output_dir: Path to output directory for results

    Example:
        >>> config = {
        ...     "field_dim": 8,
        ...     "vector_store": {
        ...         "qdrant": {
        ...             "host": "localhost",
        ...             "port": 6333,
        ...             "collection_name": "my_project"
        ...         }
        ...     },
        ...     "embedding": {
        ...         "backend": "ollama",
        ...         "model": "snowflake-arctic-embed2:latest",
        ...         "dimension": 1024
        ...     }
        ... }
        >>> analyzer = DSCAnalyzer(config)
        >>> results = analyzer.analyze_file("src/main.py")
        >>> print(f"Found {results['chunk_count']} chunks")
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the DSC analyzer with optional configuration.

        Args:
            config: Configuration dictionary. If None, uses defaults:
                - field_dim: 8
                - enable_vector_store: True
                - output_dir: "dsc_analysis"
                - vector_store.qdrant.host: "localhost"
                - vector_store.qdrant.port: 6333
                - embedding.backend: "ollama"
                - embedding.model: "snowflake-arctic-embed2:latest"
                - embedding.dimension: 1024

        Example:
            >>> analyzer = DSCAnalyzer()  # Use defaults
            >>> analyzer = DSCAnalyzer({"field_dim": 16})  # Custom field dim
        """
        self.config = config or {}

        # Initialize core components
        self.field_container = FieldContainer(self.config)
        self.phase_manager = PhaseManager(self.config)
        self.metrics = CoreMetrics(self.config)

        # Initialize DSC components with shared field container
        self.chunker = DSCCodeChunker(
            field_dim=self.config.get("field_dim", 8),
            field_container=self.field_container,
        )

        # Initialize vector store if configured (default: enabled)
        self.vector_store = None
        if self.config.get("enable_vector_store", True):  # Default to True
            try:
                # Get nested config values with defaults
                vector_store_cfg = self.config.get("vector_store", {})
                qdrant_cfg = vector_store_cfg.get("qdrant", {})
                embedding_cfg = self.config.get("embedding", {})

                self.vector_store = DSCVectorStore(
                    qdrant_host=qdrant_cfg.get("host", "localhost"),
                    qdrant_port=qdrant_cfg.get("port", 6333),
                    collection_name=qdrant_cfg.get("collection_name", "crown_jewel_dsc"),
                    embedding_backend=embedding_cfg.get("backend", "ollama"),
                    embedding_url=embedding_cfg.get("url", "http://localhost:11434"),
                    embedding_model=embedding_cfg.get("model", "snowflake-arctic-embed2:latest"),
                    embedding_dim=embedding_cfg.get("dimension", 1024),
                    field_container=self.field_container,
                    phase_manager=self.phase_manager,
                )
                # Check if vector store is actually functional
                if self.vector_store.client is None:
                    logger.warning(
                        "Vector store initialization failed. Running without vector storage."
                    )
                    self.vector_store = None
            except Exception as e:
                logger.warning(f"Failed to initialize vector store: {e}")
                logger.warning("Running without vector storage.")
                self.vector_store = None

        # Initialize pattern analyzer
        self.pattern_analyzer = PatternAnalyzer(self.config)

        # Output directory
        self.output_dir = Path(self.config.get("output_dir", "dsc_analysis"))
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # In-memory cache for file contents, as per the "pre-compiled plaintext cache" concept
        self._file_cache: dict[str, str] = {}

    def _populate_file_cache(self, project_path: str, max_depth: int, file_extensions: list[str]):
        """Walk project tree and read all valid files into memory cache (Witness Phase).

        This implements the "Witness" phase of Crown Jewel methodology, where raw
        source files are discovered and cached for subsequent analysis phases.

        Args:
            project_path: Root directory to scan for source files
            max_depth: Maximum directory depth to traverse (0 = root only)
            file_extensions: List of file extensions to include (e.g., [".py", ".js"])

        Example:
            >>> analyzer._populate_file_cache("/path/to/project", max_depth=3,
            ...                               file_extensions=[".py"])
            >>> print(f"Cached {len(analyzer._file_cache)} files")
        """
        logger.info(f"Witness Phase: Caching files from {project_path}")
        self._file_cache.clear()
        for root, dirs, files in os.walk(project_path):
            # Prune directories based on depth
            rel_path = os.path.relpath(root, project_path)
            depth = 0 if rel_path == "." else len(Path(rel_path).parts)
            if depth > max_depth:
                dirs[:] = []  # Stop descending into this branch
                continue

            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = Path(root) / file
                    try:
                        with file_path.open(encoding="utf-8", errors="replace") as f:
                            self._file_cache[str(file_path)] = f.read()
                    except Exception as e:
                        logger.error(f"Error reading file {file_path} into cache: {e}")
        logger.info(f"Witness Phase Complete: Cached {len(self._file_cache)} files.")

    def analyze_file(self, file_path: str) -> dict[str, Any]:
        """Analyze a single file using DSC chunking and Crown Jewel metrics.

        This method implements the Recognition phase for a single file, performing:
        1. DSC chunking to decompose code into semantic units
        2. Pattern analysis using Crown Jewel metrics
        3. Vector indexing for similarity search (if enabled)
        4. File-level metric aggregation
        5. Cross-chunk pattern detection

        Args:
            file_path: Absolute or relative path to source file to analyze

        Returns:
            Dictionary containing:
                - success: bool indicating analysis completion
                - file_path: str path to analyzed file
                - chunks: list[dict] serialized DSCChunk objects
                - chunk_count: int number of chunks extracted
                - patterns: list[dict] detected patterns
                - pattern_count: int number of patterns found
                - file_metrics: dict aggregated metrics
                - field_coherence: float current Φ-field coherence
                - phase: str current Crown Jewel phase

        Raises:
            FileNotFoundError: If file_path does not exist and not in cache
            UnicodeDecodeError: If file cannot be decoded as UTF-8

        Example:
            >>> result = analyzer.analyze_file("src/main.py")
            >>> print(f"Extracted {result['chunk_count']} chunks")
            >>> for chunk in result['chunks']:
            ...     print(f"  {chunk['chunk_type']}: {chunk['provides']}")
        """
        logger.info(f"Analyzing file: {file_path}")

        # Read file content from cache if available, otherwise read from disk
        content = self._file_cache.get(file_path)
        if content is None:
            try:
                with Path(file_path).open(encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    self._file_cache[file_path] = content  # Add to cache if not there
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return {"success": False, "error": str(e), "file_path": file_path}

        # Only transition to witness phase if we're not already in a phase
        # or if we're at the end of a cycle (expression phase)
        if (
            self.phase_manager.current_phase is None
            or self.phase_manager.current_phase == "expression"
        ):
            self.phase_manager.transition_to_phase("witness")
        # Otherwise, we're in the middle of orchestration, so don't change phases

        # Chunk the file using DSC
        chunks = self.chunker.chunk_code(content, file_path)

        # Analyze patterns using Crown Jewel
        file_analysis = self.pattern_analyzer.analyze_file(file_path)

        # Index chunks if vector store is available
        if self.vector_store and chunks:
            self.vector_store.index_chunks(chunks)

        # Calculate file-level metrics
        file_metrics = self._calculate_file_metrics(chunks, file_analysis)

        # The orchestrator is responsible for phase transitions based on analysis.
        # This method's responsibility is just to produce the analysis.

        # Detect patterns across chunks
        patterns = self._detect_chunk_patterns(chunks)

        # Update field coherence
        self.field_container.calculate_field_coherence()

        results = {
            "success": True,
            "file_path": file_path,
            "chunks": [self._chunk_to_dict(chunk) for chunk in chunks],
            "chunk_count": len(chunks),
            "patterns": patterns,
            "pattern_count": len(patterns),
            "file_metrics": file_metrics,
            "field_coherence": self.field_container.field_coherence,
            "phase": self.phase_manager.current_phase,
        }

        # Save results
        self._save_file_results(file_path, results)

        return results

    def analyze_project(
        self,
        project_path: str,
        max_depth: int = 2,
        file_extensions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Analyze entire project using DSC and Crown Jewel orchestration.

        This method executes the complete six-phase Crown Jewel workflow:
        1. Witness: Cache all source files
        2. Recognition: Analyze each file with DSC chunking
        3. Compost: Identify low-quality code regions (Φ- tier)
        4. Emergence: Detect fractal patterns across chunks
        5. Blessing: Assign quality tiers and EPC scores
        6. Expression: Generate comprehensive report

        Args:
            project_path: Root directory of project to analyze
            max_depth: Maximum directory depth to scan (default: 2)
            file_extensions: List of file extensions to include (default: [".py"])

        Returns:
            Dictionary containing:
                - success: bool indicating orchestration completion
                - dsc_analysis: dict with keys:
                    - files_analyzed: int number of files processed
                    - total_chunks: int total chunks extracted
                    - total_patterns: int total patterns detected
                    - compost_candidates: list[dict] low-quality chunks
                    - blessing_distribution: dict tier percentages
                    - phase_distribution: dict phase percentages
                    - field_coherence: float final coherence value
                    - fractal_patterns: dict identified fractal structures
                - orchestration results from Crown Jewel Orchestrator

        Example:
            >>> results = analyzer.analyze_project(
            ...     "/path/to/project",
            ...     max_depth=3,
            ...     file_extensions=[".py", ".js"]
            ... )
            >>> print(f"Analyzed {results['dsc_analysis']['files_analyzed']} files")
            >>> print(f"Field coherence: {results['dsc_analysis']['field_coherence']:.3f}")
        """
        logger.info(f"Analyzing project: {project_path}")

        if file_extensions is None:
            file_extensions = [".py"]

        # Phase 1: Witness - Populate the file cache
        self._populate_file_cache(project_path, max_depth, file_extensions)

        # Create project-specific output directory
        project_name = Path(project_path).name
        project_output_dir = self.output_dir / project_name
        project_output_dir.mkdir(exist_ok=True, parents=True)

        # Configure orchestrator
        orchestrator_config = self.config.copy()
        orchestrator_config.update(
            {
                "project_root": project_path,
                "scan_depth": max_depth,
                "output_dir": str(project_output_dir),
                "purpose": self.config.get("purpose", "coherence"),
            }
        )

        # Create orchestrator with our components
        orchestrator = Orchestrator(orchestrator_config)
        orchestrator.field = self.field_container
        orchestrator.phase_manager = self.phase_manager

        # Run full orchestration
        orchestration_result = orchestrator.run()

        # If orchestration succeeded, enhance with DSC analysis
        if orchestration_result.get("success"):
            # Phase 2: Recognition - Analyze all files from the cache to get raw metrics
            logger.info(f"Recognition Phase: Analyzing {len(self._file_cache)} cached files.")
            dsc_results = []
            all_chunks = []
            for file_path in self._file_cache:
                result = self.analyze_file(file_path)
                dsc_results.append(result)
                # Collect all chunks for later phases
                if result.get("success"):
                    all_chunks.extend(result.get("chunks", []))

            # Phase 3: Compost - Identify problem areas (chunks with low blessing)
            logger.info("Compost Phase: Identifying compost candidates.")
            compost_candidates = []
            for chunk in all_chunks:
                if chunk.get("blessing", {}).get("tier") == "Φ-":
                    compost_candidates.append(
                        {
                            "file_path": chunk.get("file_path"),
                            "chunk_type": chunk.get("chunk_type"),
                            "provides": chunk.get("provides"),
                            "reason": "Low blessing tier (Φ-)",
                        }
                    )
            logger.info(f"Compost Phase Complete: Found {len(compost_candidates)} candidates.")

            # Aggregate DSC results
            total_chunks = len(all_chunks)
            total_patterns = sum(r.get("pattern_count", 0) for r in dsc_results)

            # Calculate project-wide blessing distribution
            blessing_dist = self._calculate_blessing_distribution()
            phase_dist = self._calculate_phase_distribution()

            # Enhance orchestration result with DSC analysis
            orchestration_result["dsc_analysis"] = {
                "files_analyzed": len(dsc_results),
                "total_chunks": total_chunks,
                "total_patterns": total_patterns,
                "compost_candidates": compost_candidates,
                "blessing_distribution": blessing_dist,
                "phase_distribution": phase_dist,
                "field_coherence": self.field_container.field_coherence,
            }

            # Phase 4 & 5: Emergence and Blessing (Fractal Pattern Analysis)
            logger.info("Emergence & Blessing Phases: Analyzing fractal patterns.")
            fractal_patterns = self._identify_fractal_patterns(all_chunks)
            orchestration_result["dsc_analysis"]["fractal_patterns"] = fractal_patterns
            logger.info(f"Identified {len(fractal_patterns)} fractal patterns.")

            # Phase 6: Expression (Final Report)
            # The report generation is implicitly part of the final return,
            # but could be expanded to a dedicated report generator function.

            # Save enhanced results
            results_file = project_output_dir / "dsc_project_analysis.json"
            with results_file.open("w", encoding="utf-8") as f:
                json.dump(orchestration_result, f, indent=2)

            logger.info(f"Project analysis complete. Results saved to {results_file}")

        return orchestration_result

    def search(self, query: str, **kwargs) -> list[dict[str, Any]]:
        """Search analyzed chunks using semantic vector similarity.

        Performs semantic search over indexed chunks using embedding similarity.
        Requires vector_store to be initialized and chunks to have been indexed.

        Args:
            query: Natural language search query
            **kwargs: Additional search parameters passed to DSCVectorStore.search:
                - limit: Maximum number of results (default: 10)
                - score_threshold: Minimum similarity score (default: 0.0)
                - filter: Qdrant filter conditions (default: None)
                - with_payload: Include full chunk metadata (default: True)
                - with_vectors: Include embedding vectors (default: False)

        Returns:
            List of search results, each containing:
                - chunk_id: int unique chunk identifier
                - score: float similarity score ∈ [0, 1]
                - payload: dict chunk metadata and content
                - vector: Optional embedding vector if with_vectors=True

        Example:
            >>> results = analyzer.search("error handling patterns", limit=5)
            >>> for result in results:
            ...     print(f"Score: {result['score']:.3f}")
            ...     print(f"File: {result['payload']['file_path']}")
            ...     print(f"Type: {result['payload']['chunk_type']}")
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []

        return self.vector_store.search(query, **kwargs)

    def find_resonance(self, chunk_id: int, min_resonance: float = 0.7) -> list[dict[str, Any]]:
        """Find chunks that resonate with a given reference chunk.

        Resonance measures semantic and structural similarity between chunks using
        both embedding similarity and blessing metric alignment. High resonance
        indicates chunks that share similar purposes or patterns.

        Mathematical Context:
            Resonance R = α·sim(e₁, e₂) + β·sim(Φ₁, Φ₂)
            where:
            - sim(e₁, e₂) is embedding cosine similarity
            - sim(Φ₁, Φ₂) is blessing vector similarity
            - α, β are weighting factors (typically α=0.7, β=0.3)

        Args:
            chunk_id: ID of reference chunk to find resonance with
            min_resonance: Minimum resonance score threshold ∈ [0, 1] (default: 0.7)

        Returns:
            List of resonant chunks sorted by resonance score, each containing:
                - chunk_id: int unique identifier
                - resonance_score: float resonance value ∈ [0, 1]
                - payload: dict chunk metadata
                - similarity: dict breakdown of similarity components

        Example:
            >>> resonant = analyzer.find_resonance(chunk_id=42, min_resonance=0.75)
            >>> for chunk in resonant:
            ...     print(f"Resonance: {chunk['resonance_score']:.3f}")
            ...     print(f"Chunk: {chunk['payload']['chunk_type']}")
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []

        return self.vector_store.find_resonant_chunks(chunk_id, min_resonance)

    def evolve_by_phase(self, target_phase: str) -> list[dict[str, Any]]:
        """Find chunks ready to evolve to a target Crown Jewel phase.

        Identifies chunks that have sufficient blessing and coherence to transition
        to the specified phase. This supports the Crown Jewel evolution model where
        code progresses through phases: witness → recognition → compost → emergence
        → blessing → expression.

        Args:
            target_phase: Name of target phase to evolve toward. Valid phases:
                - "witness": Initial discovery
                - "recognition": Pattern identification
                - "compost": Transformation candidate
                - "emergence": Novel pattern formation
                - "blessing": Quality validation
                - "expression": Final realization

        Returns:
            List of evolution candidate chunks, each containing:
                - chunk_id: int unique identifier
                - current_phase: str current Crown Jewel phase
                - target_phase: str requested target phase
                - readiness_score: float evolution readiness ∈ [0, 1]
                - blockers: list[str] factors preventing evolution
                - payload: dict chunk metadata

        Example:
            >>> candidates = analyzer.evolve_by_phase("emergence")
            >>> for chunk in candidates:
            ...     if chunk['readiness_score'] > 0.8:
            ...         print(f"Ready: {chunk['payload']['chunk_type']}")
            ...         print(f"Score: {chunk['readiness_score']:.3f}")
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []

        return self.vector_store.evolve_chunks_by_phase(target_phase)

    def _chunk_to_dict(self, chunk: DSCChunk) -> dict[str, Any]:
        """Convert DSCChunk to dictionary for JSON serialization.

        Args:
            chunk: DSCChunk instance to serialize

        Returns:
            Dictionary representation with all chunk attributes serialized

        Example:
            >>> chunk_dict = analyzer._chunk_to_dict(chunk)
            >>> print(chunk_dict.keys())
            dict_keys(['content', 'start_line', 'end_line', 'chunk_type',
                      'provides', 'depends_on', 'file_path', 'blessing',
                      'field_state'])
        """
        return {
            "content": chunk.content,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "chunk_type": chunk.chunk_type,
            "provides": chunk.provides,
            "depends_on": chunk.depends_on,
            "file_path": chunk.file_path,
            "blessing": chunk.blessing.to_dict(),
            "field_state": chunk.field_state.to_dict(),
        }

    def _calculate_file_metrics(
        self, chunks: list[DSCChunk], file_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate aggregated metrics for a file from its chunks.

        Computes file-level statistics by aggregating chunk-level metrics including
        blessing distribution, phase distribution, mean EPC, and field coherence.

        Mathematical Context:
            Mean EPC = (Σ EPC_i) / n for n chunks
            Coherence = cosine_similarity(blessing_vectors) averaged across all pairs

        Args:
            chunks: List of DSCChunk objects representing file decomposition
            file_analysis: Dictionary from Crown Jewel PatternAnalyzer with keys:
                - blessing: dict blessing metrics for file
                - patterns: list detected patterns

        Returns:
            Dictionary containing:
                - chunk_count: int number of chunks in file
                - mean_epc: float average EPC across chunks
                - blessing_distribution: dict {tier: count} for Φ+, Φ~, Φ-
                - phase_distribution: dict {phase: count}
                - coherence: float file coherence score ∈ [0, 1]
                - crown_jewel_metrics: dict file-level Crown Jewel metrics

        Example:
            >>> metrics = analyzer._calculate_file_metrics(chunks, analysis)
            >>> print(f"Mean EPC: {metrics['mean_epc']:.3f}")
            >>> print(f"Φ+ chunks: {metrics['blessing_distribution']['Φ+']}")
        """

        if not chunks:
            return {}

        # Aggregate blessing metrics
        blessing_tiers = [chunk.blessing.tier for chunk in chunks]
        epcs = [chunk.blessing.epc for chunk in chunks]
        phases = [chunk.blessing.phase for chunk in chunks]

        # Calculate blessing distribution
        blessing_counts = {
            "Φ+": 0,
            "Φ~": 0,
            "Φ-": 0,
            "Φ−": 0,
        }  # Support both dash types
        for tier in blessing_tiers:
            if tier == "Φ−":  # Convert Unicode minus to regular dash
                blessing_counts["Φ-"] += 1
            elif tier in blessing_counts:
                blessing_counts[tier] += 1
            else:
                # Fallback for any unexpected tier
                blessing_counts["Φ-"] += 1

        # Calculate phase distribution
        phase_counts = {}
        for phase in phases:
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        # Create coherence vector for all chunks
        chunk_blessings = [chunk.to_fragment()["blessing"] for chunk in chunks]
        coherence = self.metrics.coherence_vector(chunk_blessings)

        # Remove the temporary Unicode key
        if "Φ−" in blessing_counts:
            del blessing_counts["Φ−"]

        return {
            "chunk_count": len(chunks),
            "mean_epc": sum(epcs) / len(epcs) if epcs else 0.0,
            "blessing_distribution": blessing_counts,
            "phase_distribution": phase_counts,
            "coherence": coherence,
            "crown_jewel_metrics": file_analysis.get("blessing", {}),
        }

    def _detect_chunk_patterns(self, chunks: list[DSCChunk]) -> list[dict[str, Any]]:
        """Detect structural and semantic patterns across chunks.

        Identifies three types of patterns:
        1. Blessing tier groups: Clusters of chunks with same quality tier
        2. Phase groups: Clusters of chunks in same Crown Jewel phase
        3. High-resonance pairs: Chunk pairs with resonance > 0.8

        Mathematical Context:
            Resonance between chunks i and j:
            R(i,j) = cosine_sim(embedding_i, embedding_j) × Φ-field_alignment(i,j)

        Args:
            chunks: List of DSCChunk objects to analyze for patterns

        Returns:
            List of pattern dictionaries, each containing:
                - type: str pattern type ("blessing_tier_group", "phase_group",
                       "high_resonance_pair")
                - Additional fields depending on type:
                    For blessing_tier_group:
                        - tier: str blessing tier (Φ+, Φ~, or Φ-)
                        - chunk_count: int chunks in group
                        - mean_epc: float average EPC
                    For phase_group:
                        - phase: str Crown Jewel phase name
                        - chunk_count: int chunks in group
                        - mean_resonance: float average resonance
                    For high_resonance_pair:
                        - chunk1: str identifier
                        - chunk2: str identifier
                        - resonance: float resonance score

        Example:
            >>> patterns = analyzer._detect_chunk_patterns(chunks)
            >>> for pattern in patterns:
            ...     if pattern['type'] == 'blessing_tier_group':
            ...         print(f"{pattern['tier']}: {pattern['chunk_count']} chunks")
        """
        patterns = []

        # Group chunks by blessing tier
        tier_groups = {"Φ+": [], "Φ~": [], "Φ-": []}
        for chunk in chunks:
            tier = chunk.blessing.tier
            if tier == "Φ−":  # Convert Unicode minus to regular dash
                tier = "Φ-"
            if tier not in tier_groups:
                tier = "Φ-"  # Default to negative if unknown
            tier_groups[tier].append(chunk)

        # Create patterns for each tier group
        for tier, group in tier_groups.items():
            if len(group) >= 2:
                pattern = {
                    "type": "blessing_tier_group",
                    "tier": tier,
                    "chunk_count": len(group),
                    "chunks": [c.chunk_type + ":" + ",".join(c.provides) for c in group],
                    "mean_epc": sum(c.blessing.epc for c in group) / len(group),
                }
                patterns.append(pattern)

        # Group chunks by phase
        phase_groups = {}
        for chunk in chunks:
            phase = chunk.blessing.phase
            if phase not in phase_groups:
                phase_groups[phase] = []
            phase_groups[phase].append(chunk)

        # Create patterns for phase groups
        for phase, group in phase_groups.items():
            if len(group) >= 2:
                pattern = {
                    "type": "phase_group",
                    "phase": phase,
                    "chunk_count": len(group),
                    "chunks": [c.chunk_type + ":" + ",".join(c.provides) for c in group],
                    "mean_resonance": sum(c.blessing.resonance_score for c in group) / len(group),
                }
                patterns.append(pattern)

        # Detect high-resonance pairs
        for i, chunk1 in enumerate(chunks):
            for _j, chunk2 in enumerate(chunks[i + 1 :], i + 1):
                resonance = self.chunker.calculate_chunk_resonance(chunk1, chunk2)
                if resonance > 0.8:
                    pattern = {
                        "type": "high_resonance_pair",
                        "chunk1": chunk1.chunk_type + ":" + ",".join(chunk1.provides),
                        "chunk2": chunk2.chunk_type + ":" + ",".join(chunk2.provides),
                        "resonance": resonance,
                    }
                    patterns.append(pattern)

        return patterns

    def _calculate_blessing_distribution(self) -> dict[str, float]:
        """Calculate blessing tier distribution across all analyzed code.

        Computes the percentage of code fragments in each blessing tier (Φ+, Φ~, Φ-)
        across the entire project.

        Mathematical Context:
            Distribution: {tier: n_tier / n_total} for each tier ∈ {Φ+, Φ~, Φ-}
            where n_tier is count of fragments with that tier

        Returns:
            Dictionary mapping blessing tiers to proportions:
                - "Φ+": float proportion of high-quality chunks ∈ [0, 1]
                - "Φ~": float proportion of neutral chunks ∈ [0, 1]
                - "Φ-": float proportion of low-quality chunks ∈ [0, 1]
            Sum of all proportions equals 1.0

        Example:
            >>> dist = analyzer._calculate_blessing_distribution()
            >>> print(f"High quality (Φ+): {dist['Φ+']:.1%}")
            >>> print(f"Neutral (Φ~): {dist['Φ~']:.1%}")
            >>> print(f"Low quality (Φ-): {dist['Φ-']:.1%}")
        """
        fragments = self.field_container.get_fragments()

        if not fragments:
            return {"Φ+": 0.0, "Φ~": 0.0, "Φ-": 0.0}

        counts = {"Φ+": 0, "Φ~": 0, "Φ-": 0}
        for fragment in fragments:
            blessing = fragment.get("blessing", {})
            tier = blessing.get("Φ", "Φ-")
            # Normalize Unicode minus to hyphen-minus
            if tier == "Φ−":
                tier = "Φ-"
            if tier in counts:
                counts[tier] += 1

        total = len(fragments)
        return {tier: count / total for tier, count in counts.items()}

    def _calculate_phase_distribution(self) -> dict[str, float]:
        """Calculate Crown Jewel phase distribution across all analyzed code.

        Computes the percentage of code fragments in each Crown Jewel phase
        across the entire project.

        Returns:
            Dictionary mapping phase names to proportions:
                - Key: str phase name (witness, recognition, compost, emergence,
                      blessing, expression)
                - Value: float proportion of chunks in that phase ∈ [0, 1]
            Sum of all proportions equals 1.0

        Example:
            >>> dist = analyzer._calculate_phase_distribution()
            >>> for phase, proportion in sorted(dist.items(),
            ...                                 key=lambda x: x[1], reverse=True):
            ...     print(f"{phase}: {proportion:.1%}")
        """
        fragments = self.field_container.get_fragments()

        if not fragments:
            return {}

        phase_counts = {}
        for fragment in fragments:
            blessing = fragment.get("dsc_blessing", {})
            phase = blessing.get("phase", "unknown")
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        total = len(fragments)
        return {phase: count / total for phase, count in phase_counts.items()}

    def _save_file_results(self, file_path: str, results: dict[str, Any]):
        """Save analysis results for a file to JSON.

        Args:
            file_path: Path to source file that was analyzed
            results: Analysis results dictionary to serialize

        Example:
            >>> analyzer._save_file_results("src/main.py", results)
            # Saves to dsc_analysis/main_analysis.json
        """
        # Create safe filename
        safe_name = Path(file_path).stem.replace("/", "_").replace("\\", "_")
        results_file = self.output_dir / f"{safe_name}_analysis.json"

        with results_file.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved analysis results to {results_file}")

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive analysis report with recommendations.

        Creates a detailed report summarizing the entire analysis including field
        coherence, blessing distribution, phase progression, top blessed fragments,
        emerging patterns, and actionable recommendations.

        Returns:
            Dictionary containing:
                - timestamp: str ISO format timestamp
                - field_coherence: float overall Φ-field coherence
                - current_phase: str current Crown Jewel phase
                - phase_history: list[dict] phase transition history
                - fragment_count: int total fragments analyzed
                - pattern_count: int total patterns detected
                - blessed_group_count: int number of blessed groups
                - capacitor_count: int items awaiting emergence
                - blessing_distribution: dict tier percentages
                - phase_distribution: dict phase percentages
                - top_blessed_fragments: list[dict] highest EPC fragments
                - emerging_patterns: list[dict] patterns in emergence
                - recommendations: list[str] actionable suggestions

        Example:
            >>> report = analyzer.generate_report()
            >>> print(f"Field coherence: {report['field_coherence']:.3f}")
            >>> print(f"Total fragments: {report['fragment_count']}")
            >>> for rec in report['recommendations']:
            ...     print(f"- {rec}")
        """

        # Calculate field coherence
        field_coherence = self.field_container.calculate_field_coherence()

        # Get current phase
        current_phase = self.phase_manager.current_phase
        phase_history = self.phase_manager.get_phase_history()

        # Get fragments and patterns
        fragments = self.field_container.get_fragments()
        patterns = self.field_container.get_patterns()

        # Calculate distributions
        blessing_dist = self._calculate_blessing_distribution()
        phase_dist = self._calculate_phase_distribution()

        # Get blessed groups
        blessed_groups = self.field_container.get_blessed_groups()

        # Get capacitor items (potential emergences)
        capacitor_items = self.field_container.get_capacitor()

        report = {
            "timestamp": self.field_container.last_pulse.isoformat(),
            "field_coherence": field_coherence,
            "current_phase": current_phase,
            "phase_history": phase_history,
            "fragment_count": len(fragments),
            "pattern_count": len(patterns),
            "blessed_group_count": len(blessed_groups),
            "capacitor_count": len(capacitor_items),
            "blessing_distribution": blessing_dist,
            "phase_distribution": phase_dist,
            "top_blessed_fragments": self._get_top_blessed_fragments(5),
            "emerging_patterns": self._get_emerging_patterns(5),
            "recommendations": self._generate_recommendations(),
        }

        # Save report
        report_file = self.output_dir / "dsc_analysis_report.json"
        with report_file.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Create markdown report
        self._create_markdown_report(report)

        return report

    def _get_top_blessed_fragments(self, n: int) -> list[dict[str, Any]]:
        """Get top N blessed fragments by EPC score.

        Args:
            n: Number of top fragments to return

        Returns:
            List of fragment dictionaries sorted by EPC (highest first)

        Example:
            >>> top = analyzer._get_top_blessed_fragments(5)
            >>> for frag in top:
            ...     print(f"{frag['chunk_type']}: EPC={frag['blessing']['epc']:.3f}")
        """
        fragments = self.field_container.get_fragments()

        # Sort by EPC
        sorted_fragments = sorted(
            fragments, key=lambda f: f.get("blessing", {}).get("epc", 0.0), reverse=True
        )

        return [
            {
                "file": f.get("file", ""),
                "chunk_type": f.get("chunk_type", ""),
                "provides": f.get("provides", []),
                "blessing": f.get("blessing", {}),
            }
            for f in sorted_fragments[:n]
        ]

    def _get_emerging_patterns(self, n: int) -> list[dict[str, Any]]:
        """Get top N emerging patterns by EPC score.

        Filters for patterns in Φ+ or Φ~ tiers with EPC > 0.6, indicating
        high-quality patterns that are actively forming.

        Args:
            n: Number of emerging patterns to return

        Returns:
            List of pattern dictionaries sorted by EPC (highest first)

        Example:
            >>> emerging = analyzer._get_emerging_patterns(5)
            >>> for pattern in emerging:
            ...     print(f"Type: {pattern['type']}, EPC: {pattern['blessing']['epc']:.3f}")
        """
        patterns = self.field_container.get_patterns()

        # Filter for emergence characteristics
        emerging = []
        for pattern in patterns:
            blessing = pattern.get("blessing", {})
            if blessing.get("Φ") in ["Φ+", "Φ~"] and blessing.get("epc", 0) > 0.6:
                emerging.append(pattern)

        # Sort by EPC
        emerging.sort(key=lambda p: p.get("blessing", {}).get("epc", 0.0), reverse=True)

        return emerging[:n]

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations based on analysis results.

        Analyzes blessing distribution, phase distribution, field coherence, and
        capacitor state to produce specific improvement suggestions.

        Returns:
            List of recommendation strings providing actionable guidance

        Example:
            >>> recs = analyzer._generate_recommendations()
            >>> for i, rec in enumerate(recs, 1):
            ...     print(f"{i}. {rec}")
        """
        recommendations = []

        # Get distributions
        blessing_dist = self._calculate_blessing_distribution()
        phase_dist = self._calculate_phase_distribution()

        # Blessing-based recommendations
        if blessing_dist.get("Φ-", 0) > 0.3:
            recommendations.append(
                "High proportion of Φ- chunks. Consider refactoring for better code quality."
            )

        if blessing_dist.get("Φ+", 0) < 0.2:
            recommendations.append(
                "Low proportion of Φ+ chunks. Focus on improving documentation and error handling."
            )

        # Phase-based recommendations
        if phase_dist.get("compost", 0) > 0.2:
            recommendations.append(
                "Significant code in compost phase. Review for potential removal or transformation."
            )

        if phase_dist.get("emergent", 0) > 0.1:
            recommendations.append(
                "Emergent patterns detected. Consider consolidating these into stable patterns."
            )

        # Field coherence recommendations
        if self.field_container.field_coherence < 0.5:
            recommendations.append(
                "Low field coherence. Consider aligning code patterns for better consistency."
            )

        # Capacitor recommendations
        capacitor_count = len(self.field_container.get_capacitor())
        if capacitor_count > 10:
            recommendations.append(
                f"{capacitor_count} items in capacitor. Review for potential emergence."
            )

        return recommendations

    def _create_markdown_report(self, report: dict[str, Any]):
        """Create human-readable markdown version of analysis report.

        Args:
            report: Report dictionary from generate_report()

        Example:
            >>> analyzer._create_markdown_report(report)
            # Creates dsc_analysis/dsc_analysis_report.md
        """
        md_file = self.output_dir / "dsc_analysis_report.md"

        with md_file.open("w", encoding="utf-8") as f:
            f.write("# DSC Analysis Report\n\n")
            f.write(f"**Generated:** {report['timestamp']}\n")
            f.write(f"**Field Coherence:** {report['field_coherence']:.3f}\n")
            f.write(f"**Current Phase:** {report['current_phase']}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Fragments Analyzed:** {report['fragment_count']}\n")
            f.write(f"- **Patterns Detected:** {report['pattern_count']}\n")
            f.write(f"- **Blessed Groups:** {report['blessed_group_count']}\n")
            f.write(f"- **Capacitor Items:** {report['capacitor_count']}\n\n")

            f.write("## Blessing Distribution\n\n")
            for tier, pct in report["blessing_distribution"].items():
                f.write(f"- **{tier}:** {pct:.1%}\n")
            f.write("\n")

            f.write("## Phase Distribution\n\n")
            for phase, pct in sorted(
                report["phase_distribution"].items(), key=lambda x: x[1], reverse=True
            ):
                f.write(f"- **{phase}:** {pct:.1%}\n")
            f.write("\n")

            f.write("## Top Blessed Fragments\n\n")
            for i, fragment in enumerate(report["top_blessed_fragments"], 1):
                blessing = fragment["blessing"]
                f.write(f"{i}. **{fragment['chunk_type']}** - {', '.join(fragment['provides'])}\n")
                f.write(f"   - Blessing: {blessing.get('Φ')} (EPC: {blessing.get('epc', 0):.3f})\n")
            f.write("\n")

            f.write("## Recommendations\n\n")
            for rec in report["recommendations"]:
                f.write(f"- {rec}\n")
            f.write("\n")

            f.write("## Phase History\n\n")
            for entry in report["phase_history"][-10:]:  # Last 10 phases
                f.write(f"- {entry['phase']} ({entry['timestamp']})\n")

        logger.info(f"Created markdown report: {md_file}")

    def _identify_fractal_patterns(
        self, all_chunks: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        """Identify fractal patterns by clustering structurally similar chunks.

        Fractal patterns are repeating structural motifs that appear across different
        code locations. This method uses AST-based structural signatures to identify
        chunks with similar control flow patterns.

        Mathematical Context:
            Structural similarity based on AST node type sequence:
            signature(chunk) = sorted([node_type for node in ast.walk(parse(chunk))])
            Two chunks are structurally similar if signature(chunk1) == signature(chunk2)

        Args:
            all_chunks: List of chunk dictionaries with 'content' and metadata

        Returns:
            Dictionary mapping pattern names to lists of chunk occurrences:
                - Key: str pattern identifier ("pattern_0", "pattern_1", ...)
                - Value: list[dict] chunks matching this pattern, each containing:
                    - file_path: str source file path
                    - provides: list[str] symbols provided by chunk

        Example:
            >>> patterns = analyzer._identify_fractal_patterns(all_chunks)
            >>> for name, occurrences in patterns.items():
            ...     print(f"{name}: {len(occurrences)} occurrences")
            ...     for occ in occurrences[:3]:  # First 3 examples
            ...         print(f"  - {occ['file_path']}: {occ['provides']}")
        """
        patterns = defaultdict(list)

        # Create a simplified structural signature for each chunk
        for chunk in all_chunks:
            structure = []
            try:
                tree = ast.parse(chunk.get("content", ""))
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.For, ast.While, ast.Return, ast.Call)):
                        structure.append(node.__class__.__name__)
                # Create a hashable signature
                chunk["structural_signature"] = tuple(sorted(structure))
            except SyntaxError:
                chunk["structural_signature"] = ()

        # Group chunks by their structural signature
        groups = defaultdict(list)
        for chunk in all_chunks:
            groups[chunk["structural_signature"]].append(chunk)

        # Refine groups into patterns if they have multiple members
        pattern_count = 0
        for _signature, group in groups.items():
            if len(group) > 1:
                pattern_name = f"pattern_{pattern_count}"
                # Further analysis could be done here (e.g., metric similarity)
                # For now, structural similarity is the main driver.
                patterns[pattern_name] = [
                    {"file_path": c.get("file_path"), "provides": c.get("provides")} for c in group
                ]
                pattern_count += 1

        return patterns
