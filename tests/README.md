# PBJRAG Test Suite

Comprehensive test suite for the PBJRAG v3 package.

## Test Files

### `conftest.py`
Shared pytest fixtures including:
- `sample_python_code` - Valid Python code samples
- `sample_python_file` - Temporary Python files
- `test_config` - Test configuration dictionaries
- `sample_blessing_vector` - Sample blessing metrics
- `temp_project_dir` - Temporary project directories

### `test_analyzer.py`
Tests for `DSCAnalyzer` - Unified analysis interface

**Tests (8 total):**
- Initialization with/without config
- File analysis returning chunks
- Valid Python code analysis
- Error handling for nonexistent files
- Project-level analysis
- Vector store configuration
- Output directory creation

### `test_chunker.py`
Tests for `DSCCodeChunker` - Code chunking with field analysis

**Tests (10 total):**
- Chunker initialization
- Integration with FieldContainer
- Chunk production from code
- DSCChunk structure validation
- FieldState structure (9 field dimensions)
- BlessingState structure (tier, epc, metrics)
- Serialization to dict/fragment
- Empty code handling
- Chunk type detection

### `test_metrics.py`
Tests for `CoreMetrics` - Blessing calculation and metrics

**Tests (15 total):**
- CoreMetrics initialization
- Blessing vector creation
- Blessing tier calculation (Φ+, Φ~, Φ-)
- Scalar quantization
- Pareto weighting
- Edge cases (zero/max values)
- Metric ranges validation

### `test_phase_manager.py`
Tests for `PhaseManager` - 7-phase lifecycle management

**Tests (13 total):**
- Phase manager initialization
- Valid phase list
- Phase transitions
- Complete phase sequence
- Invalid phase/transition handling
- Phase history tracking
- Cycling back to witness phase
- Configuration support

### `test_optional_deps.py`
Tests for optional dependencies - Feature flags and graceful fallback

**Tests (13 total):**
- HAVE_CHROMA feature flag
- HAVE_QDRANT feature flag
- HAVE_NEO4J feature flag
- ChromaDB import when available
- Graceful fallback without optional deps
- Core functionality without stores
- Import validation

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_analyzer.py

# Run with coverage
pytest tests/ --cov=pbjrag

# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_metrics.py::TestCoreMetrics::test_blessing_tier_calculation_positive
```

## Test Coverage

Total: **56 tests** covering:
- Core analysis pipeline (DSCAnalyzer)
- Code chunking (DSCCodeChunker)
- Field state representation (FieldState)
- Blessing calculations (BlessingState, CoreMetrics)
- Phase management (PhaseManager)
- Optional dependency handling

## Key Test Scenarios

### Edge Cases
- Empty code
- Invalid Python syntax
- Nonexistent files
- Zero/maximum metric values
- Invalid phase transitions

### Integration Points
- FieldContainer integration
- Vector store configuration
- Optional dependency detection
- Phase lifecycle management

### API Validation
- All public classes are importable
- Methods return expected types
- Serialization works correctly
- Error handling is proper

## Dependencies

Required for tests:
- `pytest` - Test framework
- `numpy` - Array operations
- `pbjrag` - Package under test

Optional (for full coverage):
- `pytest-cov` - Coverage reporting
- `chromadb` - ChromaDB integration tests
- `qdrant-client` - Qdrant integration tests
- `neo4j` - Neo4j integration tests

## Notes

- Tests are designed to work WITHOUT optional dependencies
- Vector stores are disabled by default in test config
- All imports should work regardless of optional packages
- Feature flags (HAVE_CHROMA, HAVE_QDRANT, HAVE_NEO4J) are tested for graceful fallback
