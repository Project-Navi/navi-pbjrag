"""
Crown Jewel Core - Orchestration and Field Management

Translation note: Crown Jewel manages the analysis lifecycle
- For DevOps: Think CI/CD pipeline for code quality
- For scholars: Phase-based field evolution system
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
