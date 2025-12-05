#!/usr/bin/env python3
"""
DSC Code Chunker - Migrated from PBJRAG-2 and integrated with Crown Jewel Core

This integrates the mathematical precision of PBJRAG-2's DSC chunker with
Crown Jewel Core's coherence curves and field management.
"""

import ast
import re
from dataclasses import dataclass
from typing import Any

import numpy as np

from pbjrag.crown_jewel.field_container import FieldContainer

# Import from crown_jewel_core
from pbjrag.crown_jewel.metrics import CoreMetrics, create_blessing_vector


@dataclass
class FieldState:
    """Multi-dimensional field representation of code"""

    semantic: np.ndarray  # Meaning and purpose
    emotional: np.ndarray  # Developer intent and feeling
    ethical: np.ndarray  # Quality and best practices
    temporal: np.ndarray  # Evolution and change patterns
    entropic: np.ndarray  # Chaos and unpredictability
    rhythmic: np.ndarray  # Cadence and flow
    contradiction: np.ndarray  # Tensions and conflicts
    relational: np.ndarray  # Dependencies and connections
    emergent: np.ndarray  # Novelty and surprise

    @property
    def dimension(self) -> int:
        return self.semantic.shape[0]

    def to_dict(self) -> dict[str, list[float]]:
        """Convert to dictionary for JSON serialization"""
        return {
            "semantic": self.semantic.tolist(),
            "emotional": self.emotional.tolist(),
            "ethical": self.ethical.tolist(),
            "temporal": self.temporal.tolist(),
            "entropic": self.entropic.tolist(),
            "rhythmic": self.rhythmic.tolist(),
            "contradiction": self.contradiction.tolist(),
            "relational": self.relational.tolist(),
            "emergent": self.emergent.tolist(),
        }


@dataclass
class BlessingState:
    """Blessing calculation results - now integrated with CoreMetrics"""

    tier: str  # Φ+, Φ~, Φ-
    epc: float  # Emergence Potential Coefficient
    ethical_alignment: float
    contradiction_pressure: float
    presence_density: float
    resonance_score: float
    phase: str  # compost, reflection, becoming, stillness, turning, emergent, grinding

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "tier": self.tier,
            "epc": self.epc,
            "ethical_alignment": self.ethical_alignment,
            "contradiction_pressure": self.contradiction_pressure,
            "presence_density": self.presence_density,
            "resonance_score": self.resonance_score,
            "phase": self.phase,
        }


@dataclass
class DSCChunk:
    """A chunk with full DSC field analysis"""

    content: str
    start_line: int
    end_line: int
    field_state: FieldState
    blessing: BlessingState
    chunk_type: str  # function, class, module, etc.
    provides: list[str]  # What this chunk offers
    depends_on: list[str]  # What this chunk needs
    file_path: str | None = None  # Added for crown_jewel integration

    def to_fragment(self) -> dict[str, Any]:
        """Convert to crown_jewel fragment format"""
        return {
            "content": self.content,
            "file": self.file_path or "",
            "start_line": self.start_line,
            "end_line": self.end_line,
            "chunk_type": self.chunk_type,
            "provides": self.provides,
            "depends_on": self.depends_on,
            "field_state": self.field_state.to_dict(),
            "blessing": create_blessing_vector(
                cadence=1.0 - self.blessing.contradiction_pressure,
                qualia=self.blessing.ethical_alignment,
                entropy=np.mean(self.field_state.semantic[:2]),
                contradiction=self.blessing.contradiction_pressure,
                presence=self.blessing.presence_density,
            ),
            "dsc_blessing": self.blessing.to_dict(),
        }


