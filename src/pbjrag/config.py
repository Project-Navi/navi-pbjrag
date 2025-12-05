#!/usr/bin/env python3
"""PBJRAG Configuration Management.

This module handles configuration loading and validation from multiple sources
with a clear priority order:

1. Default config (config/default.yaml)
2. Custom config file (via PBJRAG_CONFIG env var or --config flag)
3. Environment variables (PBJRAG_<SECTION>_<OPTION>)
4. Runtime overrides (passed to functions)

The module uses Pydantic for validation when available and gracefully falls back
to dictionary-based validation if Pydantic is not installed. All configuration
sections are type-safe with comprehensive validation rules.

Configuration Sections:
    - core: Basic settings (version, field dimension, purpose, output)
    - vector_store: Qdrant vector database settings
    - chroma: ChromaDB configuration (alternative vector store)
    - neo4j: Graph database integration settings
    - embedding: Text embedding model configuration
    - analysis: Analysis behavior and thresholds
    - performance: Resource usage and optimization
    - report: Report generation preferences

Example:
    Basic configuration loading::

        from pbjrag.config import load_config

        config = load_config()
        field_dim = config['core']['field_dim']  # 8
        qdrant_host = config['vector_store']['qdrant']['host']  # 'localhost'

    Using ConfigLoader for nested access::

        from pbjrag.config import get_config

        config = get_config()
        field_dim = config.get('core', 'field_dim')  # 8
        purpose = config.get('core', 'purpose', default='coherence')

    Environment variable override::

        $ export PBJRAG_CORE_FIELD_DIM=16
        $ export QDRANT_HOST=vector-db.example.com
        $ python -c "from pbjrag.config import load_config; print(load_config())"

    Runtime overrides::

        config = load_config(
            config_dict={
                'core': {'purpose': 'stability'},
                'analysis': {'complexity_threshold': 15}
            }
        )

Attributes:
    HAVE_PYDANTIC (bool): Whether Pydantic is available for validation
    HAVE_YAML (bool): Whether PyYAML is available for config file loading
    _global_config (ConfigLoader | None): Singleton global configuration instance
"""

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Optional Pydantic import for validation
try:
    from pydantic import BaseModel, Field, ValidationError

    HAVE_PYDANTIC = True
except ImportError:
    HAVE_PYDANTIC = False
    BaseModel = object  # type: ignore

    def Field(*args, **kwargs):  # noqa: N802
        """Stub for Field decorator when Pydantic is not installed.

        Args:
            *args: Positional arguments (ignored)
            **kwargs: Keyword arguments (ignored)

        Returns:
            None: No-op when Pydantic unavailable
        """
        return

    ValidationError = Exception  # type: ignore

# Optional YAML import
try:
    import yaml

    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False
    yaml = None  # type: ignore


# =============================================================================
# Configuration Schema (Pydantic Models if available)
# =============================================================================

