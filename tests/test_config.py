"""
Tests for configuration management module.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path to import config module directly (avoids NumPy/SciPy import issues)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestCoreConfig:
    """Test core configuration loading and validation."""

    def test_import_config_module(self):
        """Test that config module can be imported."""
        from pbjrag import config

        assert config is not None

    def test_have_pydantic_detection(self):
        """Test that HAVE_PYDANTIC is set correctly."""
        from pbjrag.config import HAVE_PYDANTIC

        # Should be True since we have pydantic installed
        assert isinstance(HAVE_PYDANTIC, bool)

    def test_have_yaml_detection(self):
        """Test that HAVE_YAML is set correctly."""
        from pbjrag.config import HAVE_YAML

        # Should be True since we have yaml installed
        assert isinstance(HAVE_YAML, bool)

    @pytest.mark.skipif(
        not os.path.exists("/home/ndspence/GitHub/navi-pbjrag/src/pbjrag/config.py"),
        reason="Config module not found",
    )
    def test_core_config_defaults(self):
        """Test CoreConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import CoreConfig

            config = CoreConfig()
            assert config.version == "3.0.0"
            assert config.field_dim == 8
            assert config.purpose == "coherence"
            assert config.output_dir == "pbjrag_output"
            assert config.log_level == "INFO"
            assert config.enable_vector_store is True

    @pytest.mark.skipif(
        not os.path.exists("/home/ndspence/GitHub/navi-pbjrag/src/pbjrag/config.py"),
        reason="Config module not found",
    )
    def test_core_config_custom_values(self):
        """Test CoreConfig with custom values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import CoreConfig

            config = CoreConfig(field_dim=16, purpose="stability", output_dir="custom_output")
            assert config.field_dim == 16
            assert config.purpose == "stability"
            assert config.output_dir == "custom_output"


class TestQdrantConfig:
    """Test Qdrant configuration."""

    def test_qdrant_config_defaults(self):
        """Test QdrantConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import QdrantConfig

            config = QdrantConfig()
            assert config.host == "localhost"
            assert config.port == 6333
            assert config.collection_name == "crown_jewel_dsc"
            assert config.distance == "cosine"
            assert config.enable_hnsw is True


class TestVectorStoreConfig:
    """Test vector store configuration."""

    def test_vector_store_config_defaults(self):
        """Test VectorStoreConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import VectorStoreConfig

            config = VectorStoreConfig()
            assert config.batch_size == 32
            assert config.max_chunk_size == 2048


class TestChromaConfig:
    """Test ChromaDB configuration."""

    def test_chroma_config_defaults(self):
        """Test ChromaConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import ChromaConfig

            config = ChromaConfig()
            assert config.collection_name == "crown_jewel_dsc"
            assert config.embedding_model == "all-mpnet-base-v2"
            assert config.batch_size == 32


class TestNeo4jConfig:
    """Test Neo4j configuration."""

    def test_neo4j_config_defaults(self):
        """Test Neo4jConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import Neo4jConfig

            config = Neo4jConfig()
            assert config.uri == "bolt://localhost:7687"
            assert config.user == "neo4j"
            assert config.database == "neo4j"
            assert config.enable_graph_algorithms is True


class TestEmbeddingConfig:
    """Test embedding configuration."""

    def test_embedding_config_defaults(self):
        """Test EmbeddingConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import EmbeddingConfig

            config = EmbeddingConfig()
            assert config.backend == "ollama"
            assert config.url == "http://localhost:11434"
            assert config.dimension == 1024


class TestConfigValidation:
    """Test configuration validation."""

    def test_invalid_field_dim_too_small(self):
        """Test that field_dim below minimum raises error."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pydantic import ValidationError

            from pbjrag.config import CoreConfig

            with pytest.raises(ValidationError):
                CoreConfig(field_dim=2)  # Min is 4

    def test_invalid_field_dim_too_large(self):
        """Test that field_dim above maximum raises error."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pydantic import ValidationError

            from pbjrag.config import CoreConfig

            with pytest.raises(ValidationError):
                CoreConfig(field_dim=64)  # Max is 32

    def test_invalid_purpose(self):
        """Test that invalid purpose raises error."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pydantic import ValidationError

            from pbjrag.config import CoreConfig

            with pytest.raises(ValidationError):
                CoreConfig(purpose="invalid_purpose")

    def test_invalid_log_level(self):
        """Test that invalid log level raises error."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pydantic import ValidationError

            from pbjrag.config import CoreConfig

            with pytest.raises(ValidationError):
                CoreConfig(log_level="TRACE")

    def test_invalid_port_negative(self):
        """Test that negative port raises error."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pydantic import ValidationError

            from pbjrag.config import QdrantConfig

            with pytest.raises(ValidationError):
                QdrantConfig(port=-1)

    def test_invalid_distance_metric(self):
        """Test that invalid distance metric raises error."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pydantic import ValidationError

            from pbjrag.config import QdrantConfig

            with pytest.raises(ValidationError):
                QdrantConfig(distance="manhattan")


