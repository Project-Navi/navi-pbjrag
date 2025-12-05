#!/usr/bin/env python3
"""
Neo4j Graph Store for PBJRAG v3
Stores code relationships, patterns, and DSC field states as a knowledge graph
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Any

try:
    import networkx as nx
    from neo4j import GraphDatabase

    HAVE_NEO4J = True
except ImportError:
    HAVE_NEO4J = False
    GraphDatabase = None
    nx = None

logger = logging.getLogger(__name__)


class DSCNeo4jStore:
    """
    Neo4j adapter for storing code analysis as a knowledge graph.
    Integrates with NetworkX for graph algorithms.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str | None = None,
        database: str = "neo4j",
    ):
        """Initialize Neo4j connection.

        Password can be provided directly or via NEO4J_PASSWORD environment variable.
        """
        if not HAVE_NEO4J:
            logger.warning("Neo4j driver not available. Install with: pip install neo4j")
            self.driver = None
            return

        # Get password from environment variable if not provided
        actual_password = password or os.environ.get("NEO4J_PASSWORD")
        if not actual_password:
            logger.error(
                "Neo4j password not provided. Set NEO4J_PASSWORD environment variable "
                "or pass password parameter."
            )
            self.driver = None
            return

        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, actual_password))
            self.database = database

            # Test connection
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")

            logger.info(f"Connected to Neo4j at {uri}")

            # Create indexes and constraints
            self._setup_schema()

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def _setup_schema(self):
        """Create indexes and constraints for optimal performance"""
        with self.driver.session(database=self.database) as session:
            # Indexes for different node types
            queries = [
                # Code structure nodes
                "CREATE INDEX IF NOT EXISTS FOR (n:Module) ON (n.path)",
                "CREATE INDEX IF NOT EXISTS FOR (n:Class) ON (n.name)",
                "CREATE INDEX IF NOT EXISTS FOR (n:Function) ON (n.name)",
                "CREATE INDEX IF NOT EXISTS FOR (n:Pattern) ON (n.type)",
                # DSC field nodes
                "CREATE INDEX IF NOT EXISTS FOR (n:FieldState) ON (n.timestamp)",
                "CREATE INDEX IF NOT EXISTS FOR (n:Blessing) ON (n.tier)",
                "CREATE INDEX IF NOT EXISTS FOR (n:Phase) ON (n.name)",
                # Vector/embedding nodes
                "CREATE INDEX IF NOT EXISTS FOR (n:Chunk) ON (n.id)",
                "CREATE INDEX IF NOT EXISTS FOR (n:Embedding) ON (n.model)",
                # Constraints for uniqueness
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Module) REQUIRE n.path IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Chunk) REQUIRE n.id IS UNIQUE",
            ]

            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    logger.warning(f"Schema setup query failed: {e}")

    def store_code_structure(self, file_path: str, ast_data: dict[str, Any]):
        """
        Store AST structure as a graph

        Creates nodes for:
        - Module (file)
        - Classes
        - Functions
        - Imports

        Creates relationships:
        - CONTAINS (Module -> Class/Function)
        - DEFINES (Class -> Method)
        - IMPORTS (Module -> Module)
        - CALLS (Function -> Function)
        """
        if not self.driver:
            return

        with self.driver.session(database=self.database) as session:
            # Create module node
            module_query = """
            MERGE (m:Module {path: $path})
            SET m.name = $name,
                m.lines = $lines,
                m.complexity = $complexity,
                m.analyzed_at = datetime()
            RETURN m
            """

            session.run(
                module_query,
                {
                    "path": file_path,
                    "name": file_path.split("/")[-1],
                    "lines": ast_data.get("lines", 0),
                    "complexity": ast_data.get("complexity", 0),
                },
            )

            # Create class nodes and relationships
            for class_info in ast_data.get("classes", []):
                class_query = """
                MATCH (m:Module {path: $module_path})
                MERGE (c:Class {name: $name, module: $module_path})
                SET c.methods = $methods,
                    c.lines = $lines,
                    c.docstring = $docstring
                MERGE (m)-[:CONTAINS]->(c)
                """

                session.run(
                    class_query,
                    {
                        "module_path": file_path,
                        "name": class_info["name"],
                        "methods": len(class_info.get("methods", [])),
                        "lines": class_info.get("lines", 0),
                        "docstring": class_info.get("docstring", ""),
                    },
                )

            # Create function nodes
            for func_info in ast_data.get("functions", []):
                func_query = """
                MATCH (m:Module {path: $module_path})
                MERGE (f:Function {name: $name, module: $module_path})
                SET f.params = $params,
                    f.lines = $lines,
                    f.complexity = $complexity,
                    f.docstring = $docstring
                MERGE (m)-[:CONTAINS]->(f)
                """

                session.run(
                    func_query,
                    {
                        "module_path": file_path,
                        "name": func_info["name"],
                        "params": func_info.get("params", []),
                        "lines": func_info.get("lines", 0),
                        "complexity": func_info.get("complexity", 0),
                        "docstring": func_info.get("docstring", ""),
                    },
                )

            # Create import relationships
            for import_name in ast_data.get("imports", []):
                import_query = """
                MATCH (m:Module {path: $module_path})
                MERGE (i:Module {name: $import_name})
                MERGE (m)-[:IMPORTS]->(i)
                """

                session.run(import_query, {"module_path": file_path, "import_name": import_name})

    def store_dsc_field_state(self, chunk_id: str, field_state: dict[str, float]):
        """
        Store DSC field state as a node with 6 dimensions
        """
        if not self.driver:
            return

        with self.driver.session(database=self.database) as session:
            query = """
            MERGE (c:Chunk {id: $chunk_id})
            CREATE (f:FieldState {
                timestamp: datetime(),
                semantic: $semantic,
                emotional: $emotional,
                ethical: $ethical,
                temporal: $temporal,
                contradiction: $contradiction,
                relational: $relational,
                entropy: $entropy,
                coherence: $coherence
            })
            MERGE (c)-[:HAS_FIELD_STATE]->(f)
            """

            session.run(
                query,
                {
                    "chunk_id": chunk_id,
                    "semantic": field_state.get("semantic", 0.0),
                    "emotional": field_state.get("emotional", 0.0),
                    "ethical": field_state.get("ethical", 0.0),
                    "temporal": field_state.get("temporal", 0.0),
                    "contradiction": field_state.get("contradiction", 0.0),
                    "relational": field_state.get("relational", 0.0),
                    "entropy": field_state.get("entropy", 0.0),
                    "coherence": field_state.get("coherence", 0.0),
                },
            )

    def store_fractal_pattern(self, pattern: dict[str, Any]):
        """
        Store fractal pattern detection results
        """
        if not self.driver:
            return

        pattern_id = hashlib.md5(json.dumps(pattern, sort_keys=True).encode()).hexdigest()

        with self.driver.session(database=self.database) as session:
            query = """
            MERGE (p:Pattern {id: $id})
            SET p.type = $type,
                p.scale = $scale,
                p.frequency = $frequency,
                p.locations = $locations,
                p.confidence = $confidence,
                p.detected_at = datetime()
            """

            session.run(
                query,
                {
                    "id": pattern_id,
                    "type": pattern.get("type", "unknown"),
                    "scale": pattern.get("scale", 1),
                    "frequency": pattern.get("frequency", 1),
                    "locations": pattern.get("locations", []),
                    "confidence": pattern.get("confidence", 0.0),
                },
            )

            # Link pattern to affected modules
            for location in pattern.get("locations", []):
                link_query = """
                MATCH (p:Pattern {id: $pattern_id})
                MATCH (m:Module {path: $module_path})
                MERGE (m)-[:EXHIBITS_PATTERN]->(p)
                """

                session.run(link_query, {"pattern_id": pattern_id, "module_path": location})

    def store_blessing_vector(self, entity_id: str, blessing: dict[str, Any]):
        """
        Store blessing vector calculation
        """
        if not self.driver:
            return

        with self.driver.session(database=self.database) as session:
            query = """
            MERGE (e:Entity {id: $entity_id})
            CREATE (b:Blessing {
                tier: $tier,
                epc: $epc,
                ethics: $ethics,
                coherence: $coherence,
                presence: $presence,
                timestamp: datetime()
            })
            MERGE (e)-[:HAS_BLESSING]->(b)
            """

            session.run(
                query,
                {
                    "entity_id": entity_id,
                    "tier": blessing.get("tier", "Φ"),
                    "epc": blessing.get("epc", 0.0),
                    "ethics": blessing.get("ethics", 0.0),
                    "coherence": blessing.get("coherence", 0.0),
                    "presence": blessing.get("presence", 0.0),
                },
            )

    def store_networkx_graph(self, graph: "nx.Graph", graph_type: str = "dependency"):
        """
        Convert and store a NetworkX graph in Neo4j
        """
        if not self.driver or not nx:
            return

        with self.driver.session(database=self.database) as session:
            # Store nodes
            for node, attrs in graph.nodes(data=True):
                node_query = """
                MERGE (n:GraphNode {id: $id, graph_type: $graph_type})
                SET n += $properties
                """

                properties = attrs.copy()
                properties["created_at"] = datetime.now().isoformat()

                session.run(
                    node_query,
                    {"id": str(node), "graph_type": graph_type, "properties": properties},
                )

            # Store edges
            for source, target, attrs in graph.edges(data=True):
                edge_query = """
                MATCH (s:GraphNode {id: $source, graph_type: $graph_type})
                MATCH (t:GraphNode {id: $target, graph_type: $graph_type})
                MERGE (s)-[r:CONNECTED {graph_type: $graph_type}]->(t)
                SET r += $properties
                """

                properties = attrs.copy()
                properties["created_at"] = datetime.now().isoformat()

                session.run(
                    edge_query,
                    {
                        "source": str(source),
                        "target": str(target),
                        "graph_type": graph_type,
                        "properties": properties,
                    },
                )

    def query_pattern_clusters(self) -> list[dict[str, Any]]:
        """
        Find clusters of related patterns using graph algorithms
        """
        if not self.driver:
            return []

        with self.driver.session(database=self.database) as session:
            query = """
            MATCH (m:Module)-[:EXHIBITS_PATTERN]->(p:Pattern)
            WITH p, collect(m) as modules
            WHERE size(modules) > 1
            RETURN p.type as pattern_type,
                   p.confidence as confidence,
                   size(modules) as affected_modules,
                   [m in modules | m.path] as module_paths
            ORDER BY affected_modules DESC
            LIMIT 10
            """

            result = session.run(query)
            return [dict(record) for record in result]

    def find_code_smells(self) -> list[dict[str, Any]]:
        """
        Query for potential code smells using graph patterns
        """
        if not self.driver:
            return []

        with self.driver.session(database=self.database) as session:
            # Find circular dependencies
            circular_query = """
            MATCH (m1:Module)-[:IMPORTS]->(m2:Module)-[:IMPORTS]->(m1)
            RETURN m1.path as module1, m2.path as module2, 'circular_dependency' as smell
            """

            # Find god classes (classes with too many methods)
            god_class_query = """
            MATCH (c:Class)
            WHERE c.methods > 20
            RETURN c.name as class_name, c.module as module,
                   c.methods as method_count, 'god_class' as smell
            """

            # Find long functions
            long_func_query = """
            MATCH (f:Function)
            WHERE f.lines > 50 OR f.complexity > 10
            RETURN f.name as function, f.module as module,
                   f.lines as lines, f.complexity as complexity, 'long_function' as smell
            """

            smells = []
            for query in [circular_query, god_class_query, long_func_query]:
                result = session.run(query)
                smells.extend([dict(record) for record in result])

            return smells

    def get_evolution_timeline(self, entity_id: str) -> list[dict[str, Any]]:
        """
        Get the evolution timeline of an entity's field states and blessings
        """
        if not self.driver:
            return []

        with self.driver.session(database=self.database) as session:
            query = """
            MATCH (e:Entity {id: $entity_id})-[:HAS_FIELD_STATE|HAS_BLESSING]->(state)
            RETURN state, labels(state) as type
            ORDER BY state.timestamp DESC
            LIMIT 50
            """

            result = session.run(query, {"entity_id": entity_id})
            timeline = []

            for record in result:
                state_data = dict(record["state"])
                state_data["type"] = record["type"][0] if record["type"] else "unknown"
                timeline.append(state_data)

            return timeline

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")


