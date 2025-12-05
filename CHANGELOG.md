# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-12-05

### Added
- Initial extraction from Neural-Forge-Bootstrapper as standalone package
- Full 9-dimensional DSC (Differential Symbolic Calculus) analysis framework
- `DSCAnalyzer` for comprehensive file and project analysis
- `DSCCodeChunker` for semantic code chunking with blessing awareness
- `CoreMetrics` for blessing tier calculation (Φ+, Φ~, Φ-)
- `PhaseManager` for 7-phase lifecycle detection and management
- `PatternAnalyzer` for fractal pattern detection across codebases
- `FieldContainer` for managing symbolic field state
- Optional vector store integrations (Qdrant, ChromaDB, Neo4j)
- CLI tool via `pbjrag` command
- Standalone package structure with clean public API
- MIT license for open-source distribution

### Changed
- Import paths now use `pbjrag` instead of `src.neural_forge.pbjrag`
- Simplified public API exports through `__init__.py`
- Dependencies made optional via extras (qdrant, chroma, neo4j, all)
- Configuration system streamlined for standalone usage
- Documentation updated for standalone package context

### Notes
- This is the first standalone release of PBJRAG
- Part of the Project-Navi ecosystem
- Extracted from Neural-Forge-Bootstrapper for broader usability
- Core mathematical foundations preserved from original implementation
