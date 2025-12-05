"""
Comprehensive tests for Neo4j Store module.

Tests cover:
- Initialization with/without Neo4j driver available
- Password handling (direct and env var)
- Connection handling and error cases
- Schema setup
- All storage methods
- Query methods
- Graceful fallback when Neo4j unavailable
"""

import json
import os
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from pbjrag.dsc.neo4j_store import DSCNeo4jStore, UnifiedGraphStore


class TestDSCNeo4jStoreInitialization:
    """Test suite for DSCNeo4jStore initialization scenarios."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", False)
    def test_init_without_neo4j_driver(self, caplog):
        """Test initialization when Neo4j driver is not available."""
        store = DSCNeo4jStore()

        assert store.driver is None
        assert "Neo4j driver not available" in caplog.text
        assert "pip install neo4j" in caplog.text

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    @patch("pbjrag.dsc.neo4j_store.logger")
    def test_init_with_direct_password(self, mock_logger, mock_graph_db):
        """Test initialization with password provided directly."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(
            uri="bolt://localhost:7687", user="neo4j", password="test_password", database="neo4j"
        )

        # Verify driver was created with correct credentials
        mock_graph_db.driver.assert_called_once_with(
            "bolt://localhost:7687", auth=("neo4j", "test_password")
        )

        # Verify connection test was called (first call)
        first_call = mock_session.run.call_args_list[0]
        assert first_call.args[0] == "RETURN 1"

        # Verify successful connection log was called
        mock_logger.info.assert_called()
        log_messages = [call.args[0] for call in mock_logger.info.call_args_list]
        assert any("Connected to Neo4j" in msg for msg in log_messages)

        assert store.driver is not None
        assert store.database == "neo4j"

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    @patch.dict(os.environ, {"NEO4J_PASSWORD": "env_password"})
    def test_init_with_env_password(self, mock_graph_db):
        """Test initialization with password from environment variable."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(uri="bolt://test:7687", user="neo4j")

        # Verify password from env was used
        mock_graph_db.driver.assert_called_once_with(
            "bolt://test:7687", auth=("neo4j", "env_password")
        )
        assert store.driver is not None

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_password(self, caplog):
        """Test initialization without password fails gracefully."""
        store = DSCNeo4jStore()

        assert store.driver is None
        assert "Neo4j password not provided" in caplog.text
        assert "NEO4J_PASSWORD" in caplog.text

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_init_connection_failure(self, mock_graph_db, caplog):
        """Test initialization handles connection failures."""
        mock_graph_db.driver.side_effect = Exception("Connection refused")

        store = DSCNeo4jStore(password="test_password")

        assert store.driver is None
        assert "Failed to connect to Neo4j" in caplog.text
        assert "Connection refused" in caplog.text

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_init_test_query_failure(self, mock_graph_db, caplog):
        """Test initialization handles test query failures."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_session.run.side_effect = Exception("Query failed")
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")

        assert store.driver is None
        assert "Failed to connect to Neo4j" in caplog.text


class TestSchemaSetup:
    """Test suite for schema setup functionality."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_setup_schema_creates_indexes(self, mock_graph_db):
        """Test that schema setup creates all required indexes."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")

        # Verify schema queries were executed
        calls = mock_session.run.call_args_list

        # Check for index creation queries
        index_queries = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Module) ON (n.path)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Class) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Function) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Pattern) ON (n.type)",
            "CREATE INDEX IF NOT EXISTS FOR (n:FieldState) ON (n.timestamp)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Blessing) ON (n.tier)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Phase) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Chunk) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Embedding) ON (n.model)",
        ]

        # Check for constraint creation queries
        constraint_queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Module) REQUIRE n.path IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Chunk) REQUIRE n.id IS UNIQUE",
        ]

        # Verify all expected queries were called (after RETURN 1)
        executed_queries = [
            call.args[0] if call.args else call.kwargs.get("query", "") for call in calls[1:]
        ]  # Skip first "RETURN 1"

        for query in index_queries + constraint_queries:
            assert query in executed_queries, f"Missing query: {query}"

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_setup_schema_handles_errors(self, mock_graph_db, caplog):
        """Test that schema setup handles individual query failures gracefully."""
        mock_driver = MagicMock()
        mock_session = MagicMock()

        # Make schema queries fail but connection test succeed
        call_count = [0]

        def side_effect_func(query):
            call_count[0] += 1
            if call_count[0] == 1:  # First call is "RETURN 1"
                return MagicMock()
            raise Exception("Schema creation failed")

        mock_session.run.side_effect = side_effect_func
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")

        # Store should still be created despite schema errors
        assert store.driver is not None
        assert "Schema setup query failed" in caplog.text


