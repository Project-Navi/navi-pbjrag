"""
Crown Jewel Core - Orchestration and Field Management

The Crown Jewel module provides the mathematical foundation and orchestration
layer for PBJRAG's code analysis system. It manages field states, phase
transitions, and blessing calculations using field theory principles.

Core Concepts:
    - Field Container: Manages code fragments as field objects with properties
      like coherence, entropy, and coupling strength
    - Phase Manager: Orchestrates 7-phase lifecycle transitions:
      Raw → Analyzed → Chunked → Vectorized → Retrieved → Blessed → Transcendent
    - Orchestrator: Coordinates multi-agent analysis workflows across phases
    - Core Metrics: Calculates EPC (Efficacy-Purity-Coherence) scores and
      determines blessing tiers (Mundane → Blessed → Sacred → Transcendent)

Key Components:
    - FieldContainer: Container for code field states and transformations
    - PhaseManager: Manages phase transitions and lifecycle coordination
    - Orchestrator: High-level workflow orchestration and multi-phase analysis
    - CoreMetrics: EPC calculation, blessing tier assignment, quality scoring
    - PatternAnalyzer: Detects architectural patterns and code structures
    - ErrorHandler: Manages ambiguity resolution and error recovery

Translation Guide:
    - For DevOps: CI/CD pipeline for code quality with automated assessments
    - For Researchers: Phase-based field evolution with mathematical rigor
    - For Developers: Automated code quality gates and improvement guidance
    - For Architects: System-level quality orchestration and monitoring

Example Usage:
    >>> from pbjrag.crown_jewel import Orchestrator, PhaseManager, CoreMetrics
    >>>
    >>> # Orchestrate full analysis
    >>> orchestrator = Orchestrator()
    >>> results = orchestrator.run_full_analysis(codebase_path)
    >>>
    >>> # Manage phases manually
    >>> phase_mgr = PhaseManager()
    >>> phase_mgr.transition_to_phase("ANALYZED")
    >>>
    >>> # Calculate blessing metrics
    >>> metrics = CoreMetrics()
    >>> epc_score = metrics.calculate_epc(field_state)
    >>> blessing_tier = metrics.assign_blessing_tier(epc_score)
    >>> print(f"Blessing: {blessing_tier}, EPC: {epc_score:.3f}")

Mathematical Foundation:
    The Crown Jewel system uses field theory to model code quality:
    - EPC = √((E² + P² + C²) / 3)  where E=Efficacy, P=Purity, C=Coherence
    - Blessing tiers based on EPC thresholds: <0.5, 0.5-0.7, 0.7-0.9, >0.9
    - Field coupling strength measures inter-component dependencies
"""

from .error_handler import handle_error, resolve_ambiguity
from .field_container import FieldContainer, create_field
from .metrics import CoreMetrics, create_blessing_vector
from .orchestrator import Orchestrator, run_orchestration
from .pattern_analyzer import (PatternAnalyzer, analyze_codebase,
                               detect_patterns)
from .phase_manager import PhaseManager

__all__ = [
    "CoreMetrics",
    "create_blessing_vector",
    "FieldContainer",
    "create_field",
    "PhaseManager",
    "Orchestrator",
    "run_orchestration",
    "PatternAnalyzer",
    "analyze_codebase",
    "detect_patterns",
    "handle_error",
    "resolve_ambiguity",
]
