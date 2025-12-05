"""
PBJRAG v3: Differential Symbolic Calculus for Code Analysis

Copyright (c) 2024-2025 Project Navi. All rights reserved.

SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-PNEUL-D-2.2

This software is dual-licensed:
- AGPL-3.0-or-later for open source use
- PNEUL-D v2.2 commercial license (contact legal@projectnavi.ai)

PBJRAG is a code analysis framework that applies field theory mathematics to
assess code quality. It treats code as symbolic fields with measurable properties
like coherence, entropy, and quality scores that evolve through a structured
lifecycle.

What It Does:
    PBJRAG analyzes code by modeling it as multi-dimensional field objects.
    Each code fragment receives quality metrics (EPC scores) and progresses
    through 7 phases from raw input to blessed/transcendent status based on
    calculated field properties.

Core Components:
    - DSCAnalyzer: Performs code analysis using symbolic calculus methods
    - DSCCodeChunker: Segments source code into semantically meaningful chunks
    - PhaseManager: Tracks code through 7 lifecycle phases
    - Orchestrator: Coordinates multi-phase analysis pipelines
    - FieldContainer: Stores and manages code fragment field states
    - CoreMetrics: Calculates EPC (Efficacy-Purity-Coherence) quality scores

Use Cases:
    - DevOps: Automated code quality gates in CI/CD pipelines
    - Development: Code quality assessment and improvement tracking
    - Research: Quantitative analysis of software evolution patterns
    - Architecture: Codebase health monitoring and technical debt detection

Example Usage:
    >>> from pbjrag import DSCAnalyzer, DSCCodeChunker
    >>>
    >>> # Analyze code quality
    >>> analyzer = DSCAnalyzer()
    >>> chunks = DSCCodeChunker().chunk_code(source_code)
    >>> results = analyzer.analyze(chunks)
    >>>
    >>> # Access quality metrics
    >>> for chunk in chunks:
    ...     print(f"Blessing Tier: {chunk.blessing_state.tier}")
    ...     print(f"EPC Score: {chunk.field_state.epc_value}")

Project Structure:
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