if HAVE_PYDANTIC:

    class CoreConfig(BaseModel):
        """Core configuration settings.

        Defines fundamental PBJRAG behavior including version, field dimension,
        analysis purpose, output location, and logging level.

        Attributes:
            version (str): PBJRAG version string (default: "3.0.0")
            field_dim (int): Dimension of field tensor (4-32, default: 8)
            purpose (str): Analysis purpose - stability, emergence, coherence, or innovation
            output_dir (str): Output directory for results (default: "pbjrag_output")
            log_level (str): Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
            enable_vector_store (bool): Enable Qdrant vector store integration
            enable_neo4j (bool): Enable Neo4j graph database integration
            enable_chroma (bool): Enable ChromaDB vector store integration
        """

        version: str = "3.0.0"
        field_dim: int = Field(default=8, ge=4, le=32)
        purpose: str = Field(
            default="coherence", pattern="^(stability|emergence|coherence|innovation)$"
        )
        output_dir: str = "pbjrag_output"
        log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
        enable_vector_store: bool = True
        enable_neo4j: bool = False
        enable_chroma: bool = False

    class QdrantConfig(BaseModel):
        """Qdrant vector store configuration.

        Settings for connecting to and using Qdrant as the primary vector database
        for semantic search and similarity operations.

        Attributes:
            host (str): Qdrant server hostname (default: "localhost")
            port (int): Qdrant server port (1-65535, default: 6333)
            collection_name (str): Name of Qdrant collection for DSC vectors
            distance (str): Distance metric - cosine, euclidean, or dot
            enable_hnsw (bool): Enable HNSW indexing for faster search
        """

        host: str = "localhost"
        port: int = Field(default=6333, ge=1, le=65535)
        collection_name: str = "crown_jewel_dsc"
        distance: str = Field(default="cosine", pattern="^(cosine|euclidean|dot)$")
        enable_hnsw: bool = True

    class VectorStoreConfig(BaseModel):
        """Vector store configuration.

        Aggregates vector database settings including Qdrant configuration,
        batch processing parameters, and chunking limits.

        Attributes:
            qdrant (QdrantConfig): Qdrant-specific configuration
            batch_size (int): Number of vectors to process per batch (1-256)
            max_chunk_size (int): Maximum size of text chunks for embedding (≥256)
        """

        qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
        batch_size: int = Field(default=32, ge=1, le=256)
        max_chunk_size: int = Field(default=2048, ge=256)

    class ChromaConfig(BaseModel):
        """ChromaDB configuration.

        Alternative vector store using ChromaDB for local-first semantic search
        without requiring a separate database server.

        Attributes:
            path (str): Filesystem path for ChromaDB storage
            collection_name (str): Name of ChromaDB collection
            embedding_model (str): SentenceTransformer model for embeddings
            batch_size (int): Number of embeddings to process per batch (≥1)
        """

        path: str = "/app/chroma_db"
        collection_name: str = "crown_jewel_dsc"
        embedding_model: str = "all-mpnet-base-v2"
        batch_size: int = Field(default=32, ge=1)

    class Neo4jConfig(BaseModel):
        """Neo4j graph store configuration.

        Settings for integrating Neo4j graph database to store and query
        code structure relationships and dependency graphs.

        Attributes:
            uri (str): Neo4j connection URI (bolt://...)
            user (str): Neo4j username
            password (str | None): Neo4j password (None if auth disabled)
            database (str): Neo4j database name
            enable_graph_algorithms (bool): Enable graph algorithm library
        """

        uri: str = "bolt://localhost:7687"
        user: str = "neo4j"
        password: str | None = None
        database: str = "neo4j"
        enable_graph_algorithms: bool = True

    class EmbeddingConfig(BaseModel):
        """Embedding configuration.

        Controls text embedding model selection and behavior for semantic
        vector generation from code and documentation.

        Attributes:
            backend (str): Embedding backend - ollama, openai, or sentence_transformers
            url (str): Backend service URL for remote embedding APIs
            model (str): Specific model name/identifier
            dimension (int | None): Embedding vector dimension (≥128)
            normalize (bool): Normalize vectors to unit length
            enable_cache (bool): Cache embeddings to disk for reuse
            cache_dir (str): Directory for embedding cache storage
        """

        backend: str = Field(default="ollama", pattern="^(ollama|openai|sentence_transformers)$")
        url: str = "http://localhost:11434"
        model: str = "snowflake-arctic-embed2:latest"
        dimension: int | None = Field(default=1024, ge=128)
        normalize: bool = True
        enable_cache: bool = True
        cache_dir: str = ".pbjrag_cache"

    class AnalysisConfig(BaseModel):
        """Analysis configuration.

        Defines analysis behavior including coherence calculation methods,
        blessing tier thresholds, pattern detection, and complexity analysis.

        Attributes:
            coherence_method (str): Method for coherence calculation - standard, weighted, adaptive
            blessing_tiers (dict[str, float]): Thresholds for positive/neutral blessing classification
            enable_pattern_detection (bool): Enable design pattern recognition
            pattern_confidence_threshold (float): Minimum confidence for pattern detection (0-1)
            enable_complexity_analysis (bool): Enable cyclomatic complexity analysis
            complexity_threshold (int): Threshold for flagging high complexity (≥1)
            enable_dependency_analysis (bool): Enable dependency graph analysis
        """

        coherence_method: str = Field(default="standard", pattern="^(standard|weighted|adaptive)$")
        blessing_tiers: dict[str, float] = Field(
            default_factory=lambda: {"positive": 0.7, "neutral": 0.4}
        )
        enable_pattern_detection: bool = True
        pattern_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
        enable_complexity_analysis: bool = True
        complexity_threshold: int = Field(default=10, ge=1)
        enable_dependency_analysis: bool = True

    class PerformanceConfig(BaseModel):
        """Performance configuration.

        Settings for resource usage optimization including parallel processing,
        memory limits, and worker thread management.

        Attributes:
            worker_threads (int): Number of worker threads (0 = auto-detect)
            max_parallel_files (int): Maximum files to analyze in parallel (≥1)
            memory_optimization (bool): Enable memory usage optimization
            max_memory_mb (int): Maximum memory usage in MB (0 = unlimited)
        """

        worker_threads: int = Field(default=0, ge=0)
        max_parallel_files: int = Field(default=4, ge=1)
        memory_optimization: bool = False
        max_memory_mb: int = Field(default=0, ge=0)

    class ReportConfig(BaseModel):
        """Report generation configuration.

        Controls report output format, styling, content inclusion, and
        visualization preferences.

        Attributes:
            format (str): Output format - markdown, json, html, or all
            include_snippets (bool): Include code snippets in reports
            max_snippet_length (int): Maximum length of code snippets (≥50)
            persona (str): Output terminology style - general, devops, or scholar
            include_visualizations (bool): Include charts and graphs in reports
        """

        format: str = Field(default="markdown", pattern="^(markdown|json|html|all)$")
        include_snippets: bool = True
        max_snippet_length: int = Field(default=200, ge=50)
        persona: str = Field(default="general", pattern="^(general|devops|scholar)$")
        include_visualizations: bool = False

    class PBJRAGConfig(BaseModel):
        """Complete PBJRAG configuration.

        Root configuration model aggregating all subsections with proper
        validation and default values.

        Attributes:
            core (CoreConfig): Core system settings
            vector_store (VectorStoreConfig): Vector database configuration
            chroma (ChromaConfig): ChromaDB alternative vector store
            neo4j (Neo4jConfig): Graph database integration
            embedding (EmbeddingConfig): Text embedding settings
            analysis (AnalysisConfig): Analysis behavior configuration
            performance (PerformanceConfig): Resource usage settings
            report (ReportConfig): Report generation preferences

        Example:
            Create validated configuration::

                config_dict = {
                    'core': {'field_dim': 16, 'purpose': 'stability'},
                    'analysis': {'complexity_threshold': 15}
                }

                validated = PBJRAGConfig(**config_dict)
                print(validated.core.field_dim)  # 16
                print(validated.analysis.complexity_threshold)  # 15
        """

        core: CoreConfig = Field(default_factory=CoreConfig)
        vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
        chroma: ChromaConfig = Field(default_factory=ChromaConfig)
        neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)
        embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
        analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
        performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
        report: ReportConfig = Field(default_factory=ReportConfig)

        class Config:
            extra = "allow"  # Allow extra fields for extensibility


