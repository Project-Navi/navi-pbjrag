"""PBJRAG - Semantic Code Analysis via 9-Dimensional Field Theory.

Copyright (c) 2024-2025 Project Navi. All rights reserved.

SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-PNEUL-D-2.2

This software is dual-licensed:
- AGPL-3.0-or-later for open source use
- PNEUL-D v2.2 commercial license (contact legal@projectnavi.ai)

Overview
--------
PBJRAG treats code as a multi-dimensional field evolving through configuration
space, enabling trajectory-based quality assessment. It analyzes code using
9 distinct field dimensions to quantify quality, detect patterns, and guide
refactoring decisions.

The 9 field dimensions are:
    1. **Semantic**: Meaning, purpose, and vocabulary richness
    2. **Emotional**: Developer intent and naming patterns
    3. **Ethical**: Code quality and best practices adherence
    4. **Temporal**: Evolution patterns and change indicators
    5. **Entropic**: Chaos, unpredictability, and cyclomatic complexity
    6. **Rhythmic**: Code flow, cadence, and formatting consistency
    7. **Contradiction**: Internal tensions and complexity pressures
    8. **Relational**: Dependencies and interconnectedness
    9. **Emergent**: Novelty, creativity, and sophisticated patterns

Mathematical Foundation
-----------------------
PBJRAG uses the Emergence Potential Coefficient (EPC) to quantify code quality:

    EPC = sigmoid(geometric_mean([cadence, qualia, entropy])) × relational_modifier

    where relational_modifier = 1.0 - 0.4 × |mean(relational) - 0.5|

Blessing tiers (Φ+, Φ~, Φ-) are assigned based on EPC thresholds:
    - Φ+ (Blessed): EPC ≥ 0.7 - High-quality, well-structured code
    - Φ~ (Mundane): 0.5 ≤ EPC < 0.7 - Acceptable code with room for improvement
    - Φ- (Decay): EPC < 0.5 - Low-quality code requiring refactoring

Phase States
------------
Code evolves through 7 lifecycle phases:
    - **compost** (0.0-0.2): Decay, legacy code, needs refactoring
    - **reflection** (0.2-0.35): Analysis phase, stabilizing
    - **becoming** (0.35-0.5): Transformation, evolving code
    - **stillness** (0.5-0.65): Balanced, stable implementation
    - **turning** (0.65-0.8): Pivoting, architectural shifts
    - **emergent** (0.8-0.9): High-quality, innovative patterns
    - **grinding** (0.9-1.0): Over-optimized, potentially brittle

Quick Start
-----------
Basic analysis:
    >>> from pbjrag import DSCAnalyzer
    >>> analyzer = DSCAnalyzer()
    >>> results = analyzer.analyze_file("my_code.py")
    >>> print(f"Quality: {results['average_epc']:.2f}")

Advanced chunking with field analysis:
    >>> from pbjrag import DSCCodeChunker, DSCChunk, FieldState, BlessingState
    >>> chunker = DSCCodeChunker()
    >>> chunks = chunker.chunk_code(source_code, filepath="example.py")
    >>> for chunk in chunks:
    ...     print(f"Chunk: {chunk.chunk_type}")
    ...     print(f"Blessing: {chunk.blessing.tier}")
    ...     print(f"Phase: {chunk.blessing.phase}")
    ...     print(f"EPC: {chunk.field_state.epc_value:.3f}")

Quality metrics calculation:
    >>> from pbjrag import CoreMetrics, create_blessing_vector
    >>> metrics = CoreMetrics()
    >>> vector = create_blessing_vector(
    ...     cadence=0.7, qualia=0.8, entropy=0.5,
    ...     contradiction=0.3, presence=0.75
    ... )
    >>> print(f"EPC: {vector['epc']:.3f}")
    >>> print(f"Blessing: {vector['Φ']}")

Orchestrated workflow:
    >>> from pbjrag import Orchestrator, PhaseManager
    >>> orchestrator = Orchestrator()
    >>> results = orchestrator.run_full_analysis("./src")
    >>> phase_mgr = PhaseManager()
    >>> print(f"Phase: {phase_mgr.current_phase}")

Pattern detection:
    >>> from pbjrag import PatternAnalyzer
    >>> analyzer = PatternAnalyzer()
    >>> patterns = analyzer.detect_patterns(codebase_path)

Core Classes
------------
DSCAnalyzer
    High-level analysis interface for file and project analysis.
    Coordinates chunking, field calculation, and quality assessment.

DSCCodeChunker
    Low-level chunking with 9-dimensional field analysis.
    Segments source code into semantically meaningful chunks with blessing states.

DSCChunk
    Container for individual code chunk with associated metadata:
    - field_state: 9-dimensional field representation
    - blessing: Quality tier and phase information
    - chunk_type: Structural type (function, class, etc.)
    - content: Raw code text

FieldState
    9-dimensional field representation of code properties.
    Each dimension is a float value between 0.0 and 1.0.

BlessingState
    Quality tier classification and phase tracking:
    - tier: Φ+, Φ~, or Φ- blessing category
    - phase: Current lifecycle phase (compost → grinding)
    - epc: Emergence Potential Coefficient value

CoreMetrics
    EPC and blessing calculations with coherence curve evaluation.
    Provides the mathematical foundation for quality assessment.

Orchestrator
    Coordinates multi-phase analysis workflows.
    Manages the complete analysis pipeline from raw code to blessed output.

PhaseManager
    Tracks code through 7 lifecycle phases.
    Handles phase transitions and state management.

PatternAnalyzer
    Detects architectural patterns and code structures.
    Identifies design patterns, anti-patterns, and complexity hotspots.

Use Cases
---------
- **DevOps**: Automated code quality gates in CI/CD pipelines
- **Development**: Code quality assessment and improvement tracking
- **Research**: Quantitative analysis of software evolution patterns
- **Architecture**: Codebase health monitoring and technical debt detection
- **Refactoring**: Identify high-priority areas for improvement

Project Structure
-----------------
pbjrag/
├── crown_jewel/    # Core orchestration and field management
│   ├── metrics.py           # EPC and blessing calculations
│   ├── orchestrator.py      # Analysis workflow coordination
│   ├── phase_manager.py     # Lifecycle phase tracking
│   ├── field_container.py   # Field state storage
│   └── pattern_analyzer.py  # Pattern detection
├── dsc/            # Differential symbolic calculus engine
│   ├── analyzer.py          # High-level analysis interface
│   ├── chunker.py           # Code chunking with field analysis
│   └── vector_store.py      # Qdrant-native vector storage
└── metrics/        # Quality assessment utilities

For more information, visit: https://github.com/Project-Navi/navi-pbjrag

Version: 3.0.0
"""

__version__ = "3.0.0"

# Core analysis components
# Orchestration and workflow management
# Error handling utilities
from .crown_jewel import (
    CoreMetrics,
    FieldContainer,
    Orchestrator,
    PatternAnalyzer,
    PhaseManager,
    create_blessing_vector,
    create_field,
    handle_error,
    resolve_ambiguity,
)
from .dsc import BlessingState, DSCAnalyzer, DSCChunk, DSCCodeChunker, FieldState

__all__ = [
    # Analysis and chunking
    "DSCAnalyzer",
    "DSCCodeChunker",
    "DSCChunk",
    "FieldState",
    "BlessingState",
    # Orchestration
    "Orchestrator",
    "PhaseManager",
    "PatternAnalyzer",
    # Metrics and quality assessment
    "CoreMetrics",
    "create_blessing_vector",
    # Field management
    "FieldContainer",
    "create_field",
    # Error handling
    "handle_error",
    "resolve_ambiguity",
]