class TestCodeStructureStorage:
    """Test suite for code structure storage methods."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", False)
    def test_store_code_structure_without_driver(self):
        """Test that store_code_structure returns early without driver."""
        store = DSCNeo4jStore()

        # Should not raise exception
        result = store.store_code_structure("test.py", {})
        assert result is None

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_store_code_structure_with_complete_ast(self, mock_graph_db):
        """Test storing complete AST data."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()  # Clear setup calls

        ast_data = {
            "lines": 100,
            "complexity": 5,
            "classes": [
                {
                    "name": "TestClass",
                    "methods": ["method1", "method2"],
                    "lines": 50,
                    "docstring": "Test class docstring",
                }
            ],
            "functions": [
                {
                    "name": "test_function",
                    "params": ["arg1", "arg2"],
                    "lines": 10,
                    "complexity": 2,
                    "docstring": "Test function",
                }
            ],
            "imports": ["os", "sys", "json"],
        }

        store.store_code_structure("/path/to/test.py", ast_data)

        # Verify queries were executed
        calls = mock_session.run.call_args_list

        # Should have: 1 module + 1 class + 1 function + 3 imports = 6 queries
        assert len(calls) >= 6

        # Verify module creation
        module_call = calls[0]
        assert "Module" in module_call.args[0]
        module_params = module_call.args[1] if len(module_call.args) > 1 else module_call.kwargs
        assert module_params["path"] == "/path/to/test.py"
        assert module_params["lines"] == 100

        # Verify class creation
        class_call = calls[1]
        assert "Class" in class_call.args[0]
        class_params = class_call.args[1] if len(class_call.args) > 1 else class_call.kwargs
        assert class_params["name"] == "TestClass"
        assert class_params["lines"] == 50

        # Verify function creation
        func_call = calls[2]
        assert "Function" in func_call.args[0]
        func_params = func_call.args[1] if len(func_call.args) > 1 else func_call.kwargs
        assert func_params["name"] == "test_function"
        assert func_params["complexity"] == 2

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_store_code_structure_with_minimal_ast(self, mock_graph_db):
        """Test storing AST with minimal data."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        # Empty AST data
        ast_data = {"classes": [], "functions": [], "imports": []}

        store.store_code_structure("minimal.py", ast_data)

        # Should only create module
        calls = mock_session.run.call_args_list
        assert len(calls) == 1  # Only module creation


class TestDSCFieldStorage:
    """Test suite for DSC field state storage."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", False)
    def test_store_field_state_without_driver(self):
        """Test field state storage without driver."""
        store = DSCNeo4jStore()
        result = store.store_dsc_field_state("chunk_1", {})
        assert result is None

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_store_field_state_complete(self, mock_graph_db):
        """Test storing complete field state."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        field_state = {
            "semantic": 0.8,
            "emotional": 0.6,
            "ethical": 0.9,
            "temporal": 0.7,
            "contradiction": 0.3,
            "relational": 0.85,
            "entropy": 0.4,
            "coherence": 0.95,
        }

        store.store_dsc_field_state("chunk_123", field_state)

        # Verify query execution
        calls = mock_session.run.call_args_list
        assert len(calls) == 1

        call = calls[0]
        assert "FieldState" in call.args[0]
        assert "HAS_FIELD_STATE" in call.args[0]
        params = call.args[1] if len(call.args) > 1 else call.kwargs
        assert params["chunk_id"] == "chunk_123"
        assert params["semantic"] == 0.8
        assert params["coherence"] == 0.95

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_store_field_state_with_defaults(self, mock_graph_db):
        """Test storing field state with default values."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        # Partial field state
        field_state = {"semantic": 0.5}

        store.store_dsc_field_state("chunk_456", field_state)

        call = mock_session.run.call_args_list[0]
        params = call.args[1] if len(call.args) > 1 else call.kwargs
        # Should use 0.0 defaults for missing fields
        assert params["semantic"] == 0.5
        assert params["emotional"] == 0.0
        assert params["ethical"] == 0.0