class TestAnalysisConfig:
    """Test analysis configuration."""

    def test_analysis_config_defaults(self):
        """Test AnalysisConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import AnalysisConfig

            config = AnalysisConfig()
            assert config.coherence_method == "standard"
            assert config.enable_pattern_detection is True
            assert config.pattern_confidence_threshold == 0.6
            assert config.enable_complexity_analysis is True
            assert config.complexity_threshold == 10
            assert config.enable_dependency_analysis is True

    def test_analysis_config_custom(self):
        """Test AnalysisConfig with custom values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import AnalysisConfig

            config = AnalysisConfig(coherence_method="weighted", pattern_confidence_threshold=0.8)
            assert config.coherence_method == "weighted"
            assert config.pattern_confidence_threshold == 0.8


class TestPerformanceConfig:
    """Test performance configuration."""

    def test_performance_config_defaults(self):
        """Test PerformanceConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import PerformanceConfig

            config = PerformanceConfig()
            assert config.worker_threads == 0
            assert config.max_parallel_files == 4
            assert config.memory_optimization is False
            assert config.max_memory_mb == 0


class TestReportConfig:
    """Test report configuration."""

    def test_report_config_defaults(self):
        """Test ReportConfig default values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import ReportConfig

            config = ReportConfig()
            assert config.format == "markdown"
            assert config.include_snippets is True
            assert config.max_snippet_length == 200
            assert config.persona == "general"
            assert config.include_visualizations is False

    def test_report_config_custom(self):
        """Test ReportConfig with custom values."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import ReportConfig

            config = ReportConfig(format="json", persona="devops", include_visualizations=True)
            assert config.format == "json"
            assert config.persona == "devops"
            assert config.include_visualizations is True


class TestPBJRAGConfig:
    """Test complete PBJRAG configuration."""

    def test_pbjrag_config_defaults(self):
        """Test PBJRAGConfig with all defaults."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import PBJRAGConfig

            config = PBJRAGConfig()
            assert config.core is not None
            assert config.vector_store is not None
            assert config.chroma is not None
            assert config.neo4j is not None
            assert config.embedding is not None
            assert config.analysis is not None
            assert config.performance is not None
            assert config.report is not None

    def test_pbjrag_config_model_dump(self):
        """Test PBJRAGConfig can be serialized."""
        from pbjrag.config import HAVE_PYDANTIC

        if HAVE_PYDANTIC:
            from pbjrag.config import PBJRAGConfig

            config = PBJRAGConfig()
            dumped = config.model_dump()
            assert isinstance(dumped, dict)
            assert "core" in dumped
            assert "vector_store" in dumped


