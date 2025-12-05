"""
Crown Jewel - Core Orchestration Module

The Crown Jewel module manages the analysis pipeline for code quality assessment.
It coordinates phase transitions, calculates quality scores, and orchestrates
multi-stage analysis workflows.

What It Does:
    Crown Jewel orchestrates PBJRAG's code analysis lifecycle. It tracks code
    fragments through 7 phases, calculates EPC quality scores, assigns blessing
    tiers, and coordinates analysis workflows. It also manages field states,
    detects architectural patterns, and handles error recovery.

Core Components:
    - FieldContainer: Stores and manages code fragment field states
    - PhaseManager: Tracks code through 7 lifecycle phases:
      Raw → Analyzed → Chunked → Vectorized → Retrieved → Blessed → Transcendent
    - Orchestrator: Coordinates multi-phase analysis workflows
    - CoreMetrics: Calculates EPC scores and assigns blessing tiers:
      Mundane (0-0.5) → Blessed (0.5-0.7) → Sacred (0.7-0.9) → Transcendent (>0.9)
    - PatternAnalyzer: Detects architectural patterns and code structures
    - ErrorHandler: Manages ambiguity resolution and error recovery

Use Cases:
    - Automated code quality gates in CI/CD pipelines
    - Multi-phase code analysis workflow orchestration
    - Quality trend tracking and reporting
    - Architectural pattern detection
    - Technical debt monitoring

Example Usage:
    >>> from pbjrag.crown_jewel import Orchestrator, PhaseManager, CoreMetrics
    >>>
    >>> # Run complete analysis workflow
    >>> orchestrator = Orchestrator()
    >>> results = orchestrator.run_full_analysis(codebase_path)
    >>>
    >>> # Manage lifecycle phases manually
    >>> phase_mgr = PhaseManager()
    >>> phase_mgr.transition_to_phase("ANALYZED")
    >>> print(f"Current phase: {phase_mgr.current_phase}")
    >>>
    >>> # Calculate quality metrics
    >>> metrics = CoreMetrics()
    >>> epc_score = metrics.calculate_epc(field_state)
    >>> blessing_tier = metrics.assign_blessing_tier(epc_score)
    >>> print(f"Blessing Tier: {blessing_tier}, EPC: {epc_score:.3f}")

Quality Scoring:
    EPC (Efficacy-Purity-Coherence) is calculated as:
    EPC = √((E² + P² + C²) / 3)

    Where E, P, C are normalized scores (0.0-1.0) for:
    - Efficacy: Functional correctness and effectiveness
    - Purity: Code cleanliness and best practices
    - Coherence: Internal consistency and logical structure

    Blessing tiers are assigned based on EPC thresholds:
    - Mundane: EPC < 0.5
    - Blessed: 0.5 ≤ EPC < 0.7
    - Sacred: 0.7 ≤ EPC < 0.9
    - Transcendent: EPC ≥ 0.9
"""

from .error_handler import handle_error, resolve_ambiguity
from .field_container import FieldContainer, create_field
from .metrics import CoreMetrics, create_blessing_vector
from .orchestrator import Orchestrator, run_orchestration
from .pattern_analyzer import PatternAnalyzer, analyze_codebase, detect_patterns
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