class TestFractalPatternStorage:
    """Test suite for fractal pattern storage."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", False)
    def test_store_pattern_without_driver(self):
        """Test pattern storage without driver."""
        store = DSCNeo4jStore()
        result = store.store_fractal_pattern({})
        assert result is None

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_store_fractal_pattern_complete(self, mock_graph_db):
        """Test storing complete fractal pattern."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        pattern = {
            "type": "recursion",
            "scale": 3,
            "frequency": 5,
            "locations": ["/path/a.py", "/path/b.py"],
            "confidence": 0.87,
        }

        store.store_fractal_pattern(pattern)

        # Should create pattern node and link to modules
        calls = mock_session.run.call_args_list
        assert len(calls) == 3  # 1 pattern + 2 location links

        # Verify pattern creation
        pattern_call = calls[0]
        assert "Pattern" in pattern_call.args[0]
        pattern_params = pattern_call.args[1] if len(pattern_call.args) > 1 else pattern_call.kwargs
        assert pattern_params["type"] == "recursion"
        assert pattern_params["confidence"] == 0.87

        # Verify location links
        for i, location in enumerate(pattern["locations"], 1):
            link_call = calls[i]
            assert "EXHIBITS_PATTERN" in link_call.args[0]
            link_params = link_call.args[1] if len(link_call.args) > 1 else link_call.kwargs
            assert link_params["module_path"] == location

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_store_pattern_generates_consistent_id(self, mock_graph_db):
        """Test that identical patterns generate same ID."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")

        pattern1 = {"type": "test", "scale": 1}
        pattern2 = {"scale": 1, "type": "test"}  # Different order

        mock_session.run.reset_mock()
        store.store_fractal_pattern(pattern1)
        params1 = (
            mock_session.run.call_args_list[0].args[1]
            if len(mock_session.run.call_args_list[0].args) > 1
            else mock_session.run.call_args_list[0].kwargs
        )
        id1 = params1["id"]

        mock_session.run.reset_mock()
        store.store_fractal_pattern(pattern2)
        params2 = (
            mock_session.run.call_args_list[0].args[1]
            if len(mock_session.run.call_args_list[0].args) > 1
            else mock_session.run.call_args_list[0].kwargs
        )
        id2 = params2["id"]

        # Should generate same ID regardless of dict order
        assert id1 == id2


class TestBlessingStorage:
    """Test suite for blessing vector storage."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", False)
    def test_store_blessing_without_driver(self):
        """Test blessing storage without driver."""
        store = DSCNeo4jStore()
        result = store.store_blessing_vector("entity_1", {})
        assert result is None

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_store_blessing_vector_complete(self, mock_graph_db):
        """Test storing complete blessing vector."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        blessing = {"tier": "Ω", "epc": 0.92, "ethics": 0.88, "coherence": 0.95, "presence": 0.87}

        store.store_blessing_vector("entity_xyz", blessing)

        call = mock_session.run.call_args_list[0]
        assert "Blessing" in call.args[0]
        assert "HAS_BLESSING" in call.args[0]
        params = call.args[1] if len(call.args) > 1 else call.kwargs
        assert params["entity_id"] == "entity_xyz"
        assert params["tier"] == "Ω"
        assert params["epc"] == 0.92


class TestNetworkXIntegration:
    """Test suite for NetworkX graph storage."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", False)
    def test_store_networkx_without_driver(self):
        """Test NetworkX storage without driver."""
        store = DSCNeo4jStore()
        result = store.store_networkx_graph(None, "test")
        assert result is None

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.nx")
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_store_networkx_graph(self, mock_graph_db, mock_nx):
        """Test storing NetworkX graph."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        # Create mock NetworkX graph
        mock_graph = MagicMock()
        mock_graph.nodes.return_value = [
            ("node1", {"attr1": "value1"}),
            ("node2", {"attr2": "value2"}),
        ]
        mock_graph.edges.return_value = [("node1", "node2", {"weight": 0.5})]

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        store.store_networkx_graph(mock_graph, "dependency")

        # Should create 2 nodes + 1 edge = 3 queries
        calls = mock_session.run.call_args_list
        assert len(calls) == 3

        # Verify node creation
        assert "GraphNode" in calls[0].args[0]
        params = calls[0].args[1] if len(calls[0].args) > 1 else calls[0].kwargs
        assert params["id"] == "node1"
        assert params["graph_type"] == "dependency"


class TestQueryMethods:
    """Test suite for query methods."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", False)
    def test_query_pattern_clusters_without_driver(self):
        """Test query without driver returns empty list."""
        store = DSCNeo4jStore()
        result = store.query_pattern_clusters()
        assert result == []

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_query_pattern_clusters(self, mock_graph_db):
        """Test querying pattern clusters."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        # Mock query result
        mock_records = [
            {
                "pattern_type": "recursion",
                "confidence": 0.85,
                "affected_modules": 3,
                "module_paths": ["/a.py", "/b.py", "/c.py"],
            }
        ]
        mock_result.__iter__.return_value = iter(mock_records)
        mock_session.run.return_value = mock_result

        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        results = store.query_pattern_clusters()

        assert len(results) == 1
        assert results[0]["pattern_type"] == "recursion"
        assert results[0]["affected_modules"] == 3

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_find_code_smells(self, mock_graph_db):
        """Test finding code smells."""
        mock_driver = MagicMock()
        mock_session = MagicMock()

        # Mock different smell queries
        def run_side_effect(query):
            mock_result = MagicMock()
            if "circular_dependency" in query or "IMPORTS" in query:
                records = [{"module1": "a.py", "module2": "b.py", "smell": "circular_dependency"}]
            elif "god_class" in query:
                records = [
                    {
                        "class_name": "GodClass",
                        "module": "big.py",
                        "method_count": 25,
                        "smell": "god_class",
                    }
                ]
            elif "long_function" in query:
                records = [
                    {
                        "function": "huge_func",
                        "module": "messy.py",
                        "lines": 100,
                        "complexity": 15,
                        "smell": "long_function",
                    }
                ]
            else:
                records = []
            mock_result.__iter__.return_value = iter(records)
            return mock_result

        mock_session.run.side_effect = run_side_effect
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")

        smells = store.find_code_smells()

        # Should find all three types of smells
        assert len(smells) == 3
        smell_types = [s["smell"] for s in smells]
        assert "circular_dependency" in smell_types
        assert "god_class" in smell_types
        assert "long_function" in smell_types

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_get_evolution_timeline(self, mock_graph_db):
        """Test getting entity evolution timeline."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_records = [
            {
                "state": {"semantic": 0.8, "timestamp": "2024-01-01T12:00:00"},
                "type": ["FieldState"],
            },
            {"state": {"tier": "Ω", "timestamp": "2024-01-01T11:00:00"}, "type": ["Blessing"]},
        ]

        mock_result.__iter__.return_value = iter(mock_records)
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        timeline = store.get_evolution_timeline("entity_123")

        assert len(timeline) == 2
        assert timeline[0]["type"] == "FieldState"
        assert timeline[1]["type"] == "Blessing"
        assert "timestamp" in timeline[0]