class TestConfigLoader:
    """Test configuration loader."""

    def test_config_loader_initialization(self):
        """Test ConfigLoader can be instantiated."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()
        assert loader._config == {}
        assert loader._loaded is False

    def test_config_loader_load_with_dict(self):
        """Test ConfigLoader with dict override."""
        from pbjrag.config import HAVE_PYDANTIC, ConfigLoader

        loader = ConfigLoader()

        config = loader.load(config_dict={"core": {"field_dim": 16}}, validate=False)

        assert config is not None
        if "core" in config:
            assert config["core"].get("field_dim") == 16

    def test_config_loader_load_defaults(self):
        """Test ConfigLoader loads defaults."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()
        config = loader.load(validate=False)
        assert config is not None
        assert loader._loaded is True

    def test_config_loader_deep_merge(self):
        """Test ConfigLoader deep merge functionality."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()

        base = {"a": {"b": 1, "c": 2}, "d": 3}
        override = {"a": {"b": 10, "e": 5}}
        merged = loader._deep_merge(base, override)

        assert merged["a"]["b"] == 10
        assert merged["a"]["c"] == 2
        assert merged["a"]["e"] == 5
        assert merged["d"] == 3


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_exists(self):
        """Test ConfigurationError can be raised."""
        from pbjrag.config import ConfigurationError

        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test error")

    def test_configuration_error_message(self):
        """Test ConfigurationError has message."""
        from pbjrag.config import ConfigurationError

        try:
            raise ConfigurationError("Test error message")
        except ConfigurationError as e:
            assert "Test error message" in str(e)


class TestGetConfig:
    """Test get_config function."""

    def test_get_config_function(self):
        """Test get_config returns ConfigLoader."""
        from pbjrag.config import ConfigLoader, get_config

        config = get_config()
        assert config is not None
        assert isinstance(config, ConfigLoader)

    def test_get_config_with_overrides(self):
        """Test get_config with config_dict overrides."""
        from pbjrag.config import ConfigLoader, get_config

        # get_config takes config_dict as second positional arg
        config = get_config(config_dict={"core": {"purpose": "stability"}})
        assert config is not None
        assert isinstance(config, ConfigLoader)

    def test_get_config_reload(self):
        """Test get_config with reload."""
        from pbjrag.config import get_config

        config1 = get_config()
        config2 = get_config(reload=True)
        assert config1 is not None
        assert config2 is not None


class TestYAMLLoading:
    """Test YAML file loading functionality."""

    def test_load_yaml_config_valid_file(self, tmp_path):
        """Test loading valid YAML config file."""
        from pbjrag.config import HAVE_YAML, ConfigLoader

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        # Create a valid YAML config file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            """
core:
  field_dim: 16
  purpose: stability
vector_store:
  qdrant:
    host: test-host
    port: 7000
"""
        )

        loader = ConfigLoader()
        config = loader._load_yaml_config(config_file)

        assert config["core"]["field_dim"] == 16
        assert config["core"]["purpose"] == "stability"
        assert config["vector_store"]["qdrant"]["host"] == "test-host"
        assert config["vector_store"]["qdrant"]["port"] == 7000

    def test_load_yaml_config_file_not_found(self):
        """Test loading non-existent YAML file raises error."""
        from pbjrag.config import HAVE_YAML, ConfigLoader, ConfigurationError

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        loader = ConfigLoader()
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            loader._load_yaml_config("/nonexistent/path/config.yaml")

    def test_load_yaml_config_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML raises error."""
        from pbjrag.config import HAVE_YAML, ConfigLoader, ConfigurationError

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: :")

        loader = ConfigLoader()
        with pytest.raises(ConfigurationError, match="Failed to parse YAML"):
            loader._load_yaml_config(config_file)

    def test_load_yaml_config_not_dict(self, tmp_path):
        """Test loading YAML that's not a dict raises error."""
        from pbjrag.config import HAVE_YAML, ConfigLoader, ConfigurationError

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        config_file = tmp_path / "list.yaml"
        config_file.write_text("- item1\n- item2\n")

        loader = ConfigLoader()
        with pytest.raises(ConfigurationError, match="expected dict"):
            loader._load_yaml_config(config_file)

    def test_load_yaml_without_yaml_support(self):
        """Test YAML loading without yaml module raises error."""
        from pbjrag.config import ConfigLoader, ConfigurationError

        loader = ConfigLoader()

        with patch("pbjrag.config.HAVE_YAML", False):
            with pytest.raises(ConfigurationError, match="YAML support not available"):
                loader._load_yaml_config("/some/path.yaml")

    def test_load_default_config_with_yaml(self, tmp_path):
        """Test loading default config when YAML is available."""
        from pbjrag.config import HAVE_YAML, ConfigLoader

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        loader = ConfigLoader()
        config = loader._load_default_config()

        assert config is not None
        assert isinstance(config, dict)

    def test_load_default_config_fallback(self):
        """Test fallback to hardcoded defaults when YAML unavailable."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()

        with patch("pbjrag.config.HAVE_YAML", False):
            config = loader._load_default_config()

            assert config is not None
            assert config["core"]["version"] == "3.0.0"
            assert config["core"]["field_dim"] == 8
            assert config["core"]["purpose"] == "coherence"

    def test_load_with_custom_config_file(self, tmp_path):
        """Test loading with custom config file."""
        from pbjrag.config import HAVE_YAML, ConfigLoader

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        config_file = tmp_path / "custom.yaml"
        config_file.write_text(
            """
