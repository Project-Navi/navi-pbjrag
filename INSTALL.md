# Installation Guide - navi-pbjrag

Complete installation guide for **navi-pbjrag v3.0** - Presence-Based Jurisdictional RAG with 9-dimensional code analysis.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.10 or higher (3.10, 3.11, 3.12 supported)
- **OS**: Linux, macOS, Windows (any OS with Python support)
- **Memory**: Minimum 2GB RAM (4GB+ recommended for large codebases)
- **Disk Space**: ~500MB for dependencies

### Required Software
- Python 3.10+ with pip
- Git (for cloning repository)
- (Optional) Docker and Docker Compose for containerized deployment

### Check Python Version
```bash
python --version  # Should show 3.10 or higher
pip --version     # Should be present
```

If Python is not installed or version is too old:
- **Ubuntu/Debian**: `sudo apt install python3.10 python3-pip`
- **macOS**: `brew install python@3.10`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

---

## 🚀 Installation Methods

### Method 1: Quick Install from PyPI (Recommended)

```bash
# Install latest stable release
pip install navi-pbjrag

# Verify installation
pbjrag --version
```

**With optional dependencies:**
```bash
# For Qdrant vector store
pip install navi-pbjrag[qdrant]

# For ChromaDB vector store
pip install navi-pbjrag[chroma]

# For Neo4j graph database
pip install navi-pbjrag[neo4j]

# Install all optional dependencies
pip install navi-pbjrag[all]
```

### Method 2: Editable Install from Source (For Development)

```bash
# Clone repository
git clone https://github.com/Project-Navi/navi-pbjrag.git
cd navi-pbjrag

# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Verify installation
pbjrag --version
```

### Method 3: Install from Source (Without Cloning)

```bash
# Install directly from GitHub
pip install git+https://github.com/Project-Navi/navi-pbjrag.git

# Or from a specific branch/tag
pip install git+https://github.com/Project-Navi/navi-pbjrag.git@v3.0.0
```

### Method 4: Docker Installation (Includes Services)

```bash
# Clone repository
git clone https://github.com/Project-Navi/navi-pbjrag.git
cd navi-pbjrag

# Build and run with Docker Compose
docker-compose up -d

# Access WebUI at http://localhost:8501
# Qdrant UI at http://localhost:6333/dashboard
```

**Docker includes:**
- navi-pbjrag with all dependencies
- Qdrant vector database
- Streamlit WebUI
- Pre-configured services

---

## 🐍 Virtual Environment Setup (Recommended)

Using a virtual environment isolates dependencies and prevents conflicts.

### Using venv (Built-in)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install navi-pbjrag
pip install navi-pbjrag

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n pbjrag python=3.10
conda activate pbjrag

# Install navi-pbjrag
pip install navi-pbjrag

# Deactivate when done
conda deactivate
```

### Using virtualenv

```bash
# Install virtualenv if not present
pip install virtualenv

# Create virtual environment
virtualenv venv

# Activate (Linux/macOS)
source venv/bin/activate
# Or (Windows)
venv\Scripts\activate

# Install navi-pbjrag
pip install navi-pbjrag
```

---

## ✅ Verification Steps

### 1. Check Installation
```bash
# Verify package is installed
pip show navi-pbjrag

# Check CLI is accessible
pbjrag --version

# Should output: navi-pbjrag version 3.0.0
```

### 2. Test Basic Functionality
```bash
# Analyze a simple Python file
echo 'def hello(): return "world"' > test.py
pbjrag analyze test.py

# Should output blessing analysis
```

### 3. Test Optional Dependencies
```bash
# Check what's installed
python -c "import qdrant_client; print('Qdrant: OK')" 2>/dev/null || echo "Qdrant: Not installed"
python -c "import chromadb; print('ChromaDB: OK')" 2>/dev/null || echo "ChromaDB: Not installed"
python -c "import neo4j; print('Neo4j: OK')" 2>/dev/null || echo "Neo4j: Not installed"
```

### 4. Run Example Analysis
```bash
# Clone repository for examples
git clone https://github.com/Project-Navi/navi-pbjrag.git
cd navi-pbjrag/examples/sample_project

# Analyze the sample project
pbjrag analyze . --output-json analysis.json

# View the results
cat analysis.json
```

### 5. Run Tests (Development Installation)
```bash
# Only for editable/dev install
cd navi-pbjrag
pytest tests/
```

---

## 🔧 Advanced Installation Options

### Install Specific Versions
```bash
# Install specific version
pip install navi-pbjrag==3.0.0

# Install version range
pip install "navi-pbjrag>=2.0,<4.0"

# Upgrade to latest
pip install --upgrade navi-pbjrag
```

### Offline Installation
```bash
# Download package and dependencies
pip download navi-pbjrag -d ./packages/

# Install from downloaded packages
pip install --no-index --find-links=./packages/ navi-pbjrag
```

### System-wide vs User Installation
```bash
# User installation (no sudo required)
pip install --user navi-pbjrag

