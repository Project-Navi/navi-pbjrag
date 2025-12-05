"""
PBJRAG v3: Differential Symbolic Calculus for Code Analysis

A next-generation code analysis framework that understands code as
living, evolving symbolic fields rather than static text.

Translation notes:
- For DevOps: Advanced code quality metrics and analysis
- For researchers: Mathematical field theory applied to software
- For developers: Intelligent code understanding and evolution tracking
"""

__version__ = "3.0.0"

from .crown_jewel import Orchestrator, PhaseManager
# Import main components for easy access
from .dsc import DSCAnalyzer, DSCCodeChunker

# Note: Do NOT import metrics at this level - it should be imported as:
# from pbjrag.crown_jewel import metrics
# or
# from pbjrag.crown_jewel import CoreMetrics, create_blessing_vector

__all__ = [
    "DSCAnalyzer",
    "DSCCodeChunker",
    "PhaseManager",
    "Orchestrator",
]
