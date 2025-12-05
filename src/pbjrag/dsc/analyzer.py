#!/usr/bin/env python3
"""
DSC Analyzer - Unified analysis interface integrating PBJRAG-2 with Crown Jewel Core

This provides a high-level interface that combines DSC chunking, vector storage,
and Crown Jewel's orchestration capabilities.
"""

import ast
import json
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..crown_jewel.field_container import FieldContainer
from ..crown_jewel.metrics import CoreMetrics
from ..crown_jewel.orchestrator import Orchestrator
from ..crown_jewel.pattern_analyzer import PatternAnalyzer
from ..crown_jewel.phase_manager import PhaseManager
from .chunker import DSCChunk, DSCCodeChunker
from .vector_store import DSCVectorStore

logger = logging.getLogger(__name__)


class DSCAnalyzer:
    """
    Unified analyzer that integrates DSC capabilities with Crown Jewel orchestration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the DSC analyzer with optional configuration"""
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
        self._file_cache: Dict[str, str] = {}

    def _populate_file_cache(
        self, project_path: str, max_depth: int, file_extensions: List[str]
    ):
        """Walks the project path and reads all valid files into an in-memory cache."""
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
                    file_path = os.path.join(root, file)
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="replace"
                        ) as f:
                            self._file_cache[file_path] = f.read()
                    except Exception as e:
                        logger.error(f"Error reading file {file_path} into cache: {e}")
        logger.info(f"Witness Phase Complete: Cached {len(self._file_cache)} files.")

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single file using DSC chunking and Crown Jewel metrics.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Analysis results including chunks, patterns, and metrics
        """
        logger.info(f"Analyzing file: {file_path}")

        # Read file content from cache if available, otherwise read from disk
        content = self._file_cache.get(file_path)
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
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
        file_extensions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze an entire project using DSC and Crown Jewel orchestration.

        Args:
            project_path: Root directory of the project
            max_depth: Maximum directory depth to scan
            file_extensions: File extensions to analyze (default: [".py"])

        Returns:
            Complete project analysis results
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
            logger.info(
                f"Recognition Phase: Analyzing {len(self._file_cache)} cached files."
            )
            dsc_results = []
            all_chunks = []
            for file_path in self._file_cache.keys():
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
            logger.info(
                f"Compost Phase Complete: Found {len(compost_candidates)} candidates."
            )

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
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(orchestration_result, f, indent=2)

            logger.info(f"Project analysis complete. Results saved to {results_file}")

        return orchestration_result

    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search analyzed chunks using vector store.

        Args:
            query: Search query
            **kwargs: Additional search parameters (see DSCVectorStore.search)

        Returns:
            Search results
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []

        return self.vector_store.search(query, **kwargs)

    def find_resonance(
        self, chunk_id: int, min_resonance: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find chunks that resonate with a given chunk.

        Args:
            chunk_id: ID of the reference chunk
            min_resonance: Minimum resonance score

        Returns:
            List of resonant chunks
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []

        return self.vector_store.find_resonant_chunks(chunk_id, min_resonance)

    def evolve_by_phase(self, target_phase: str) -> List[Dict[str, Any]]:
        """
        Find chunks ready to evolve to a target phase.

        Args:
            target_phase: Target phase name

        Returns:
            List of evolution candidates
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []

        return self.vector_store.evolve_chunks_by_phase(target_phase)

    def _chunk_to_dict(self, chunk: DSCChunk) -> Dict[str, Any]:
        """Convert a DSCChunk to a dictionary for JSON serialization"""
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
        self, chunks: List[DSCChunk], file_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate aggregated metrics for a file"""

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

    def _detect_chunk_patterns(self, chunks: List[DSCChunk]) -> List[Dict[str, Any]]:
        """Detect patterns across chunks"""
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
                    "chunks": [
                        c.chunk_type + ":" + ",".join(c.provides) for c in group
                    ],
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
                    "chunks": [
                        c.chunk_type + ":" + ",".join(c.provides) for c in group
                    ],
                    "mean_resonance": sum(c.blessing.resonance_score for c in group)
                    / len(group),
                }
                patterns.append(pattern)

        # Detect high-resonance pairs
        for i, chunk1 in enumerate(chunks):
            for j, chunk2 in enumerate(chunks[i + 1 :], i + 1):
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

    def _calculate_blessing_distribution(self) -> Dict[str, float]:
        """Calculate blessing distribution across all analyzed code"""
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

    def _calculate_phase_distribution(self) -> Dict[str, float]:
        """Calculate phase distribution across all analyzed code"""
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

    def _save_file_results(self, file_path: str, results: Dict[str, Any]):
        """Save analysis results for a file"""
        # Create safe filename
        safe_name = Path(file_path).stem.replace("/", "_").replace("\\", "_")
        results_file = self.output_dir / f"{safe_name}_analysis.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved analysis results to {results_file}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analysis report"""

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
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Create markdown report
        self._create_markdown_report(report)

        return report

    def _get_top_blessed_fragments(self, n: int) -> List[Dict[str, Any]]:
        """Get top N blessed fragments"""
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

    def _get_emerging_patterns(self, n: int) -> List[Dict[str, Any]]:
        """Get top N emerging patterns"""
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

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
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

    def _create_markdown_report(self, report: Dict[str, Any]):
        """Create a markdown version of the report"""
        md_file = self.output_dir / "dsc_analysis_report.md"

        with open(md_file, "w", encoding="utf-8") as f:
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
                f.write(
                    f"{i}. **{fragment['chunk_type']}** - {', '.join(fragment['provides'])}\n"
                )
                f.write(
                    f"   - Blessing: {blessing.get('Φ')} (EPC: {blessing.get('epc', 0):.3f})\n"
                )
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
        self, all_chunks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identifies fractal patterns by clustering chunks based on structural
        and metric similarity, inspired by code_fractal_detector.py.
        """
        patterns = defaultdict(list)

        # Create a simplified structural signature for each chunk
        for chunk in all_chunks:
            structure = []
            try:
                tree = ast.parse(chunk.get("content", ""))
                for node in ast.walk(tree):
                    if isinstance(
                        node, (ast.If, ast.For, ast.While, ast.Return, ast.Call)
                    ):
                        structure.append(node.__class__.__name__)
                # Create a hashable signature
                chunk["structural_signature"] = tuple(sorted(structure))
            except SyntaxError:
                chunk["structural_signature"] = tuple()

        # Group chunks by their structural signature
        groups = defaultdict(list)
        for chunk in all_chunks:
            groups[chunk["structural_signature"]].append(chunk)

        # Refine groups into patterns if they have multiple members
        pattern_count = 0
        for signature, group in groups.items():
            if len(group) > 1:
                pattern_name = f"pattern_{pattern_count}"
                # Further analysis could be done here (e.g., metric similarity)
                # For now, structural similarity is the main driver.
                patterns[pattern_name] = [
                    {"file_path": c.get("file_path"), "provides": c.get("provides")}
                    for c in group
                ]
                pattern_count += 1

        return patterns