# =============================================================================
# Configuration Loader
# =============================================================================


class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded.

    This exception is raised for various configuration problems including
    invalid YAML syntax, missing required files, validation failures, and
    type conversion errors.

    Example:
        >>> try:
        ...     config = load_config(config_file='missing.yaml')
        ... except ConfigurationError as e:
        ...     print(f"Config error: {e}")
        Config error: Configuration file not found: missing.yaml
    """


class ConfigLoader:
    """Loads and validates configuration from multiple sources.

    ConfigLoader implements a priority-based configuration system that merges
    settings from defaults, files, environment variables, and runtime overrides.
    It provides type-safe access to configuration values with optional Pydantic
    validation.

    The configuration priority order (highest to lowest):
        1. Runtime overrides (config_dict parameter)
        2. Environment variables (PBJRAG_* prefix)
        3. Custom config file (via parameter or PBJRAG_CONFIG env var)
        4. Default config (config/default.yaml)

    Attributes:
        _config (dict[str, Any]): Merged configuration dictionary
        _loaded (bool): Whether configuration has been loaded

    Example:
        Basic usage::

            loader = ConfigLoader()
            config = loader.load()

            field_dim = loader.get('core', 'field_dim')
            qdrant_host = loader.get('vector_store', 'qdrant', 'host')

            print(f"Field dimension: {field_dim}")
            print(f"Qdrant host: {qdrant_host}")

        Custom config file::

            loader = ConfigLoader()
            config = loader.load(config_file='custom.yaml')

        Runtime overrides::

            loader = ConfigLoader()
            config = loader.load(
                config_dict={
                    'core': {'purpose': 'stability'},
                    'analysis': {'complexity_threshold': 20}
                }
            )

        Environment variables::

            $ export PBJRAG_CORE_FIELD_DIM=16
            $ export QDRANT_HOST=db.example.com
            $ python
            >>> loader = ConfigLoader()
            >>> config = loader.load()
            >>> print(config['core']['field_dim'])  # 16
    """

    def __init__(self):
        """Initialize ConfigLoader with empty state.

        Creates a new ConfigLoader instance ready to load configuration from
        various sources. No configuration is loaded until load() is called.
        """
        self._config: dict[str, Any] = {}
        self._loaded = False

    def load(
        self,
        config_file: str | Path | None = None,
        config_dict: dict[str, Any] | None = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        """Load configuration from multiple sources.

        Loads and merges configuration from defaults, files, environment variables,
        and runtime overrides according to priority order. Optionally validates
        the final configuration with Pydantic if available.

        Priority order (highest to lowest):
            1. config_dict (runtime overrides)
            2. Environment variables (PBJRAG_*)
            3. config_file (custom config)
            4. Default config (config/default.yaml)

        Args:
            config_file (str | Path | None): Path to custom YAML config file.
                If None, uses PBJRAG_CONFIG environment variable if set.
            config_dict (dict[str, Any] | None): Runtime configuration overrides
                that take highest priority. Useful for programmatic config changes.
            validate (bool): Whether to validate with Pydantic if available.
                Validation provides type safety but requires pydantic package.

        Returns:
            dict[str, Any]: Complete merged configuration dictionary with all
                sections populated and validated.

        Raises:
            ConfigurationError: If configuration is invalid, files cannot be
                loaded, YAML parsing fails, or Pydantic validation fails.

        Examples:
            Load default configuration::

                loader = ConfigLoader()
                config = loader.load()
                print(config['core']['field_dim'])  # 8

            Load with custom file::

                loader = ConfigLoader()
                config = loader.load(config_file='production.yaml')

            Load with runtime overrides::

                loader = ConfigLoader()
                config = loader.load(
                    config_dict={
                        'core': {'purpose': 'stability', 'field_dim': 16},
                        'vector_store': {'qdrant': {'host': 'prod-db.example.com'}}
                    }
                )

            Skip validation::

                loader = ConfigLoader()
                config = loader.load(validate=False)  # Faster, no type checking
        """
        try:
            # 1. Load default config
            default_config = self._load_default_config()

            # 2. Load custom config file if provided
            if config_file is not None:
                custom_config = self._load_yaml_config(config_file)
                default_config = self._deep_merge(default_config, custom_config)

            # 3. Check for PBJRAG_CONFIG environment variable
            env_config_file = os.environ.get("PBJRAG_CONFIG")
            if env_config_file:
                env_file_config = self._load_yaml_config(env_config_file)
                default_config = self._deep_merge(default_config, env_file_config)

            # 4. Override with environment variables
            env_overrides = self._load_env_overrides()
            default_config = self._deep_merge(default_config, env_overrides)

            # 5. Apply runtime overrides
            if config_dict:
                default_config = self._deep_merge(default_config, config_dict)

            # 6. Validate if Pydantic is available
            if validate and HAVE_PYDANTIC:
                try:
                    validated = PBJRAGConfig(**default_config)
                    self._config = validated.model_dump()
                except ValidationError as e:
                    logger.error(f"Configuration validation failed: {e}")
                    raise ConfigurationError(f"Invalid configuration: {e}")
            else:
                self._config = default_config

            self._loaded = True
            return self._config

        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _load_default_config(self) -> dict[str, Any]:
        """Load default configuration from config/default.yaml.

        Attempts to load the default configuration file from the package's
        config directory. Falls back to hardcoded defaults if the file is
        not found or YAML support is unavailable.

        Returns:
            dict[str, Any]: Default configuration dictionary

        Note:
            This method searches for config/default.yaml relative to the
            package installation directory.
        """
        # Try to find config/default.yaml relative to this file
        config_dir = Path(__file__).parent.parent.parent / "config"
        default_config_path = config_dir / "default.yaml"

        if default_config_path.exists() and HAVE_YAML:
            return self._load_yaml_config(default_config_path)

        # Fallback to hardcoded defaults if YAML not available
        logger.warning("Could not load default.yaml, using hardcoded defaults")
        return self._get_hardcoded_defaults()

    def _load_yaml_config(self, path: str | Path) -> dict[str, Any]:
        """Load configuration from YAML file.

        Reads and parses a YAML configuration file with error handling for
        missing files and invalid YAML syntax.

        Args:
            path (str | Path): Path to YAML configuration file

        Returns:
            dict[str, Any]: Parsed configuration dictionary

        Raises:
            ConfigurationError: If YAML support is not available, file is not
                found, or YAML parsing fails
        """
        if not HAVE_YAML:
            raise ConfigurationError("YAML support not available. Install with: pip install pyyaml")

        path = Path(path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")

        try:
            with path.open(encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ConfigurationError(
                        f"Invalid YAML config in {path}: expected dict, got {type(config)}"
                    )
                return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML config {path}: {e}")

    def _load_env_overrides(self) -> dict[str, Any]:
        """Load configuration overrides from environment variables.

        Scans environment variables for configuration overrides using both
        special mappings and generic PBJRAG_* variables. Performs automatic
        type conversion for booleans, integers, and floats.

        Environment variable patterns:
            - Special mappings: QDRANT_HOST, NEO4J_URI, etc.
            - Generic: PBJRAG_SECTION_KEY (e.g., PBJRAG_CORE_FIELD_DIM)

        Returns:
            dict[str, Any]: Configuration overrides from environment

        Examples:
            Set environment variables::

                $ export PBJRAG_CORE_FIELD_DIM=16
                $ export PBJRAG_CORE_PURPOSE=stability
                $ export QDRANT_HOST=db.example.com
                $ export NEO4J_PASSWORD=secret123

            Load with overrides::

                loader = ConfigLoader()
                config = loader.load()
                # config['core']['field_dim'] == 16
                # config['vector_store']['qdrant']['host'] == 'db.example.com'
        """
        overrides: dict[str, Any] = {}

        # Special handling for common variables
        env_mappings = {
            "QDRANT_HOST": ("vector_store", "qdrant", "host"),
            "QDRANT_PORT": ("vector_store", "qdrant", "port"),
            "INFINITY_URL": ("vector_store", "infinity_url"),
            "NEO4J_URI": ("neo4j", "uri"),
            "NEO4J_USER": ("neo4j", "user"),
            "NEO4J_PASSWORD": ("neo4j", "password"),
            "CHROMA_DB_PATH": ("chroma", "path"),
        }

        for env_var, path in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                self._set_nested(overrides, path, self._convert_type(value))

        # Generic PBJRAG_* environment variables
        # Pattern: PBJRAG_SECTION_KEY -> section.key (only split on first underscore)
        for key, value in os.environ.items():
            if key.startswith("PBJRAG_"):
                # Remove PBJRAG_ prefix
                remainder = key[7:]
                parts = remainder.split("_", 1)  # Split only on first underscore

                if len(parts) == 2:
                    section, option = parts
                    # Convert to lowercase for section, keep option as-is for snake_case
                    section = section.lower()
                    option = option.lower()
                    self._set_nested(overrides, (section, option), self._convert_type(value))
                elif len(parts) == 1:
                    # Single-level config (unusual but supported)
                    self._set_nested(overrides, (parts[0].lower(),), self._convert_type(value))

        return overrides

    def _set_nested(self, d: dict[str, Any], path: tuple, value: Any) -> None:
        """Set a nested dictionary value using a tuple path.

        Creates intermediate dictionaries as needed to set a value at the
        specified nested path.

        Args:
            d (dict[str, Any]): Dictionary to modify
            path (tuple): Tuple of keys representing nested path
            value (Any): Value to set at the path

        Examples:
            >>> config = {}
            >>> loader._set_nested(config, ('core', 'field_dim'), 16)
            >>> print(config)
            {'core': {'field_dim': 16}}
        """
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    def _convert_type(self, value: str) -> Any:
        """Convert string environment variable to appropriate type.

        Attempts to convert string values to boolean, integer, or float.
        Falls back to string if no conversion is possible.

        Args:
            value (str): String value from environment variable

        Returns:
            Any: Converted value (bool, int, float, or str)

        Examples:
            >>> loader._convert_type('true')
            True
            >>> loader._convert_type('42')
            42
            >>> loader._convert_type('3.14')
            3.14
            >>> loader._convert_type('hello')
            'hello'
        """
        # Boolean
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # String
        return value

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries, override takes precedence.

        Recursively merges two dictionaries, with values from 'override' taking
        precedence over 'base'. Nested dictionaries are merged recursively.

        Args:
            base (dict[str, Any]): Base configuration dictionary
            override (dict[str, Any]): Override configuration dictionary

        Returns:
            dict[str, Any]: Merged configuration dictionary

        Examples:
            >>> base = {'core': {'field_dim': 8, 'purpose': 'coherence'}}
            >>> override = {'core': {'field_dim': 16}}
            >>> result = loader._deep_merge(base, override)
            >>> print(result)
            {'core': {'field_dim': 16, 'purpose': 'coherence'}}
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _get_hardcoded_defaults(self) -> dict[str, Any]:
        """Get fallback hardcoded defaults if YAML not available.

        Provides minimal default configuration when config/default.yaml cannot
        be loaded or YAML support is not available.

        Returns:
            dict[str, Any]: Hardcoded default configuration
        """
        return {
            "core": {
                "version": "3.0.0",
                "field_dim": 8,
                "purpose": "coherence",
                "output_dir": "pbjrag_output",
                "log_level": "INFO",
                "enable_vector_store": True,
                "enable_neo4j": False,
                "enable_chroma": False,
            },
            "vector_store": {
                "qdrant": {
                    "host": "localhost",
                    "port": 6333,
                    "collection_name": "crown_jewel_dsc",
                },
                "infinity_url": "http://127.0.0.1:7997",
                "embedding_model": "jinaai/jina-embeddings-v2-base-code",
                "batch_size": 32,
            },
            "analysis": {
                "coherence_method": "standard",
                "enable_pattern_detection": True,
                "complexity_threshold": 10,
            },
            "report": {
                "format": "markdown",
                "persona": "general",
            },
        }

    def get(self, *keys: str, default: Any = None) -> Any:
        """Get a configuration value using nested keys.

        Retrieves a value from the configuration dictionary using a sequence
        of keys representing a nested path. Returns default if any key in the
        path is not found.

        Args:
            *keys (str): Variable number of keys forming a nested path
            default (Any): Default value to return if path not found

        Returns:
            Any: Configuration value at the specified path, or default

        Raises:
            ConfigurationError: If configuration has not been loaded

        Examples:
            >>> config = get_config()
            >>> field_dim = config.get('core', 'field_dim')  # 8
            >>> qdrant_host = config.get('vector_store', 'qdrant', 'host')  # 'localhost'
            >>> missing = config.get('nonexistent', 'key', default='fallback')  # 'fallback'
        """
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded. Call load() first.")

        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def config(self) -> dict[str, Any]:
        """Get the complete configuration dictionary.

        Returns:
            dict[str, Any]: Complete merged configuration dictionary

        Raises:
            ConfigurationError: If configuration has not been loaded

        Examples:
            >>> loader = ConfigLoader()
            >>> loader.load()
            >>> full_config = loader.config
            >>> print(full_config['core']['field_dim'])
            8
        """
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded. Call load() first.")
        return self._config


# =============================================================================
# Global Configuration Instance
# =============================================================================

_global_config: ConfigLoader | None = None


def get_config(
    config_file: str | Path | None = None,
    config_dict: dict[str, Any] | None = None,
    reload: bool = False,
) -> ConfigLoader:
    """Get the global configuration instance.

    Returns a singleton ConfigLoader instance that can be reused across the
    application. Creates and loads the configuration on first call, then
    returns the cached instance on subsequent calls unless reload=True.

    Args:
        config_file (str | Path | None): Optional path to custom config file
        config_dict (dict[str, Any] | None): Optional runtime configuration overrides
        reload (bool): Force reload configuration from sources

    Returns:
        ConfigLoader: Global ConfigLoader instance with loaded configuration

    Examples:
        Basic usage::

            >>> config = get_config()
            >>> field_dim = config.get('core', 'field_dim')
            >>> print(field_dim)
            8

        With custom file::

            >>> config = get_config(config_file='production.yaml')
            >>> purpose = config.get('core', 'purpose')

        Force reload::

            >>> config = get_config(reload=True)  # Reload from all sources
    """
    global _global_config

    if _global_config is None or reload:
        _global_config = ConfigLoader()
        _global_config.load(config_file=config_file, config_dict=config_dict)

    return _global_config


def load_config(
    config_file: str | Path | None = None,
    config_dict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convenience function to load and return configuration as a dictionary.

    Loads configuration from all sources and returns the complete merged
    dictionary. This is a convenience wrapper around get_config() for cases
    where you just need the config dict without the ConfigLoader instance.

    Args:
        config_file (str | Path | None): Optional path to custom config file
        config_dict (dict[str, Any] | None): Optional runtime configuration overrides

    Returns:
        dict[str, Any]: Complete configuration dictionary

    Examples:
        Basic usage::

            >>> config = load_config()
            >>> print(config['core']['field_dim'])
            8

        With overrides::

            >>> config = load_config(
            ...     config_dict={'core': {'purpose': 'stability', 'field_dim': 16}}
            ... )
            >>> print(config['core']['purpose'])
            stability
            >>> print(config['core']['field_dim'])
            16
    """
    config_loader = get_config(config_file=config_file, config_dict=config_dict, reload=True)
    return config_loader.config