class DSCCodeChunker:
    """
    Enhanced DSC chunker integrated with Crown Jewel Core's metrics system.
    """

    def __init__(self, field_dim: int = 8, field_container: FieldContainer | None = None):
        """Initialize with field dimension and optional field container"""
        self.field_dim = field_dim
        self.field_container = field_container or FieldContainer()
        self.metrics = CoreMetrics()

        # Phase boundaries from DSC
        self.phase_boundaries = {
            "compost": (0.0, 0.2),
            "reflection": (0.2, 0.35),
            "becoming": (0.35, 0.5),
            "stillness": (0.5, 0.65),
            "turning": (0.65, 0.8),
            "emergent": (0.8, 0.9),
            "grinding": (0.9, 1.0),
        }

    def chunk_code(self, code: str, filepath: str = "") -> list[DSCChunk]:
        """Main entry point - chunk code using DSC principles"""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Handle malformed code
            chunk = self._create_malformed_chunk(code)
            chunk.file_path = filepath

            # Add to field container
            self.field_container.add_fragment(chunk.to_fragment())

            return [chunk]

        chunks = []
        lines = code.split("\n")

        # Extract different code elements
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunk = self._create_function_chunk(node, lines, tree)
                chunk.file_path = filepath
                chunks.append(chunk)
            elif isinstance(node, ast.ClassDef):
                chunk = self._create_class_chunk(node, lines, tree)
                chunk.file_path = filepath
                chunks.append(chunk)

        # Add module-level chunk if there's code outside functions/classes
        module_chunk = self._create_module_chunk(tree, lines, chunks)
        if module_chunk:
            module_chunk.file_path = filepath
            chunks.append(module_chunk)

        # Add all chunks to field container
        for chunk in chunks:
            fragment = chunk.to_fragment()
            self.field_container.add_fragment(fragment)

            # Also detect patterns if we have enough chunks
            if len(self.field_container.fragments) >= 2:
                self._detect_and_store_patterns()

        return chunks

    def _detect_and_store_patterns(self):
        """Detect patterns in current fragments and store in field container"""
        fragments = self.field_container.get_fragments()

        # Group similar fragments
        similar_groups = self._find_similar_fragments(fragments)

        for group in similar_groups:
            if len(group) >= 2:
                # Calculate group blessing using CoreMetrics
                blessings = [f.get("blessing", {}) for f in group]
                group_coherence = self.metrics.coherence_vector(blessings)

                pattern = {
                    "type": "similarity_pattern",
                    "fragments": [f.get("file", "") for f in group],
                    "coherence": group_coherence,
                    "blessing": group_coherence,
                }

                self.field_container.add_pattern(pattern)

    def _find_similar_fragments(
        self, fragments: list[dict[str, Any]]
    ) -> list[list[dict[str, Any]]]:
        """Find groups of similar fragments"""
        groups = []
        used = set()

        for i, frag1 in enumerate(fragments):
            if i in used:
                continue

            group = [frag1]
            used.add(i)

            blessing1 = frag1.get("blessing", {})

            for j, frag2 in enumerate(fragments[i + 1 :], i + 1):
                if j in used:
                    continue

                blessing2 = frag2.get("blessing", {})

                # Simple similarity based on blessing tier and EPC
                if (
                    blessing1.get("Φ") == blessing2.get("Φ")
                    and abs(blessing1.get("epc", 0) - blessing2.get("epc", 0)) < 0.1
                ):
                    group.append(frag2)
                    used.add(j)

            if len(group) >= 2:
                groups.append(group)

        return groups

    def _create_function_chunk(
        self, node: ast.FunctionDef, lines: list[str], tree: ast.AST
    ) -> DSCChunk:
        """Create a chunk for a function with full DSC analysis"""
        start_line = node.lineno - 1
        end_line = getattr(node, "end_lineno", start_line + 1)
        content = "\n".join(lines[start_line:end_line])

        # Extract field state
        field_state = self._extract_field_state(node, content, tree)

        # Calculate blessing using Crown Jewel's enhanced metrics
        blessing = self._calculate_blessing_enhanced(field_state, node, content, tree)

        # Extract dependencies
        deps = self._extract_dependencies(node)

        return DSCChunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            field_state=field_state,
            blessing=blessing,
            chunk_type="function",
            provides=[node.name],
            depends_on=deps,
        )

    def _create_class_chunk(self, node: ast.ClassDef, lines: list[str], tree: ast.AST) -> DSCChunk:
        """Create a chunk for a class with full DSC analysis"""
        start_line = node.lineno - 1
        end_line = getattr(node, "end_lineno", start_line + 1)
        content = "\n".join(lines[start_line:end_line])

        # Extract field state
        field_state = self._extract_field_state(node, content, tree)

        # Calculate blessing
        blessing = self._calculate_blessing_enhanced(field_state, node, content, tree)

        # Extract what this class provides
        provides = [node.name]
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                provides.append(f"{node.name}.{item.name}")

        # Extract dependencies
        deps = self._extract_dependencies(node)

        return DSCChunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            field_state=field_state,
            blessing=blessing,
            chunk_type="class",
            provides=provides,
            depends_on=deps,
        )

    def _calculate_blessing_enhanced(
        self, field_state: FieldState, node: ast.AST, content: str, tree: ast.AST
    ) -> BlessingState:
        """
        Calculate blessing, now modulated by relational coherence.
        A chunk's quality depends on both its internal state and its role in the whole.
        """
        # 1. Calculate internal metrics
        ethical_alignment = np.mean(field_state.ethical)
        contradiction_pressure = np.mean(field_state.contradiction)

        # Presence density (documentation + clarity)
        docstring = ""
        if isinstance(node, ast.AST) and hasattr(node, "body"):
            try:
                docstring = ast.get_docstring(node)
            except TypeError:
                docstring = ""
        doc_lines = len(docstring.split("\n")) if docstring else 0
        comment_lines = content.count("#")
        total_lines = content.count("\n") + 1
        presence_density = (doc_lines + comment_lines) / max(total_lines, 1)

        # 2. Calculate Relational Coherence Modifier
        # How well is this chunk integrated into the whole?
        relational_mean = np.mean(field_state.relational)

        # An isolated chunk (low relational score) is penalized.
        # A highly coupled chunk is also slightly penalized as it can indicate poor modularity.
        # The sweet spot is a moderately connected chunk.
        relational_modifier = 1.0 - (
            abs(relational_mean - 0.5) * 0.4
        )  # Penalty for being too isolated or too coupled

        # 3. Create blessing vector, applying the relational modifier to the EPC inputs
        blessing_vector = create_blessing_vector(
            cadence=1.0 - contradiction_pressure,
            qualia=ethical_alignment
            * relational_modifier,  # Effective ethics is modulated by integration
            entropy=np.mean(field_state.semantic[:2]),
            contradiction=contradiction_pressure,
            presence=presence_density
            * relational_modifier,  # Effective presence is modulated by integration
        )

        # Get tier from CoherenceCurve
        tier = blessing_vector["Φ"]
        epc = blessing_vector["epc"]

        # Calculate resonance score
        resonance_score = (
            np.mean(field_state.semantic) * 0.25
            + ethical_alignment * 0.30
            + (1 - contradiction_pressure) * 0.20
            + presence_density * 0.15
            + np.mean(field_state.temporal) * 0.10
        )

        # Determine phase based on EPC and patterns
        phase = self._determine_phase(epc, field_state)

        return BlessingState(
            tier=tier,
            epc=epc,
            ethical_alignment=ethical_alignment,
            contradiction_pressure=contradiction_pressure,
            presence_density=presence_density,
            resonance_score=resonance_score,
            phase=phase,
        )

    # Include all the field extraction methods from original PBJRAG-2
    def _extract_field_state(self, node: ast.AST, content: str, tree: ast.AST) -> FieldState:
        """Extract multi-dimensional field state from code"""

        # Semantic field - what the code means/does
        semantic = self._extract_semantic_field(node, content)

        # Emotional field - developer intent, naming patterns
        emotional = self._extract_emotional_field(node, content)

        # Ethical field - code quality, best practices
        ethical = self._extract_ethical_field(node, content)

        # Temporal field - change patterns, evolution
        temporal = self._extract_temporal_field(node, content)

        # Contradiction field - internal complexity
        contradiction = self._extract_contradiction_field(node)

        # Relational field - interconnectedness
        relational = self._extract_relational_field(node, tree)

        # Rhythmic field - cadence and flow
        rhythmic = self._extract_rhythmic_field(node, content)

        # Emergent field - novelty and surprise
        emergent = self._extract_emergent_field(node, content)

        return FieldState(
            semantic=semantic,
            emotional=emotional,
            ethical=ethical,
            temporal=temporal,
            entropic=self._extract_entropic_field(node, content),
            rhythmic=rhythmic,
            contradiction=contradiction,
            relational=relational,
            emergent=emergent,
        )

    def _extract_semantic_field(self, node: ast.AST, content: str) -> np.ndarray:
        """
        Extract semantic meaning as field vector.

        Analyzes what the code means and does by examining:
        - Token/vocabulary richness (unique vs total tokens)
        - Structural complexity (number of AST nodes)
        - Documentation quality (docstring presence and completeness)
        - Identifier naming conventions and length

        Returns a vector where each dimension represents:
        - [0]: Vocabulary richness (unique tokens / total tokens)
        - [1]: Structural complexity (normalized AST node count)
        - [2]: Documentation length (docstring length / 200)
        - [3]: Parameter documentation presence
        - [4]: Return documentation presence
        - [5]: Snake case naming convention adherence
        - [6]: Name length appropriateness
        - [7]: Name casing conventions
        """
        field = np.zeros(self.field_dim)

        # Token diversity (entropy-like)
        tokens = re.findall(r"\w+", content.lower())
        unique_tokens = set(tokens)
        if tokens:
            field[0] = len(unique_tokens) / len(tokens)  # Vocabulary richness

        # Structural complexity
        complexity = 0
        for _child in ast.walk(node):
            complexity += 1
        field[1] = 1 - np.exp(-complexity / 50)  # Normalized complexity

        # Docstring presence and quality
        docstring = ast.get_docstring(node)
        if docstring:
            field[2] = min(1.0, len(docstring) / 200)  # Normalized doc length
            field[3] = 1.0 if "param" in docstring.lower() else 0.5  # Parameter docs
            field[4] = 1.0 if "return" in docstring.lower() else 0.5  # Return docs

        # Name quality (semantic clarity)
        if hasattr(node, "name"):
            name = node.name
            if self.field_dim > 5:
                field[5] = 1.0 if "_" in name else 0.5  # Snake case
            if self.field_dim > 6:
                field[6] = min(1.0, len(name) / 20)  # Reasonable length
            if self.field_dim > 7:
                field[7] = 1.0 if name.lower() != name else 0.7  # Not all lowercase

        return field

    def _extract_emotional_field(self, node: ast.AST, content: str) -> np.ndarray:
        """
        Extract emotional/intentional patterns including documentation density.

        Analyzes developer intent and emotional resonance by examining:
        - Documentation and comment density (communication level)
        - Naming sentiment (positive/negative indicators in identifiers)
        - TODO/FIXME markers (unresolved intent)
        - Assertion presence (confidence level)

        Returns a vector where each dimension represents:
        - [0]: Documentation and comment density
        - [1]: Positive naming indicators (create, build, init, etc.)
        - [2]: Negative naming indicators (delete, error, broken, etc.)
        - [3]: TODO marker presence (normalized)
        - [4]: FIXME marker presence (normalized)
        - [5]: Assertion count (confidence level)
        """
        field = np.zeros(self.field_dim)

        # Documentation + comment density (developer communication & intent)
        comment_lines = content.count("#")
        docstring = ""
        if isinstance(node, ast.AST) and hasattr(node, "body"):
            try:
                docstring = ast.get_docstring(node)
            except TypeError:
                docstring = ""
        doc_lines = len(docstring.split("\n")) if docstring else 0
        total_lines = content.count("\n") + 1
        field[0] = (comment_lines + doc_lines) / max(total_lines, 1)

        # Naming sentiment – positive/negative intent signals in identifier names
        if hasattr(node, "name"):
            name_lower = node.name.lower()
            # Positive indicators
            positive = [
                "create",
                "build",
                "init",
                "setup",
                "helper",
                "util",
                "calculate",
                "validate",
                "clean",
            ]
            field[1] = sum(1 for p in positive if p in name_lower) / len(positive)

            # Negative indicators
            negative = ["delete", "remove", "fail", "error", "broken", "hack"]
            field[2] = sum(1 for n in negative if n in name_lower) / len(negative)

        # TODO/FIXME presence (unresolved intent)
        lower = content.lower()
        field[3] = min(1.0, lower.count("todo") / 5)
        field[4] = min(1.0, lower.count("fixme") / 5)

        # Assertion presence (confidence)
        assertion_count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                assertion_count += 1
        if self.field_dim > 5:
            field[5] = min(1.0, assertion_count / 10)

        return field

    def _extract_ethical_field(self, node: ast.AST, content: str) -> np.ndarray:
        """
        Extract ethical alignment (code quality, best practices).

        Assesses code quality and alignment with best practices by analyzing:
        - Error handling (try/except blocks)
        - Input validation patterns
        - Type hint presence (static typing)
        - Logging presence (observability)
        - Test-like patterns (test code markers)
        - Dangerous patterns (eval, exec, globals)
        - Documentation quality
        - Cyclomatic complexity (code simplicity)

        Returns a vector where each dimension represents:
        - [0]: Error handling coverage (try blocks)
        - [1]: Input validation presence
        - [2]: Type hints presence
        - [3]: Logging presence (boolean)
        - [4]: Test pattern indicators
        - [5]: Absence of dangerous patterns
        - [6]: Docstring presence
        - [7]: Low cyclomatic complexity (simpler is better)
        """
        field = np.zeros(self.field_dim)

        # Error handling presence
        try_blocks = sum(1 for n in ast.walk(node) if isinstance(n, ast.Try))
        field[0] = min(1.0, try_blocks / 5)

        # Input validation patterns
        validations = ["assert", "raise", "check", "validate", "verify"]
        validation_score = sum(1 for v in validations if v in content.lower())
        field[1] = min(1.0, validation_score / len(validations))

        # Type hints presence
        type_hint_count = 0
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns:
                type_hint_count += 1
            for arg in node.args.args:
                if arg.annotation:
                    type_hint_count += 1
        field[2] = min(1.0, type_hint_count / 5)

        # Logging presence (observability)
        field[3] = 1.0 if "log" in content.lower() else 0.0

        # Test-like patterns
        test_patterns = ["test_", "assert", "mock", "fixture"]
        field[4] = sum(1 for p in test_patterns if p in content.lower()) / len(test_patterns)

        # Dangerous patterns (negative ethics)
        dangerous = ["exec", "eval", "global", "__dict__"]
        field[5] = 1.0 - sum(1 for d in dangerous if d in content) / len(dangerous)

        # Documentation quality
        if hasattr(node, "body") and node.body:
            first = node.body[0]
            has_docstring = (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            )
            if self.field_dim > 6:
                field[6] = 1.0 if has_docstring else 0.0

        # Cyclomatic complexity (inverse ethics - simpler is better)
        branches = sum(
            1
            for n in ast.walk(node)
            if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With))
        )
        if self.field_dim > 7:
            field[7] = 1.0 / (1 + branches / 10)

        return field

    def _extract_temporal_field(self, node: ast.AST, content: str) -> np.ndarray:
        """
        Extract temporal/evolution patterns.

        Analyzes code evolution and change patterns by examining:
        - Version indicators (v1, v2, deprecated, legacy)
        - Change markers (TODO, FIXME, HACK, refactor, optimize)
        - Stability indicators (stable, final, production, tested)
        - Modern imports (typing, dataclasses, pathlib, enum)
        - Async patterns (modern evolution indicators)

        Returns a vector where each dimension represents:
        - [0]: Version indicator presence
        - [1]: Change marker presence
        - [2]: Stability indicator presence (inverse of change)
        - [3]: Modern import usage
        - [4]: Async pattern usage
        """
        field = np.zeros(self.field_dim)

        # Version indicators
        version_patterns = ["v1", "v2", "version", "deprecated", "legacy", "new"]
        field[0] = sum(1 for p in version_patterns if p in content.lower()) / len(version_patterns)

        # Change indicators
        change_patterns = ["todo", "fixme", "hack", "refactor", "optimize"]
        field[1] = sum(1 for p in change_patterns if p in content.lower()) / len(change_patterns)

        # Stability indicators (inverse of change)
        stable_patterns = ["stable", "final", "production", "tested"]
        field[2] = sum(1 for p in stable_patterns if p in content.lower()) / len(stable_patterns)

        # Import freshness (newer imports suggest evolution)
        modern_imports = ["typing", "dataclasses", "pathlib", "enum"]
        import_score = 0
        for child in ast.walk(node):
            if isinstance(child, ast.ImportFrom):
                for modern in modern_imports:
                    if child.module and modern in child.module:
                        import_score += 1
            elif isinstance(child, ast.Import):
                for alias in child.names:
                    for modern in modern_imports:
                        if modern in alias.name:
                            import_score += 1
        field[3] = min(1.0, import_score / len(modern_imports))

        # Async patterns (modern evolution)
        field[4] = 1.0 if isinstance(node, ast.AsyncFunctionDef) else 0.0

        return field

    def _extract_contradiction_field(self, node: ast.AST) -> np.ndarray:
        """
        Extract contradiction/complexity patterns from the AST node.

        Analyzes internal tensions and complexity by measuring:
        - Cyclomatic complexity (number of decision points)
        - Nesting depth (how deeply nested the code structure is)

        The contradiction field represents internal code complexity that
        may indicate tension between different design goals or unclear
        implementation strategies.

        Returns a vector where all dimensions contain:
        - Combination of cyclomatic complexity (60%) and nesting depth (40%)
        - Higher values indicate more contradictory/complex code
        """
        field = np.zeros(self.field_dim)

        # 1. Cyclomatic Complexity
        complexity = 0
        for child in ast.walk(node):
            if isinstance(
                child,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                    ast.And,
                    ast.Or,
                    ast.ExceptHandler,
                ),
            ):
                complexity += 1

        complexity_score = min(1.0, complexity / 10.0)

        # 2. Nesting Depth
        max_depth = self._calculate_max_depth(node)
        depth_score = min(1.0, (max_depth - 1) / 10.0 if max_depth > 0 else 0)

        # Combine scores, giving a slight edge to complexity over depth
        contradiction_score = (complexity_score * 0.6) + (depth_score * 0.4)

        field.fill(contradiction_score)
        return field

    def _extract_relational_field(self, node: ast.AST, tree: ast.AST) -> np.ndarray:
        """
        Extracts relational field by analyzing calls to and from this node.

        Analyzes how well integrated this code is with the rest of the system:
        - Outgoing connections (how many other functions it calls)
        - Incoming connections (how many times it's called by other functions)
        - Dependency fan-out (external dependencies)
        - Role in the codebase (core vs peripheral)

        A more connected node has a higher relational score, indicating it's
        a key piece of the system. Moderately connected is ideal; too isolated
        or too coupled indicates poor modularity.

        Returns a vector representing relational connectivity metrics.
        """
        field = np.zeros(self.field_dim)
        node_name = getattr(node, "name", None)
        if not node_name:
            return field

        # How many other functions does this function call? (Outgoing connections)
        outgoing_calls = {
            n.func.id
            for n in ast.walk(node)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        }
        field[0] = min(1.0, len(outgoing_calls) / 10.0)

        # How many times is this function called within the file? (Incoming connections)
        incoming_calls = 0
        for scope in ast.walk(tree):
            if scope is not node:  # Don't count recursive calls against itself here
                for sub_node in ast.walk(scope):
                    if (
                        isinstance(sub_node, ast.Call)
                        and isinstance(sub_node.func, ast.Name)
                        and sub_node.func.id == node_name
                    ):
                        incoming_calls += 1

        field[1] = min(1.0, incoming_calls / 10.0)

        # Shared dependencies (a measure of topical coherence)
        my_deps = self._get_dependencies(node)
        shared_deps = 0
        for other_node in ast.walk(tree):
            if isinstance(other_node, (ast.FunctionDef, ast.ClassDef)) and other_node is not node:
                other_deps = self._get_dependencies(other_node)
                shared_deps += len(set(my_deps) & set(other_deps))

        field[2] = min(1.0, shared_deps / 20.0)

        return field

    def _get_dependencies(self, node: ast.AST) -> list[str]:
        """Extract what this code depends on."""
        deps = set()

        # Track all names that are loaded (not stored)
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Name)
                and isinstance(child.ctx, ast.Load)
                and child.id not in {"self", "True", "False", "None"}
            ):
                deps.add(child.id)

        # Remove names that are defined in this scope
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                deps.discard(child.id)

        return list(deps)

    def _calculate_max_depth(self, node: ast.AST) -> int:
        """Calculates the maximum nesting depth of control-flow statements."""
        if not isinstance(node, ast.AST):
            return 0

        children = list(ast.iter_child_nodes(node))
        if not children:
            return 1

        max_child_depth = max(self._calculate_max_depth(c) for c in children)

        is_control_flow = isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.Try,
                ast.With,
                ast.AsyncFor,
                ast.AsyncWith,
            ),
        )
        return max_child_depth + 1 if is_control_flow else max_child_depth

    def _determine_phase(self, epc: float, field_state: FieldState) -> str:
        """Determine which phase the code is in"""
        # Weighted phase calculation based on multiple factors
        temporal_mean = np.mean(field_state.temporal)
        ethical_mean = np.mean(field_state.ethical)

        # Phase score combines EPC with temporal and ethical factors
        phase_score = epc * 0.5 + temporal_mean * 0.3 + ethical_mean * 0.2

        # Find appropriate phase
        for phase, (low, high) in self.phase_boundaries.items():
            if low <= phase_score < high:
                return phase

        return "stillness"  # Default

    def _extract_dependencies(self, node: ast.AST) -> list[str]:
        """Extract what this code depends on"""
        deps = set()

        # Track all names that are loaded (not stored)
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Name)
                and isinstance(child.ctx, ast.Load)
                and child.id not in {"self", "True", "False", "None"}
            ):
                deps.add(child.id)

        # Remove names that are defined in this scope
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                deps.discard(child.id)

        return list(deps)

    def _create_module_chunk(
        self, tree: ast.AST, lines: list[str], existing_chunks: list[DSCChunk]
    ) -> DSCChunk | None:
        """Create chunk for module-level code"""
        # Find lines not covered by existing chunks
        covered_lines = set()
        for chunk in existing_chunks:
            covered_lines.update(range(chunk.start_line, chunk.end_line))

        module_lines = []
        for i, line in enumerate(lines):
            if i not in covered_lines and line.strip():
                module_lines.append((i, line))

        if not module_lines:
            return None

        # Create module content
        start_line = module_lines[0][0]
        end_line = module_lines[-1][0] + 1
        content = "\n".join(line for _, line in module_lines)

        # Module chunks have no functional code, so they go into the compost phase
        # for later relational analysis. This is inspired by the potential_capacitor concept.
        field_state = FieldState(
            semantic=np.full(self.field_dim, 0.1),
            emotional=np.full(self.field_dim, 0.1),
            ethical=np.full(self.field_dim, 0.2),
            temporal=np.full(self.field_dim, 0.2),
            entropic=np.full(self.field_dim, 0.3),  # Module-level code has moderate entropy
            rhythmic=np.full(self.field_dim, 0.1),  # Low rhythmic score for imports/constants
            contradiction=np.full(self.field_dim, 0.0),
            relational=np.full(self.field_dim, 0.05),  # Very low relational score
            emergent=np.full(self.field_dim, 0.1),  # Low emergent for boilerplate
        )

        # Heuristic boosts – comments & TODOs increase temporal/change signal
        doc_lines = len(re.findall(r"\b\w+\b", content))
        comment_lines = content.count("#")
        presence_density = (doc_lines + comment_lines) / max(len(content.split("\n")), 1)

        blessing = BlessingState(
            tier="Φ~",  # Neutral tier, as quality is not yet determined
            epc=0.4,  # A middling EPC
            ethical_alignment=0.5,
            contradiction_pressure=0.0,
            presence_density=presence_density,
            resonance_score=0.0,
            phase="compost",
        )

        return DSCChunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            field_state=field_state,
            blessing=blessing,
            chunk_type="module",
            provides=["__module__"],
            depends_on=[],
        )

    def _create_malformed_chunk(self, code: str) -> DSCChunk:
        """Create chunk for malformed code"""
        field_state = FieldState(
            semantic=np.zeros(self.field_dim),
            emotional=np.zeros(self.field_dim),
            ethical=np.zeros(self.field_dim),
            temporal=np.zeros(self.field_dim),
            entropic=np.ones(self.field_dim),  # High entropy for malformed code
            rhythmic=np.zeros(self.field_dim),  # No rhythm in malformed code
            contradiction=np.ones(self.field_dim),  # High contradiction
            relational=np.zeros(self.field_dim),
            emergent=np.zeros(self.field_dim),  # No emergent patterns
        )

        # Use Crown Jewel metrics for malformed code
        blessing_vector = create_blessing_vector(
            cadence=0.0,
            qualia=0.0,
            entropy=1.0,  # High entropy for malformed code
            contradiction=1.0,
            presence=0.0,
        )

        blessing = BlessingState(
            tier=blessing_vector["Φ"],
            epc=blessing_vector["epc"],
            ethical_alignment=0.0,
            contradiction_pressure=1.0,
            presence_density=0.0,
            resonance_score=0.0,
            phase="compost",
        )

        return DSCChunk(
            content=code,
            start_line=0,
            end_line=len(code.split("\n")),
            field_state=field_state,
            blessing=blessing,
            chunk_type="malformed",
            provides=[],
            depends_on=[],
        )

    def calculate_chunk_resonance(self, chunk1: DSCChunk, chunk2: DSCChunk) -> float:
        """Calculate resonance between two chunks using field states"""
        # Use Crown Jewel's coherence vector for group resonance
        group_blessings = [
            chunk1.to_fragment()["blessing"],
            chunk2.to_fragment()["blessing"],
        ]

        coherence = self.metrics.coherence_vector(group_blessings)

        # Additional field-based resonance
        semantic_sim = 1 - np.linalg.norm(
            chunk1.field_state.semantic - chunk2.field_state.semantic
        ) / np.sqrt(self.field_dim)
        ethical_sim = 1 - np.linalg.norm(
            chunk1.field_state.ethical - chunk2.field_state.ethical
        ) / np.sqrt(self.field_dim)
        relational_sim = 1 - np.linalg.norm(
            chunk1.field_state.relational - chunk2.field_state.relational
        ) / np.sqrt(self.field_dim)

        # Combine coherence with field similarities
        resonance = (
            coherence["group_coherence"] * 0.4
            + semantic_sim * 0.25
            + ethical_sim * 0.20
            + relational_sim * 0.15
        )

        return min(1.0, max(0.0, resonance))

    def _extract_entropic_field(self, node: ast.AST, content: str) -> np.ndarray:
        """
        Extract entropic field as vector.

        Analyzes chaos, unpredictability, and disorder in the code by calculating:
        - McCabe cyclomatic complexity from AST
        - Exception handler count (try/except blocks)
        - Branch count (if/elif/else, for, while)
        - Loop complexity
        - Boolean operator complexity (and/or)

        The entropic field measures how much "chaos" or uncertainty exists
        in the code's behavior and structure. Higher entropy indicates more
        complex and unpredictable control flow.

        Returns a vector [0.0-1.0] representing entropic characteristics.
        """
        field = np.zeros(self.field_dim)

        try:
            # 1. McCabe Cyclomatic Complexity
            # Count decision points: each if, for, while, and, or adds complexity
            complexity = 1  # Base complexity
            for child in ast.walk(node):
                if isinstance(
                    child,
                    (
                        ast.If,
                        ast.For,
                        ast.While,
                        ast.And,
                        ast.Or,
                        ast.ExceptHandler,
                        ast.With,
                        ast.AsyncFor,
                        ast.AsyncWith,
                    ),
                ):
                    complexity += 1

            # Normalize complexity (10 is considered high complexity)
            field[0] = min(1.0, complexity / 10.0)

            # 2. Exception handler complexity
            exception_handlers = sum(1 for n in ast.walk(node) if isinstance(n, ast.ExceptHandler))
            field[1] = min(1.0, exception_handlers / 5.0)

            # 3. Branch density (control flow statements per line)
            branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While)))
            total_lines = content.count("\n") + 1
            branch_density = branches / max(total_lines, 1)
            field[2] = min(1.0, branch_density * 10)  # Scale up for visibility

            # 4. Loop complexity (nested loops increase entropy)
            loop_count = sum(
                1 for n in ast.walk(node) if isinstance(n, (ast.For, ast.While, ast.AsyncFor))
            )
            field[3] = min(1.0, loop_count / 5.0)

            # 5. Boolean complexity (complex conditions)
            bool_ops = sum(1 for n in ast.walk(node) if isinstance(n, (ast.And, ast.Or)))
            field[4] = min(1.0, bool_ops / 8.0)

            # 6. Try block nesting (nested error handling)
            try_blocks = sum(1 for n in ast.walk(node) if isinstance(n, ast.Try))
            field[5] = min(1.0, try_blocks / 3.0)

            # 7. Raise statement count (exception flow)
            raise_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.Raise))
            if self.field_dim > 6:
                field[6] = min(1.0, raise_count / 5.0)

            # 8. Overall entropy score (weighted average)
            if self.field_dim > 7:
                field[7] = (
                    field[0] * 0.3  # Cyclomatic complexity
                    + field[1] * 0.2  # Exception handlers
                    + field[2] * 0.15  # Branch density
                    + field[3] * 0.15  # Loops
                    + field[4] * 0.1  # Boolean ops
                    + field[5] * 0.05  # Try blocks
                    + field[6] * 0.05  # Raises
                )

        except Exception:
            # On any error, return neutral entropy (0.5)
            field.fill(0.5)

        return field

    def _extract_rhythmic_field(self, node: ast.AST, content: str) -> np.ndarray:
        """
        Extract rhythmic field as vector.

        Analyzes code flow, cadence, and organizational patterns by measuring:
        - Naming convention consistency (snake_case vs camelCase)
        - Indentation consistency
        - Line length variance (consistent vs erratic)
        - Function size consistency
        - Whitespace rhythm
        - Statement regularity

        The rhythmic field measures the "flow" and "beat" of how code
        is organized and how consistently patterns are applied. Higher
        rhythm indicates more consistent, predictable formatting.

        Returns a vector [0.0-1.0] representing rhythmic/flow characteristics.
        """
        field = np.zeros(self.field_dim)

        try:
            lines = content.split("\n")
            non_empty_lines = [line for line in lines if line.strip()]

            # 1. Naming convention consistency
            names = []
            for child in ast.walk(node):
                if hasattr(child, "name"):
                    names.append(child.name)
                elif isinstance(child, ast.Name):
                    names.append(child.id)

            if names:
                # Check snake_case consistency
                snake_case_count = sum(1 for name in names if "_" in name and name.islower())
                camel_case_count = sum(
                    1 for name in names if name[0].islower() and any(c.isupper() for c in name)
                )
                total_names = len(names)

                # Higher score if one convention dominates
                dominant_ratio = max(snake_case_count, camel_case_count) / total_names
                field[0] = dominant_ratio
            else:
                field[0] = 0.5  # Neutral if no names

            # 2. Indentation consistency
            if non_empty_lines:
                indents = []
                for line in non_empty_lines:
                    stripped = line.lstrip()
                    if stripped:
                        indent = len(line) - len(stripped)
                        indents.append(indent)

                if len(indents) > 1:
                    # Check if indentation follows consistent pattern (multiples of 4 or 2)
                    indent_set = set(indents)
                    # Check for 4-space rhythm
                    four_space_rhythm = sum(1 for i in indent_set if i % 4 == 0)
                    consistency = four_space_rhythm / len(indent_set)
                    field[1] = consistency
                else:
                    field[1] = 0.8  # Single indent level is consistent

            # 3. Line length variance (lower variance = more rhythmic)
            if non_empty_lines:
                line_lengths = [len(line) for line in non_empty_lines]
                mean_length = np.mean(line_lengths)
                std_length = np.std(line_lengths)

                # Convert variance to consistency score (lower std = higher rhythm)
                if mean_length > 0:
                    coefficient_of_variation = std_length / mean_length
                    # Lower CoV means more consistent line lengths
                    field[2] = max(0.0, 1.0 - min(1.0, coefficient_of_variation))
                else:
                    field[2] = 0.5

            # 4. Function/method size consistency (shorter functions = more rhythmic)
            func_count = sum(
                1 for n in ast.walk(node) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
            lines_per_func = len(non_empty_lines) / max(func_count, 1)

            # Ideal function size is 10-20 lines
            if 10 <= lines_per_func <= 20:
                field[3] = 1.0
            elif lines_per_func < 10:
                field[3] = 0.8  # Short functions are good
            else:
                # Penalty for long functions
                field[3] = max(0.0, 1.0 - (lines_per_func - 20) / 100)

            # 5. Whitespace rhythm (consistent blank line usage)
            blank_line_pattern = []
            consecutive_blanks = 0
            for line in lines:
                if not line.strip():
                    consecutive_blanks += 1
                else:
                    if consecutive_blanks > 0:
                        blank_line_pattern.append(consecutive_blanks)
                    consecutive_blanks = 0

            if blank_line_pattern:
                # Most consistent is 1-2 blank lines between sections
                consistent_blanks = sum(1 for b in blank_line_pattern if 1 <= b <= 2)
                field[4] = consistent_blanks / len(blank_line_pattern)
            else:
                field[4] = 0.7  # No blank lines is okay

            # 6. Statement density rhythm (statements per line)
            statement_count = sum(
                1
                for n in ast.walk(node)
                if isinstance(n, (ast.Assign, ast.AugAssign, ast.Return, ast.Expr, ast.Call))
            )
            statements_per_line = statement_count / max(len(non_empty_lines), 1)

            # Ideal is around 1 statement per line
            if 0.8 <= statements_per_line <= 1.2:
                field[5] = 1.0
            else:
                field[5] = max(0.0, 1.0 - abs(statements_per_line - 1.0))

            # 7. Overall rhythmic consistency
            if self.field_dim > 6:
                field[6] = np.mean(field[:6])

            # 8. Code "flow" score (combination of all rhythm factors)
            if self.field_dim > 7:
                field[7] = (
                    field[0] * 0.25  # Naming consistency
                    + field[1] * 0.20  # Indentation
                    + field[2] * 0.15  # Line length
                    + field[3] * 0.15  # Function size
                    + field[4] * 0.10  # Whitespace
                    + field[5] * 0.15  # Statement density
                )

        except Exception:
            # On any error, return neutral rhythm (0.5)
            field.fill(0.5)

        return field

    def _extract_emergent_field(self, node: ast.AST, content: str) -> np.ndarray:
        """
        Extract emergent field as vector.

        Analyzes novelty, creativity, and unexpected patterns by detecting:
        - Rare AST patterns (decorators, metaclasses, context managers)
        - Advanced Python features (walrus operator, match statements)
        - Pattern diversity (variety of language constructs used)
        - Creative implementations (generators, comprehensions, lambda)
        - Metaprogramming indicators (getattr, setattr, __dict__)

        The emergent field captures "surprise" and "novelty" - patterns
        that go beyond standard conventions and represent creative solutions.
        Higher emergence indicates more novel, sophisticated patterns.

        Returns a vector [0.0-1.0] representing emergent/novel characteristics.
        """
        field = np.zeros(self.field_dim)

        try:
            # 1. Decorator usage (creative pattern)
            decorator_count = 0
            for child in ast.walk(node):
                if isinstance(child, (ast.FunctionDef, ast.ClassDef)):
                    decorator_count += len(child.decorator_list)
            field[0] = min(1.0, decorator_count / 3.0)

            # 2. Advanced Python features
            advanced_features = 0

            # Walrus operator (Python 3.8+)
            advanced_features += sum(1 for n in ast.walk(node) if isinstance(n, ast.NamedExpr))

            # Match statements (Python 3.10+)
            advanced_features += sum(1 for n in ast.walk(node) if isinstance(n, ast.Match))

            # Context managers (with statements)
            advanced_features += sum(
                1 for n in ast.walk(node) if isinstance(n, (ast.With, ast.AsyncWith))
            )

            # Async/await patterns
            advanced_features += sum(
                1 for n in ast.walk(node) if isinstance(n, (ast.AsyncFunctionDef, ast.Await))
            )

            field[1] = min(1.0, advanced_features / 5.0)

            # 3. Metaprogramming indicators
            metaprogramming_score = 0
            content_lower = content.lower()

            # Check for metaprogramming keywords
            meta_patterns = [
                "__dict__",
                "__class__",
                "getattr",
                "setattr",
                "hasattr",
                "type(",
                "metaclass",
                "__new__",
                "__init_subclass__",
            ]
            metaprogramming_score = sum(1 for pattern in meta_patterns if pattern in content_lower)
            field[2] = min(1.0, metaprogramming_score / len(meta_patterns))

            # 4. Generator and comprehension usage (creative iteration)
            generator_count = sum(
                1
                for n in ast.walk(node)
                if isinstance(
                    n,
                    (
                        ast.GeneratorExp,
                        ast.ListComp,
                        ast.SetComp,
                        ast.DictComp,
                        ast.Yield,
                        ast.YieldFrom,
                    ),
                )
            )
            field[3] = min(1.0, generator_count / 5.0)

            # 5. Lambda and functional patterns
            functional_count = sum(
                1 for n in ast.walk(node) if isinstance(n, (ast.Lambda, ast.FunctionDef))
            )
            # Check for functional programming keywords
            functional_keywords = ["map", "filter", "reduce", "lambda", "partial"]
            functional_keyword_count = sum(
                1 for keyword in functional_keywords if keyword in content_lower
            )
            functional_score = (functional_count / 10.0 + functional_keyword_count / 5.0) / 2
            field[4] = min(1.0, functional_score)

            # 6. Pattern diversity (variety of constructs)
            pattern_types = set()
            for child in ast.walk(node):
                pattern_types.add(type(child).__name__)

            # More diverse patterns indicate creative code
            diversity_score = len(pattern_types) / 30.0  # 30+ types is very diverse
            field[5] = min(1.0, diversity_score)

            # 7. Special methods and operator overloading
            special_method_count = 0
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.FunctionDef)
                    and child.name.startswith("__")
                    and child.name.endswith("__")
                    and child.name not in ["__init__", "__new__", "__del__"]
                ):
                    special_method_count += 1

            if self.field_dim > 6:
                field[6] = min(1.0, special_method_count / 3.0)

            # 8. Overall emergence score (weighted combination)
            if self.field_dim > 7:
                field[7] = (
                    field[0] * 0.20  # Decorators
                    + field[1] * 0.20  # Advanced features
                    + field[2] * 0.15  # Metaprogramming
                    + field[3] * 0.15  # Generators/comprehensions
                    + field[4] * 0.10  # Functional patterns
                    + field[5] * 0.10  # Pattern diversity
                    + field[6] * 0.10  # Special methods
                )

        except Exception:
            # On any error, return neutral emergence (0.5)
            field.fill(0.5)

        return field
