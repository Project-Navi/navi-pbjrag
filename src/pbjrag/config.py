#!/usr/bin/env python3
"""
PBJRAG Configuration Management

Loads configuration from multiple sources in priority order:
1. Default config (config/default.yaml)
2. Custom config file (via PBJRAG_CONFIG env var or --config flag)
3. Environment variables (PBJRAG_<SECTION>_<OPTION>)
4. Runtime overrides (passed to functions)

Uses Pydantic for validation when available, falls back to dict validation.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

# Optional Pydantic import for validation
try:
    from pydantic import BaseModel, Field, ValidationError, field_validator

    HAVE_PYDANTIC = True
except ImportError:
    HAVE_PYDANTIC = False
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore
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
        """Core configuration settings"""

        version: str = "3.0.0"
        field_dim: int = Field(default=8, ge=4, le=32)
        purpose: str = Field(default="coherence", pattern="^(stability|emergence|coherence|innovation)$")
        output_dir: str = "pbjrag_output"
        log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
        enable_vector_store: bool = True
        enable_neo4j: bool = False
        enable_chroma: bool = False

    class QdrantConfig(BaseModel):
        """Qdrant vector store configuration"""

        host: str = "localhost"
        port: int = Field(default=6333, ge=1, le=65535)
        collection_name: str = "crown_jewel_dsc"
        distance: str = Field(default="cosine", pattern="^(cosine|euclidean|dot)$")
        enable_hnsw: bool = True

    class VectorStoreConfig(BaseModel):
        """Vector store configuration"""

        qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
        infinity_url: str = "http://127.0.0.1:7997"
        embedding_model: str = "jinaai/jina-embeddings-v2-base-code"
        batch_size: int = Field(default=32, ge=1, le=256)
        max_chunk_size: int = Field(default=2048, ge=256)

    class ChromaConfig(BaseModel):
        """ChromaDB configuration"""

        path: str = "/app/chroma_db"
        collection_name: str = "crown_jewel_dsc"
        embedding_model: str = "all-mpnet-base-v2"
        batch_size: int = Field(default=32, ge=1)

    class Neo4jConfig(BaseModel):
        """Neo4j graph store configuration"""

        uri: str = "bolt://localhost:7687"
        user: str = "neo4j"
        password: Optional[str] = None
        database: str = "neo4j"
        enable_graph_algorithms: bool = True

    class EmbeddingConfig(BaseModel):
        """Embedding configuration"""

        adapter: str = Field(default="infinity", pattern="^(infinity|sentence_transformers|openai)$")
        dimension: Optional[int] = Field(default=None, ge=128)
        normalize: bool = True
        enable_cache: bool = True
        cache_dir: str = ".pbjrag_cache"

    class AnalysisConfig(BaseModel):
        """Analysis configuration"""

        coherence_method: str = Field(default="standard", pattern="^(standard|weighted|adaptive)$")
        blessing_tiers: Dict[str, float] = Field(
            default_factory=lambda: {"positive": 0.7, "neutral": 0.4}
        )
        enable_pattern_detection: bool = True
        pattern_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
        enable_complexity_analysis: bool = True
        complexity_threshold: int = Field(default=10, ge=1)
        enable_dependency_analysis: bool = True

    class PerformanceConfig(BaseModel):
        """Performance configuration"""

        worker_threads: int = Field(default=0, ge=0)
        max_parallel_files: int = Field(default=4, ge=1)
        memory_optimization: bool = False
        max_memory_mb: int = Field(default=0, ge=0)

    class ReportConfig(BaseModel):
        """Report generation configuration"""

        format: str = Field(default="markdown", pattern="^(markdown|json|html|all)$")
        include_snippets: bool = True
        max_snippet_length: int = Field(default=200, ge=50)
        persona: str = Field(default="general", pattern="^(general|devops|scholar)$")
        include_visualizations: bool = False

    class PBJRAGConfig(BaseModel):
        """Complete PBJRAG configuration"""

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
    """Raised when configuration is invalid or cannot be loaded"""

    pass


class ConfigLoader:
    """
    Loads and validates configuration from multiple sources.
    """

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._loaded = False

    def load(
        self,
        config_file: Optional[Union[str, Path]] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """
        Load configuration from multiple sources.

        Priority (highest to lowest):
        1. config_dict (runtime overrides)
        2. Environment variables
        3. config_file (custom config)
        4. Default config (config/default.yaml)

        Args:
            config_file: Path to custom YAML config file
            config_dict: Runtime configuration overrides
            validate: Whether to validate with Pydantic (if available)

        Returns:
            Complete configuration dictionary

        Raises:
            ConfigurationError: If configuration is invalid or cannot be loaded
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

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration from config/default.yaml"""
        # Try to find config/default.yaml relative to this file
        config_dir = Path(__file__).parent.parent.parent / "config"
        default_config_path = config_dir / "default.yaml"

        if default_config_path.exists() and HAVE_YAML:
            return self._load_yaml_config(default_config_path)

        # Fallback to hardcoded defaults if YAML not available
        logger.warning("Could not load default.yaml, using hardcoded defaults")
        return self._get_hardcoded_defaults()

    def _load_yaml_config(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not HAVE_YAML:
            raise ConfigurationError(
                "YAML support not available. Install with: pip install pyyaml"
            )

        path = Path(path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ConfigurationError(
                        f"Invalid YAML config in {path}: expected dict, got {type(config)}"
                    )
                return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML config {path}: {e}")

    def _load_env_overrides(self) -> Dict[str, Any]:
        """Load configuration overrides from environment variables"""
        overrides: Dict[str, Any] = {}

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

    def _set_nested(self, d: Dict[str, Any], path: tuple, value: Any) -> None:
        """Set a nested dictionary value using a tuple path"""
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    def _convert_type(self, value: str) -> Any:
        """Convert string environment variable to appropriate type"""
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

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, override takes precedence"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _get_hardcoded_defaults(self) -> Dict[str, Any]:
        """Fallback hardcoded defaults if YAML not available"""
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
        """
        Get a configuration value using dot notation.

        Example:
            config.get('core', 'field_dim')  # Returns 8
            config.get('vector_store', 'qdrant', 'host')  # Returns 'localhost'
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
    def config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary"""
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded. Call load() first.")
        return self._config


# =============================================================================
# Global Configuration Instance
# =============================================================================

_global_config: Optional[ConfigLoader] = None


def get_config(
    config_file: Optional[Union[str, Path]] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    reload: bool = False,
) -> ConfigLoader:
    """
    Get the global configuration instance.

    Args:
        config_file: Optional path to custom config file
        config_dict: Optional runtime configuration overrides
        reload: Force reload configuration

    Returns:
        ConfigLoader instance with loaded configuration

    Example:
        >>> config = get_config()
        >>> field_dim = config.get('core', 'field_dim')
        >>> print(field_dim)
        8
    """
    global _global_config

    if _global_config is None or reload:
        _global_config = ConfigLoader()
        _global_config.load(config_file=config_file, config_dict=config_dict)

    return _global_config


def load_config(
    config_file: Optional[Union[str, Path]] = None,
    config_dict: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to load and return configuration as a dictionary.

    Args:
        config_file: Optional path to custom config file
        config_dict: Optional runtime configuration overrides

    Returns:
        Complete configuration dictionary

    Example:
        >>> config = load_config()
        >>> print(config['core']['field_dim'])
        8
    """
    config_loader = get_config(config_file=config_file, config_dict=config_dict, reload=True)
    return config_loader.config


# =============================================================================
# CLI Integration Helper
# =============================================================================


def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Setup logging based on configuration.

    Args:
        config: Configuration dictionary (uses global config if None)
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

    # Example 2: Load with custom file
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