class TestCloseMethod:
    """Test suite for connection closure."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", False)
    def test_close_without_driver(self):
        """Test close without driver doesn't raise exception."""
        store = DSCNeo4jStore()
        store.close()  # Should not raise

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_close_with_driver(self, mock_graph_db, caplog):
        """Test close closes driver connection."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        # Clear any logs from initialization
        caplog.clear()

        store = DSCNeo4jStore(password="test_password")
        caplog.clear()  # Clear again after init

        store.close()

        mock_driver.close.assert_called_once()
        # Logger may or may not be captured, just check driver.close was called
        assert mock_driver.close.called


class TestUnifiedGraphStore:
    """Test suite for UnifiedGraphStore."""

    @patch("pbjrag.dsc.neo4j_store.DSCNeo4jStore")
    def test_unified_store_init_neo4j_only(self, mock_neo4j_class):
        """Test unified store with Neo4j only."""
        config = {
            "enable_neo4j": True,
            "neo4j_uri": "bolt://localhost:7687",
            "neo4j_user": "neo4j",
            "neo4j_password": "password",
            "enable_qdrant": False,
            "enable_chroma": False,
        }

        store = UnifiedGraphStore(config)

        mock_neo4j_class.assert_called_once_with(
            uri="bolt://localhost:7687", user="neo4j", password="password"
        )
        assert store.neo4j is not None
        assert store.qdrant is None
        assert store.chroma is None

    @patch("pbjrag.dsc.neo4j_store.DSCNeo4jStore")
    def test_unified_store_disabled_neo4j(self, mock_neo4j_class):
        """Test unified store with Neo4j disabled."""
        config = {"enable_neo4j": False}

        store = UnifiedGraphStore(config)

        mock_neo4j_class.assert_not_called()
        assert store.neo4j is None

    @patch("pbjrag.dsc.neo4j_store.DSCNeo4jStore")
    def test_store_analysis_neo4j(self, mock_neo4j_class):
        """Test storing analysis results in Neo4j."""
        mock_neo4j = MagicMock()
        mock_neo4j_class.return_value = mock_neo4j

        config = {"enable_neo4j": True, "neo4j_password": "test"}
        store = UnifiedGraphStore(config)

        analysis_results = {
            "file_path": "/test.py",
            "ast_data": {"classes": [], "functions": []},
            "patterns": [{"type": "test", "confidence": 0.9}],
        }

        store.store_analysis(analysis_results)

        # Verify Neo4j methods were called
        mock_neo4j.store_code_structure.assert_called_once_with(
            "/test.py", {"classes": [], "functions": []}
        )
        mock_neo4j.store_fractal_pattern.assert_called_once()

    @patch("pbjrag.dsc.neo4j_store.DSCNeo4jStore")
    def test_query_unified_neo4j_only(self, mock_neo4j_class):
        """Test unified query with Neo4j only."""
        mock_neo4j = MagicMock()
        mock_neo4j.query_pattern_clusters.return_value = [{"pattern": "test"}]
        mock_neo4j.find_code_smells.return_value = [{"smell": "god_class"}]
        mock_neo4j_class.return_value = mock_neo4j

        config = {
            "enable_neo4j": True,
            "neo4j_password": "test",
            "enable_qdrant": False,  # Disable Qdrant to avoid import issues
            "enable_chroma": False,
        }
        store = UnifiedGraphStore(config)

        results = store.query_unified("test query")

        assert "patterns" in results
        assert "smells" in results
        assert len(results["patterns"]) == 1
        assert len(results["smells"]) == 1


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_empty_ast_data(self, mock_graph_db):
        """Test handling empty AST data."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        # Should not raise exception
        store.store_code_structure("empty.py", {})

        # Should still create module
        assert mock_session.run.called

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_malformed_pattern_data(self, mock_graph_db):
        """Test handling malformed pattern data."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        # Pattern with missing fields
        pattern = {"type": "incomplete"}

        # Should use defaults for missing fields
        store.store_fractal_pattern(pattern)

        call = mock_session.run.call_args_list[0]
        params = call.args[1] if len(call.args) > 1 else call.kwargs
        assert params["type"] == "incomplete"
        assert params["scale"] == 1  # Default
        assert params["confidence"] == 0.0  # Default

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_special_characters_in_paths(self, mock_graph_db):
        """Test handling special characters in file paths."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        # Path with special characters
        path = "/path/with spaces/and'quotes/test.py"

        store.store_code_structure(path, {"lines": 10})

        call = mock_session.run.call_args_list[0]
        params = call.args[1] if len(call.args) > 1 else call.kwargs
        assert params["path"] == path

    @patch("pbjrag.dsc.neo4j_store.HAVE_NEO4J", True)
    @patch("pbjrag.dsc.neo4j_store.GraphDatabase")
    def test_very_large_ast_data(self, mock_graph_db):
        """Test handling very large AST data."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        store = DSCNeo4jStore(password="test_password")
        mock_session.run.reset_mock()

        # Large AST with many classes and functions
        ast_data = {
            "classes": [{"name": f"Class{i}", "methods": []} for i in range(50)],
            "functions": [{"name": f"func{i}"} for i in range(100)],
            "imports": [f"module{i}" for i in range(200)],
        }

        store.store_code_structure("large.py", ast_data)

        # Should handle all entries
        calls = mock_session.run.call_args_list
        # 1 module + 50 classes + 100 functions + 200 imports = 351
        assert len(calls) == 351