# =============================================================================
# CLI Integration Helper
# =============================================================================


def setup_logging(config: dict[str, Any] | None = None) -> None:
    """Setup logging based on configuration.

    Configures Python's logging system with the log level specified in
    configuration. Uses global config if not provided, falls back to INFO
    level if no configuration is available.

    Args:
        config (dict[str, Any] | None): Configuration dictionary. If None,
            uses global configuration instance if loaded.

    Examples:
        With explicit config::

            >>> config = load_config()
            >>> setup_logging(config)

        Using global config::

            >>> load_config()
            >>> setup_logging()  # Uses global config

        Before config loaded::

            >>> setup_logging()  # Falls back to INFO level
    """
    if config is None:
        try:
            config = get_config().config
        except ConfigurationError:
            # No config loaded yet, use defaults
            log_level = "INFO"
        else:
            log_level = config.get("core", {}).get("log_level", "INFO")
    else:
        log_level = config.get("core", {}).get("log_level", "INFO")

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example 1: Load with defaults
    print("Example 1: Load default configuration")
    config = load_config()
    print(f"Field dimension: {config['core']['field_dim']}")
    print(f"Qdrant host: {config['vector_store']['qdrant']['host']}")

    # Example 2: Load with environment variable override
    print("\nExample 2: Load with environment variable override")
    os.environ["PBJRAG_CORE_FIELD_DIM"] = "16"
    config = load_config()
    print(f"Field dimension: {config['core']['field_dim']}")

    # Example 3: Load with runtime overrides
    print("\nExample 3: Load with runtime overrides")
    config = load_config(config_dict={"core": {"purpose": "stability"}})
    print(f"Purpose: {config['core']['purpose']}")

    # Example 4: Using ConfigLoader directly
    print("\nExample 4: Using ConfigLoader get() method")
    config_loader = get_config()
    field_dim = config_loader.get("core", "field_dim")
    qdrant_host = config_loader.get("vector_store", "qdrant", "host")
    print(f"Field dimension: {field_dim}")
    print(f"Qdrant host: {qdrant_host}")