# System-wide installation (requires permissions)
sudo pip install navi-pbjrag  # Not recommended
```

---

## 🌐 WebUI Installation

The Streamlit-based WebUI provides interactive code analysis.

### Install WebUI Dependencies
```bash
# Clone repository
git clone https://github.com/Project-Navi/navi-pbjrag.git
cd navi-pbjrag

# Install WebUI requirements
pip install -r webui/requirements.txt

# Run WebUI
streamlit run webui/app.py
```

**WebUI Features:**
- 📊 Interactive codebase analysis
- 🔍 Chunk visualization with blessing tiers
- 🔎 Semantic search (requires Qdrant)
- 📈 9-dimensional radar charts

---

## 🐳 Docker Deployment Options

### Basic Docker Run
```bash
# Build image
docker build -t navi-pbjrag .

# Run container
docker run -p 8501:8501 -v $(pwd)/data:/app/data navi-pbjrag
```

### Docker Compose with Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Docker Configuration
```bash
# Use custom Dockerfile
docker build -f Dockerfile.dev -t navi-pbjrag:dev .

# Run with environment variables
docker run -e QDRANT_HOST=localhost -e QDRANT_PORT=6333 navi-pbjrag
```

---

## 🛠️ Troubleshooting

### Common Installation Issues

#### Issue: `pip: command not found`
**Solution:**
```bash
# Install pip
python -m ensurepip --upgrade
# Or use package manager
sudo apt install python3-pip  # Ubuntu/Debian
```

#### Issue: `Permission denied` during installation
**Solution:**
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install navi-pbjrag

# Or use user installation
pip install --user navi-pbjrag
```

#### Issue: `Python version too old`
**Solution:**
```bash
# Install Python 3.10+
# Ubuntu/Debian
sudo apt install python3.10
# macOS
brew install python@3.10
# Or use pyenv for version management
pyenv install 3.10.0
pyenv global 3.10.0
```

#### Issue: `ModuleNotFoundError: No module named 'pbjrag'`
**Solution:**
```bash
# Verify installation
pip show navi-pbjrag

# If not installed
pip install navi-pbjrag

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Issue: Optional dependencies not found
**Solution:**
```bash
# Install specific optional dependencies
pip install navi-pbjrag[qdrant]
pip install navi-pbjrag[chroma]
pip install navi-pbjrag[neo4j]

# Or install all
pip install navi-pbjrag[all]
```

#### Issue: Build errors on Windows
**Solution:**
```bash
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or use pre-built wheels
pip install --only-binary :all: navi-pbjrag
```

#### Issue: SSL certificate errors
**Solution:**
```bash
# Temporarily disable SSL verification (not recommended for production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org navi-pbjrag

# Or update certificates
pip install --upgrade certifi
```

#### Issue: Dependency conflicts
**Solution:**
```bash
# Use fresh virtual environment
python -m venv fresh_venv
source fresh_venv/bin/activate
pip install navi-pbjrag

# Or use pip's dependency resolver
pip install --use-feature=fast-deps navi-pbjrag
```

---

## 📦 Dependencies Overview

### Core Dependencies (Always Installed)
- `numpy>=1.24.0` - Numerical computations for DSC
- `requests>=2.28.0` - HTTP client for external services

### Optional Dependencies

**Vector Store Support:**
- `qdrant-client>=1.7.0` - Qdrant vector database client
- `chromadb>=0.4.0` - ChromaDB embedding database

**Graph Database Support:**
- `neo4j>=5.0.0` - Neo4j graph database driver

**Development Tools:**
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `black>=23.0.0` - Code formatter
- `ruff>=0.1.0` - Fast Python linter
- `mypy>=1.0.0` - Static type checker

---

## 🔗 Next Steps

After installation:

1. **Read the Documentation**: `README.md` for feature overview
2. **Try Examples**: Check `examples/` directory
3. **Run WebUI**: `streamlit run webui/app.py`
4. **Analyze Your Code**: `pbjrag analyze /path/to/project`
5. **Explore API**: See `docs/api.md` for programmatic usage

---

## 📚 Additional Resources

- **Homepage**: https://github.com/Project-Navi/navi-pbjrag
- **Documentation**: https://github.com/Project-Navi/navi-pbjrag#readme
- **Issues**: https://github.com/Project-Navi/navi-pbjrag/issues
- **Examples**: https://github.com/Project-Navi/navi-pbjrag/tree/main/examples
- **WebUI Guide**: `README-WEBUI.md`

---

## 💡 Tips

- **Use virtual environments** to avoid dependency conflicts
- **Install optional dependencies** only if you need them (saves space)
- **Use Docker** for production deployments (includes all services)
- **Run tests** after installation to verify everything works
- **Check logs** if something doesn't work: `~/.pbjrag/logs/`

---

*For development setup and contribution guidelines, see `CONTRIBUTING.md` (if available).*