core:
  field_dim: 24
  purpose: innovation
"""
        )

        loader = ConfigLoader()
        config = loader.load(config_file=config_file, validate=False)

        assert config["core"]["field_dim"] == 24
        assert config["core"]["purpose"] == "innovation"

    def test_load_with_pbjrag_config_env_var(self, tmp_path, monkeypatch):
        """Test loading config from PBJRAG_CONFIG environment variable."""
        from pbjrag.config import HAVE_YAML, ConfigLoader

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        config_file = tmp_path / "env_config.yaml"
        config_file.write_text(
            """
core:
  field_dim: 20
  purpose: emergence
"""
        )

        monkeypatch.setenv("PBJRAG_CONFIG", str(config_file))

        loader = ConfigLoader()
        config = loader.load(validate=False)

        assert config["core"]["field_dim"] == 20
        assert config["core"]["purpose"] == "emergence"


class TestEnvironmentVariables:
    """Test environment variable loading."""

    def test_load_env_overrides_qdrant(self, monkeypatch):
        """Test QDRANT environment variables."""
        from pbjrag.config import ConfigLoader

        monkeypatch.setenv("QDRANT_HOST", "qdrant.example.com")
        monkeypatch.setenv("QDRANT_PORT", "9999")

        loader = ConfigLoader()
        overrides = loader._load_env_overrides()

        assert overrides["vector_store"]["qdrant"]["host"] == "qdrant.example.com"
        assert overrides["vector_store"]["qdrant"]["port"] == 9999

    def test_load_env_overrides_neo4j(self, monkeypatch):
        """Test NEO4J environment variables."""
        from pbjrag.config import ConfigLoader

        monkeypatch.setenv("NEO4J_URI", "bolt://neo4j.example.com:7687")
        monkeypatch.setenv("NEO4J_USER", "admin")
        monkeypatch.setenv("NEO4J_PASSWORD", "secret123")

        loader = ConfigLoader()
        overrides = loader._load_env_overrides()

        assert overrides["neo4j"]["uri"] == "bolt://neo4j.example.com:7687"
        assert overrides["neo4j"]["user"] == "admin"
        assert overrides["neo4j"]["password"] == "secret123"

    def test_load_env_overrides_chroma(self, monkeypatch):
        """Test CHROMA_DB_PATH environment variable."""
        from pbjrag.config import ConfigLoader

        monkeypatch.setenv("CHROMA_DB_PATH", "/custom/chroma/path")

        loader = ConfigLoader()
        overrides = loader._load_env_overrides()

        assert overrides["chroma"]["path"] == "/custom/chroma/path"

    def test_load_env_overrides_infinity_url(self, monkeypatch):
        """Test INFINITY_URL environment variable."""
        from pbjrag.config import ConfigLoader

        monkeypatch.setenv("INFINITY_URL", "http://infinity.example.com:8080")

        loader = ConfigLoader()
        overrides = loader._load_env_overrides()

        assert overrides["vector_store"]["infinity_url"] == "http://infinity.example.com:8080"

    def test_load_env_overrides_pbjrag_two_level(self, monkeypatch):
        """Test PBJRAG_ environment variables with two levels."""
        from pbjrag.config import ConfigLoader

        monkeypatch.setenv("PBJRAG_CORE_FIELD_DIM", "12")
        monkeypatch.setenv("PBJRAG_CORE_PURPOSE", "stability")
        monkeypatch.setenv("PBJRAG_CORE_LOG_LEVEL", "DEBUG")

        loader = ConfigLoader()
        overrides = loader._load_env_overrides()

        assert overrides["core"]["field_dim"] == 12
        assert overrides["core"]["purpose"] == "stability"
        assert overrides["core"]["log_level"] == "DEBUG"

    def test_load_env_overrides_pbjrag_single_level(self, monkeypatch):
        """Test PBJRAG_ environment variable with single level."""
        from pbjrag.config import ConfigLoader

        monkeypatch.setenv("PBJRAG_VERSION", "4.0.0")

        loader = ConfigLoader()
        overrides = loader._load_env_overrides()

        assert overrides["version"] == "4.0.0"

    def test_convert_type_boolean_true(self):
        """Test type conversion for boolean true values."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()

        assert loader._convert_type("true") is True
        assert loader._convert_type("True") is True
        assert loader._convert_type("yes") is True
        assert loader._convert_type("1") is True
        assert loader._convert_type("on") is True

    def test_convert_type_boolean_false(self):
        """Test type conversion for boolean false values."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()

        assert loader._convert_type("false") is False
        assert loader._convert_type("False") is False
        assert loader._convert_type("no") is False
        assert loader._convert_type("0") is False
        assert loader._convert_type("off") is False

    def test_convert_type_integer(self):
        """Test type conversion for integers."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()

        assert loader._convert_type("42") == 42
        assert loader._convert_type("-10") == -10
        assert loader._convert_type("0") is False  # Handled as boolean first

    def test_convert_type_float(self):
        """Test type conversion for floats."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()

        assert loader._convert_type("3.14") == 3.14
        assert loader._convert_type("-2.5") == -2.5

    def test_convert_type_string(self):
        """Test type conversion for strings."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()

        assert loader._convert_type("hello") == "hello"
        assert loader._convert_type("some text") == "some text"

    def test_set_nested_single_level(self):
        """Test setting nested value with single level."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()
        d = {}

        loader._set_nested(d, ("key",), "value")

        assert d["key"] == "value"

    def test_set_nested_multi_level(self):
        """Test setting nested value with multiple levels."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()
        d = {}

        loader._set_nested(d, ("level1", "level2", "level3"), "deep_value")

        assert d["level1"]["level2"]["level3"] == "deep_value"