# Integration with existing vector stores
class UnifiedGraphStore:
    """
    Unified store combining Neo4j (graph), Qdrant (vectors), and ChromaDB (documents)
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize all storage backends"""
        self.neo4j = None
        self.qdrant = None
        self.chroma = None

        # Initialize Neo4j
        if config.get("enable_neo4j", True):
            self.neo4j = DSCNeo4jStore(
                uri=config.get("neo4j_uri", "bolt://localhost:7687"),
                user=config.get("neo4j_user", "neo4j"),
                password=config.get("neo4j_password", "password"),
            )

        # Import and initialize other stores
        if config.get("enable_qdrant", True):
            from .vector_store import DSCVectorStore

            self.qdrant = DSCVectorStore(
                qdrant_host=config.get("qdrant_host", "localhost"),
                qdrant_port=config.get("qdrant_port", 6333),
            )

        if config.get("enable_chroma", False):
            from .chroma_store import DSCChromaStore

            self.chroma = DSCChromaStore(chroma_path=config.get("chroma_path", "./chroma_db"))

    def store_analysis(self, analysis_results: dict[str, Any]):
        """Store analysis results across all backends"""

        # Store structure in Neo4j
        if self.neo4j and "ast_data" in analysis_results:
            self.neo4j.store_code_structure(
                analysis_results["file_path"], analysis_results["ast_data"]
            )

        # Store patterns in Neo4j
        if self.neo4j and "patterns" in analysis_results:
            for pattern in analysis_results["patterns"]:
                self.neo4j.store_fractal_pattern(pattern)

        # Store embeddings in Qdrant
        if self.qdrant and "chunks" in analysis_results:
            self.qdrant.add_chunks(analysis_results["chunks"])

        # Store documents in Chroma
        if self.chroma and "documents" in analysis_results:
            self.chroma.add_documents(analysis_results["documents"])

    def query_unified(self, query: str) -> dict[str, Any]:
        """Query across all storage backends"""
        results = {}

        # Graph queries
        if self.neo4j:
            results["patterns"] = self.neo4j.query_pattern_clusters()
            results["smells"] = self.neo4j.find_code_smells()

        # Vector search
        if self.qdrant:
            results["semantic_matches"] = self.qdrant.search(query, limit=5)

        # Document search
        if self.chroma:
            results["documents"] = self.chroma.query(query, n_results=5)

        return results
