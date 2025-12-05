"""
PBJRAG v3: Differential Symbolic Calculus for Code Analysis

Copyright (c) 2024-2025 Project Navi. All rights reserved.

SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-PNEUL-D-2.2

This software is dual-licensed:
- AGPL-3.0-or-later for open source use
- PNEUL-D v2.2 commercial license (contact legal@projectnavi.ai)

A next-generation code analysis framework that understands code as living,
evolving symbolic fields rather than static text. PBJRAG combines mathematical
field theory with practical code analysis to provide deep insights into code
quality, evolution, and semantic relationships.

Core Philosophy:
    PBJRAG treats code as multi-dimensional fields that can be analyzed using
    differential calculus principles. Each code fragment exists in a field space
    with properties like coherence, entropy, and blessing state that evolve
    through a 7-phase lifecycle.

Key Components:
    - DSCAnalyzer: Analyzes code through differential symbolic calculus
    - DSCCodeChunker: Intelligently segments code into analyzable chunks
    - PhaseManager: Manages 7-phase lifecycle (Raw → Blessed → Transcendent)
    - Orchestrator: Coordinates multi-phase analysis workflows
    - FieldContainer: Manages code fragment field states and transformations
    - CoreMetrics: Calculates EPC (Efficacy-Purity-Coherence) and blessing tiers

Translation Guide:
    - For DevOps: Advanced code quality metrics with CI/CD integration
    - For Researchers: Mathematical field theory applied to software systems
    - For Developers: Intelligent code understanding and evolution tracking
    - For Architects: Codebase health monitoring and quality assessment

Example Usage:
    >>> from pbjrag import DSCAnalyzer, DSCCodeChunker
    >>>
    >>> # Analyze code quality
    >>> analyzer = DSCAnalyzer()
    >>> chunks = DSCCodeChunker().chunk_code(source_code)
    >>> results = analyzer.analyze(chunks)
    >>>
    >>> # Access blessing states
    >>> for chunk in chunks:
    ...     print(f"Blessing: {chunk.blessing_state.tier}")
    ...     print(f"EPC Score: {chunk.field_state.epc_value}")

Architecture:
    pbjrag/
    ├── crown_jewel/    # Core orchestration and field management
    ├── dsc/            # Differential symbolic calculus engine
    └── metrics/        # Quality assessment and blessing calculations

Version: 3.0.0
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