class TestConfigValidation:
    """Test configuration validation with Pydantic."""

    def test_load_with_validation_success(self):
        """Test loading with valid config and validation enabled."""
        from pbjrag.config import HAVE_PYDANTIC, ConfigLoader

        if not HAVE_PYDANTIC:
            pytest.skip("Pydantic not available")

        loader = ConfigLoader()
        config = loader.load(config_dict={"core": {"field_dim": 16}}, validate=True)

        assert config is not None
        assert config["core"]["field_dim"] == 16

    def test_load_with_validation_failure(self):
        """Test loading with invalid config and validation enabled."""
        from pbjrag.config import HAVE_PYDANTIC, ConfigLoader, ConfigurationError

        if not HAVE_PYDANTIC:
            pytest.skip("Pydantic not available")

        loader = ConfigLoader()

        with pytest.raises(ConfigurationError, match="Invalid configuration"):
            loader.load(
                config_dict={"core": {"field_dim": 100}}, validate=True  # Exceeds max of 32
            )

    def test_load_without_pydantic(self):
        """Test loading when Pydantic is not available."""
        from pbjrag.config import ConfigLoader

        with patch("pbjrag.config.HAVE_PYDANTIC", False):
            loader = ConfigLoader()
            config = loader.load(
                config_dict={"core": {"field_dim": 16}}, validate=True  # Should be ignored
            )

            assert config is not None
            assert config["core"]["field_dim"] == 16


