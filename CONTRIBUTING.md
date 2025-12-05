# Contributing to navi-pbjrag

Thank you for your interest in contributing to **navi-pbjrag** (Presence-Based Jurisdictional RAG)! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)

## Code of Conduct

This project adheres to a code of conduct that fosters an open and welcoming environment. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/navi-pbjrag.git
   cd navi-pbjrag
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Project-Navi/navi-pbjrag.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Installation Steps

1. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install optional dependencies** (if needed):
   ```bash
   pip install -e ".[all]"  # Installs Qdrant, ChromaDB, Neo4j
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Verify installation**:
   ```bash
   pytest
   ```

### IDE Setup (VS Code Recommended)

When you open the project in VS Code, you'll be prompted to install recommended extensions. Accept this to get:
- Python language support
- Ruff linting and formatting
- Type checking with Pylance
- Test discovery and execution

## Code Style Guidelines

### Python Style

We follow **PEP 8** with some modifications:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **String quotes**: Use double quotes for strings
- **Import order**: Standard library → Third-party → Local (managed by Ruff)

### Formatting

We use **Black** and **Ruff** for automatic code formatting:

```bash
# Format all code
black src/ tests/

# Run linter
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/
```

### Type Hints

All new code **must include type hints**:

```python
def calculate_metric(data: list[float], threshold: float = 0.5) -> dict[str, float]:
    """Calculate metrics from data.

    Args:
        data: List of numeric values to analyze
        threshold: Minimum threshold for filtering (default: 0.5)

    Returns:
        Dictionary containing calculated metrics

    Raises:
        ValueError: If data is empty or invalid
    """
    if not data:
        raise ValueError("Data cannot be empty")

    return {
        "mean": sum(data) / len(data),
        "max": max(data),
        "min": min(data)
    }
```

### Docstrings

Use **Google-style docstrings** for all public functions, classes, and modules:

```python
def process_code_file(
    file_path: str,
    analysis_depth: int = 9,
    include_metrics: bool = True
) -> dict[str, Any]:
    """Process a code file with Differential Symbolic Calculus analysis.

    This function performs 9-dimensional code analysis using presence-based
    jurisdictional reasoning to extract semantic meaning.

    Args:
        file_path: Path to the source code file
        analysis_depth: Number of DSC dimensions to analyze (1-9)
        include_metrics: Whether to include quantitative metrics

    Returns:
        Dictionary containing:
            - dimensions: List of DSC dimension analysis results
            - metrics: Code quality metrics (if include_metrics=True)
            - embeddings: Semantic embeddings for RAG

    Raises:
        FileNotFoundError: If file_path does not exist
        ValueError: If analysis_depth is not in range 1-9

    Example:
        >>> result = process_code_file("example.py", analysis_depth=9)
        >>> print(result["metrics"]["complexity"])
        7.2
    """
    pass
```

### Error Handling

Always implement proper error handling:

```python
# Good
try:
    result = perform_analysis(data)
    return result
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    return None

# Bad
try:
    result = perform_analysis(data)
    return result
except Exception:
    pass  # Silent failures are bad!
```

## Testing Requirements

### Test Coverage

- **Minimum coverage**: 80% overall
- **New features**: Must include tests with >90% coverage
- **Bug fixes**: Must include regression test

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=pbjrag --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run tests matching pattern
pytest -k "test_analysis"

# Run in verbose mode
pytest -v
```

### Writing Tests

Use **pytest** and follow these conventions:

```python
import pytest
from pbjrag.core import Analyzer

class TestAnalyzer:
    """Test suite for Analyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return Analyzer(dimensions=9)

    def test_analyze_valid_code(self, analyzer):
        """Test analysis with valid Python code."""
        code = "def hello(): return 'world'"
        result = analyzer.analyze(code)

        assert result is not None
        assert "dimensions" in result
        assert len(result["dimensions"]) == 9

    def test_analyze_invalid_code_raises_error(self, analyzer):
        """Test that invalid code raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Python code"):
            analyzer.analyze("invalid python @@#$")

    @pytest.mark.parametrize("depth,expected_dims", [
        (1, 1),
        (5, 5),
        (9, 9),
    ])
    def test_analysis_depth(self, analyzer, depth, expected_dims):
        """Test analysis with different depth settings."""
        result = analyzer.analyze("x = 1", depth=depth)
        assert len(result["dimensions"]) == expected_dims
```

## Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following the guidelines above

4. **Run quality checks**:
   ```bash
   # Format code
   black src/ tests/

   # Check linting
   ruff check src/ tests/

   # Type check
   mypy src/

   # Run tests
   pytest --cov=pbjrag
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new analysis dimension

   - Implement dimension 10 for temporal analysis
   - Add tests with 95% coverage
   - Update documentation

   Closes #123"
   ```

### Commit Message Format

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example**:
```
feat(analyzer): add temporal dimension analysis

Implement dimension 10 for analyzing code evolution over time.
This enhances the presence-based reasoning by incorporating
historical context.

- Add TemporalAnalyzer class
- Integrate with existing DSC pipeline
- Add comprehensive test suite
- Update documentation

Closes #123
```

### Submitting the PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what and why
   - Reference to related issues
   - Screenshots/examples if applicable

3. **PR Checklist**:
   - [ ] Code follows style guidelines
   - [ ] All tests pass
   - [ ] New tests added for new features
   - [ ] Documentation updated
   - [ ] Type hints included
   - [ ] Docstrings added
   - [ ] Changelog updated (if applicable)

### Code Review Process

- Maintainers will review your PR
- Address feedback by pushing new commits
- Once approved, your PR will be merged
- Delete your feature branch after merge

## Project Structure

```
navi-pbjrag/
├── src/pbjrag/           # Main package source code
│   ├── core/             # Core analysis modules
│   ├── dsc/              # Differential Symbolic Calculus
│   ├── rag/              # RAG integration
│   └── utils/            # Utility functions
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test fixtures and data
├── docs/                 # Documentation
├── examples/             # Usage examples
├── webui/                # Web UI components
├── .vscode/              # VS Code configuration
├── pyproject.toml        # Project configuration
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
└── README.md             # Project overview
```

## Development Workflow

### Working on a Feature

1. **Plan your changes** - Discuss in an issue first for large features
2. **Write tests first** (TDD approach recommended)
3. **Implement the feature** with type hints and docstrings
4. **Run tests** frequently during development
5. **Update documentation** as you go
6. **Submit PR** when ready

### Debugging

```bash
# Run tests with debugging
pytest --pdb

# Run specific test with print output
pytest -s tests/test_analyzer.py::test_specific_function

# Run with verbose logging
pytest --log-cli-level=DEBUG
```

### Performance Testing

```bash
# Profile your code
python -m cProfile -o profile.stats your_script.py
python -m pstats profile.stats

# Memory profiling
pip install memory_profiler
python -m memory_profiler your_script.py
```

## Questions or Issues?

- **Bug reports**: Open an issue with detailed reproduction steps
- **Feature requests**: Open an issue describing the use case
- **Questions**: Check existing issues or start a discussion

Thank you for contributing to navi-pbjrag! 🚀