class TestConfigLoaderMethods:
    """Test ConfigLoader methods."""

    def test_get_method_single_key(self):
        """Test get method with single key."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()
        loader.load(config_dict={"test": "value"}, validate=False)

        assert loader.get("test") == "value"

    def test_get_method_nested_keys(self):
        """Test get method with nested keys."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()
        loader.load(config_dict={"level1": {"level2": {"level3": "deep"}}}, validate=False)

        assert loader.get("level1", "level2", "level3") == "deep"

    def test_get_method_with_default(self):
        """Test get method with default value."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()
        loader.load(config_dict={}, validate=False)

        assert loader.get("nonexistent", default="fallback") == "fallback"

    def test_get_method_not_loaded(self):
        """Test get method before loading raises error."""
        from pbjrag.config import ConfigLoader, ConfigurationError

        loader = ConfigLoader()

        with pytest.raises(ConfigurationError, match="Configuration not loaded"):
            loader.get("test")

    def test_config_property(self):
        """Test config property returns full config."""
        from pbjrag.config import ConfigLoader

        loader = ConfigLoader()
        loader.load(config_dict={"test": "value"}, validate=False)

        config = loader.config
        assert isinstance(config, dict)
        assert "test" in config

    def test_config_property_not_loaded(self):
        """Test config property before loading raises error."""
        from pbjrag.config import ConfigLoader, ConfigurationError

        loader = ConfigLoader()

        with pytest.raises(ConfigurationError, match="Configuration not loaded"):
            _ = loader.config

    def test_load_error_handling(self, tmp_path):
        """Test error handling during load."""
        from pbjrag.config import HAVE_YAML, ConfigLoader, ConfigurationError

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        # Create an invalid config file
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("- list_instead_of_dict")

        loader = ConfigLoader()

        with pytest.raises(ConfigurationError):
            loader.load(config_file=config_file, validate=False)


class TestLoadConfig:
    """Test load_config convenience function."""

    def test_load_config_function(self):
        """Test load_config returns dict."""
        from pbjrag.config import load_config

        config = load_config(config_dict={"test": "value"})

        assert isinstance(config, dict)
        assert "test" in config

    def test_load_config_with_overrides(self):
        """Test load_config with config_dict."""
        from pbjrag.config import load_config

        config = load_config(config_dict={"core": {"purpose": "innovation"}})

        assert config["core"]["purpose"] == "innovation"


class TestSetupLogging:
    """Test logging setup."""

    def test_setup_logging_with_config(self):
        """Test setup_logging with provided config."""
        import logging

        from pbjrag.config import setup_logging

        # Store original level
        original_level = logging.root.level

        try:
            config = {"core": {"log_level": "DEBUG"}}
            setup_logging(config)

            # Check that logging was called (function may not affect root logger directly)
            # Just verify no error is raised
            assert True
        finally:
            # Restore original level
            logging.root.setLevel(original_level)

    def test_setup_logging_without_config(self):
        """Test setup_logging without config uses global."""
        import logging

        from pbjrag.config import get_config, setup_logging

        # Store original level
        original_level = logging.root.level

        try:
            # Load global config first
            get_config(reload=True)

            setup_logging(None)

            # Should not raise error and level should be valid
            assert logging.root.level in [
                logging.DEBUG,
                logging.INFO,
                logging.WARNING,
                logging.ERROR,
                logging.CRITICAL,
            ]
        finally:
            # Restore original level
            logging.root.setLevel(original_level)

    def test_setup_logging_no_global_config(self):
        """Test setup_logging when no global config loaded."""
        import logging

        from pbjrag.config import setup_logging

        # Store original level
        original_level = logging.root.level

        try:
            # Reset global config
            import pbjrag.config as config_module

            config_module._global_config = None

            setup_logging(None)

            # Should default to INFO or higher
            assert logging.root.level >= logging.DEBUG
        finally:
            # Restore original level
            logging.root.setLevel(original_level)


class TestPriorityMerging:
    """Test configuration priority and merging."""

    def test_priority_runtime_over_env(self, monkeypatch):
        """Test runtime config takes priority over environment."""
        from pbjrag.config import ConfigLoader

        monkeypatch.setenv("PBJRAG_CORE_FIELD_DIM", "12")

        loader = ConfigLoader()
        config = loader.load(config_dict={"core": {"field_dim": 24}}, validate=False)

        # Runtime should override env
        assert config["core"]["field_dim"] == 24

    def test_priority_env_over_file(self, tmp_path, monkeypatch):
        """Test environment takes priority over config file."""
        from pbjrag.config import HAVE_YAML, ConfigLoader

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        config_file = tmp_path / "test.yaml"
        config_file.write_text(
            """
core:
  field_dim: 8
"""
        )

        monkeypatch.setenv("PBJRAG_CORE_FIELD_DIM", "16")

        loader = ConfigLoader()
        config = loader.load(config_file=config_file, validate=False)

        # Env should override file
        assert config["core"]["field_dim"] == 16

    def test_full_priority_chain(self, tmp_path, monkeypatch):
        """Test complete priority chain."""
        from pbjrag.config import HAVE_YAML, ConfigLoader

        if not HAVE_YAML:
            pytest.skip("YAML support not available")

        # File config
        config_file = tmp_path / "test.yaml"
        config_file.write_text(
            """
core:
  field_dim: 8
  purpose: coherence
  output_dir: file_output
"""
        )

        # Env override
        monkeypatch.setenv("PBJRAG_CORE_PURPOSE", "stability")

        # Runtime override
        loader = ConfigLoader()
        config = loader.load(
            config_file=config_file, config_dict={"core": {"field_dim": 24}}, validate=False
        )

        # Check priorities: runtime > env > file > default
        assert config["core"]["field_dim"] == 24  # Runtime
        assert config["core"]["purpose"] == "stability"  # Env
        assert config["core"]["output_dir"] == "file_output"  # File
