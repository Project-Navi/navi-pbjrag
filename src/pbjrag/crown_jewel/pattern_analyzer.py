# D:\SanctuarIDE\crown_jewel_core\pattern_analyzer.py (continued)
# D:\SanctuarIDE\crown_jewel_core\pattern_analyzer.py
"""
Pattern Analyzer Module - Unified pattern detection and analysis for the Crown Jewel Planner.

This module consolidates functionality from code_analyzer, code_fractal_detector, and
related modules into a comprehensive system for pattern detection and analysis.
"""

import ast
import datetime
import json
import logging
import os
from pathlib import Path
import re
from typing import Any

import numpy as np

# Check for scikit-learn availability

try:
    import sklearn  # noqa: F401

    HAVE_SKLEARN = True
except ImportError:
    HAVE_SKLEARN = False

from .metrics import CoreMetrics, create_blessing_vector

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """
    Unified pattern analysis system for the Crown Jewel Planner.
    Consolidates functionality from multiple analysis modules.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the pattern analyzer with optional configuration.

        Parameters:
        - config: Optional configuration dictionary
        """
        self.config = config or {}
        self.metrics = CoreMetrics(self.config)

    def analyze_file(self, file_path: str) -> dict[str, Any]:
        """
        Analyze a single file and extract patterns.

        Parameters:
        - file_path: Path to the file to analyze

        Returns:
        - Analysis results
        """
        try:
            # Read the file
            with Path(file_path).open(encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Extract basic metrics
            metrics = self._extract_basic_metrics(file_path, content)

            # Try to parse AST
            try:
                tree = ast.parse(content)
                ast_metrics = self._extract_ast_metrics(tree, content)
                metrics.update(ast_metrics)
                metrics["ast_parse_error"] = False
            except Exception as e:
                logger.warning(f"AST parse error in {file_path}: {e} (falling back to plaintext)")
                plaintext_metrics = self._extract_plaintext_metrics(content)
                metrics.update(plaintext_metrics)
                metrics["ast_parse_error"] = True

            # Create blessing vector
            blessing = create_blessing_vector(
                cadence=metrics.get("cadence", 0.0),
                qualia=metrics.get("ethical_alignment", 0.5),
                entropy=metrics.get("entropy_level", 0.5),
                contradiction=metrics.get("contradiction_pressure", 0.5),
                presence=metrics.get("presence_density", 0.5),
            )

            metrics["blessing"] = blessing

            return metrics

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")

            # Return minimal metrics for failed analysis
            return {
                "file": file_path,
                "error": str(e),
                "ast_parse_error": True,
                "entropy_level": 0.5,
                "complexity_level": 0.5,
                "contradiction_pressure": 0.7,
                "ethical_alignment": 0.3,
                "presence_density": 0.0,
                "blessing": create_blessing_vector(
                    entropy=0.5, contradiction=0.7, qualia=0.3, presence=0.0
                ),
            }

    def _extract_basic_metrics(self, file_path: str, content: str) -> dict[str, Any]:
        """
        Extract basic metrics from a file.

        Parameters:
        - file_path: Path to the file
        - content: File content

        Returns:
        - Basic metrics
        """
        # Get file info
        path = Path(file_path)
        file_name = path.name
        file_size = len(content)
        lines = content.splitlines()
        line_count = len(lines)

        # Calculate basic metrics
        non_empty_lines = sum(1 for line in lines if line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        code_lines = non_empty_lines - comment_lines

        return {
            "file": file_path,
            "file_name": file_name,
            "file_size": file_size,
            "line_count": line_count,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "comment_ratio": comment_lines / max(line_count, 1),
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def _extract_ast_metrics(self, tree: ast.AST, content: str) -> dict[str, Any]:
        """
        Extract metrics from an AST.

        Parameters:
        - tree: AST to analyze
        - content: Original file content

        Returns:
        - AST-based metrics
        """
        # Extract functions and classes
        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "args": len(node.args.args),
                        "body_length": len(node.body),
                    }
                )
            elif isinstance(node, ast.ClassDef):
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append(child.name)

                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                        "method_count": len(methods),
                    }
                )
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                else:  # ImportFrom
                    module = node.module or ""
                    for name in node.names:
                        imports.append(f"{module}.{name.name}")

        # Calculate complexity metrics
        complexity = self._calculate_complexity(tree)

        # Calculate entropy
        entropy = self._calculate_entropy(content)

        # Extract docstrings and comments
        docstrings = self._extract_docstrings(tree)

        # Calculate presence density
        presence_density = len(docstrings) / max(len(functions) + len(classes), 1)

        # Calculate contradiction pressure
        contradiction_pressure = self._calculate_contradiction(tree, functions, classes)

        # Calculate ethical alignment
        ethical_alignment = self._calculate_ethical_alignment(docstrings, content)

        # Calculate cadence
        cadence = self._calculate_cadence(functions, classes, content)

        return {
            "functions": functions,
            "function_count": len(functions),
            "classes": classes,
            "class_count": len(classes),
            "imports": imports,
            "import_count": len(imports),
            "complexity_level": complexity,
            "entropy_level": entropy,
            "docstrings": docstrings,
            "docstring_count": len(docstrings),
            "presence_density": presence_density,
            "contradiction_pressure": contradiction_pressure,
            "ethical_alignment": ethical_alignment,
            "cadence": cadence,
        }

    def _extract_plaintext_metrics(self, content: str) -> dict[str, Any]:
        """
        Extract metrics from plaintext when AST parsing fails.

        Parameters:
        - content: File content

        Returns:
        - Plaintext-based metrics
        """
        lines = content.splitlines()

        # Calculate token-based entropy
        tokens = content.split()
        unique_tokens = set(tokens)
        token_entropy = len(unique_tokens) / max(len(tokens), 1)

        # Count comment lines
        comment_lines = sum(1 for line in lines if "#" in line)
        presence_density = comment_lines / max(len(lines), 1)

        # Estimate complexity based on line count and indentation
        indentation_levels = []
        for line in lines:
            if line.strip():
                spaces = len(line) - len(line.lstrip())
                indentation_levels.append(spaces)

        if indentation_levels:
            max_indentation = max(indentation_levels)
            complexity = min(1.0, (max_indentation / 20) * 0.5 + (len(lines) / 500) * 0.5)
        else:
            complexity = 0.5

        # Estimate contradiction based on mixed naming conventions
        camel_case = sum(1 for token in unique_tokens if re.match(r"^[a-z][a-zA-Z0-9]*$", token))
        snake_case = sum(1 for token in unique_tokens if re.match(r"^[a-z][a-z0-9_]*$", token))

        if unique_tokens:
            naming_consistency = max(camel_case, snake_case) / len(unique_tokens)
            contradiction_pressure = 1.0 - naming_consistency
        else:
            contradiction_pressure = 0.5

        # Estimate ethical alignment based on presence of certain keywords
        ethical_keywords = [
            "license",
            "copyright",
            "author",
            "version",
            "todo",
            "fixme",
            "note",
        ]
        ethical_mentions = sum(
            1 for keyword in ethical_keywords if keyword.lower() in content.lower()
        )
        ethical_alignment = min(1.0, ethical_mentions / len(ethical_keywords))

        # Estimate cadence based on line length consistency
        line_lengths = [len(line) for line in lines if line.strip()]
        if line_lengths:
            avg_length = sum(line_lengths) / len(line_lengths)
            variance = sum((length - avg_length) ** 2 for length in line_lengths) / len(
                line_lengths
            )
            normalized_variance = min(1.0, variance / (avg_length**2))
            cadence = 1.0 - normalized_variance
        else:
            cadence = 0.5

        return {
            "complexity_level": complexity,
            "entropy_level": token_entropy,
            "presence_density": presence_density,
            "contradiction_pressure": contradiction_pressure,
            "ethical_alignment": ethical_alignment,
            "cadence": cadence,
            "functions": [],
            "function_count": 0,
            "classes": [],
            "class_count": 0,
            "imports": [],
            "import_count": 0,
            "docstrings": [],
            "docstring_count": 0,
        }

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """
        Calculate code complexity based on AST.

        Parameters:
        - tree: AST to analyze

        Returns:
        - Complexity level in range [0,1]
        """
        # Count branching nodes
        branching_count = 0
        node_count = 0

        for node in ast.walk(tree):
            node_count += 1
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                branching_count += 1

        # Count nesting levels
        max_nesting = 0

        class NestingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.max_nesting = 0
                self.current_nesting = 0

            def generic_visit(self, node):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    self.current_nesting += 1
                    self.max_nesting = max(self.max_nesting, self.current_nesting)
                    super().generic_visit(node)
                    self.current_nesting -= 1
                else:
                    super().generic_visit(node)

        visitor = NestingVisitor()
        visitor.visit(tree)
        max_nesting = visitor.max_nesting

        # Calculate complexity
        branching_factor = min(1.0, branching_count / max(node_count, 1) * 3)
        nesting_factor = min(1.0, max_nesting / 10)

        return (branching_factor * 0.7) + (nesting_factor * 0.3)

    def _calculate_entropy(self, content: str) -> float:
        """
        Calculate information entropy.

        Parameters:
        - content: Content to analyze

        Returns:
        - Entropy level in range [0,1]
        """
        # Count token frequencies
        tokens = content.split()
        token_count = len(tokens)

        if token_count == 0:
            return 0.0

        token_freqs = {}
        for token in tokens:
            token_freqs[token] = token_freqs.get(token, 0) + 1

        # Calculate Shannon entropy
        entropy = 0.0
        for freq in token_freqs.values():
            prob = freq / token_count
            if prob > 0:
                entropy -= prob * np.log2(prob)

        # Normalize entropy to [0,1]
        max_entropy = np.log2(token_count) if token_count > 1 else 1
        return min(1.0, entropy / max_entropy)

    def _extract_docstrings(self, tree: ast.AST) -> list[str]:
        """
        Extract docstrings from AST.

        Parameters:
        - tree: AST to analyze

        Returns:
        - List of docstrings
        """
        docstrings = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append(docstring)

        return docstrings

    def _calculate_contradiction(
        self,
        tree: ast.AST,
        functions: list[dict[str, Any]],
        classes: list[dict[str, Any]],
    ) -> float:
        """
        Calculate contradiction pressure.

        Parameters:
        - tree: AST to analyze
        - functions: List of functions
        - classes: List of classes

        Returns:
        - Contradiction pressure in range [0,1]
        """
        # Check naming conventions
        camel_case_count = 0
        snake_case_count = 0

        for func in functions:
            name = func["name"]
            if re.match(r"^[a-z][a-zA-Z0-9]*$", name):
                camel_case_count += 1
            elif re.match(r"^[a-z][a-z0-9_]*$", name):
                snake_case_count += 1

        for cls in classes:
            name = cls["name"]
            if re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
                camel_case_count += 1
            elif re.match(r"^[a-z][a-z0-9_]*$", name):
                snake_case_count += 1

        total_names = len(functions) + len(classes)

        if total_names == 0:
            naming_contradiction = 0.5
        else:
            dominant_style = max(camel_case_count, snake_case_count)
            naming_contradiction = 1.0 - (dominant_style / total_names)

        # Check for global variables and imports
        global_vars = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        global_vars.append(target.id)

        global_contradiction = min(1.0, len(global_vars) / 20)

        # Combine contradiction factors
        return (naming_contradiction * 0.6) + (global_contradiction * 0.4)

    def _calculate_ethical_alignment(self, docstrings: list[str], content: str) -> float:
        """
        Calculate ethical alignment.

        Parameters:
        - docstrings: List of docstrings
        - content: File content

        Returns:
        - Ethical alignment in range [0,1]
        """
        # Check for license/copyright
        has_license = any(
            re.search(r"licen[sc]e", content, re.IGNORECASE) is not None for d in docstrings
        )
        has_copyright = any(
            re.search(r"copyright", content, re.IGNORECASE) is not None for d in docstrings
        )

        # Check for author attribution
        has_author = any(
            re.search(r"author", content, re.IGNORECASE) is not None for d in docstrings
        )

        # Check for parameter documentation
        param_docs = sum(
            1 for d in docstrings if re.search(r"param|parameter|arg|argument", d, re.IGNORECASE)
        )

        # Check for return value documentation
        return_docs = sum(1 for d in docstrings if re.search(r"return|returns", d, re.IGNORECASE))

        # Check for examples
        has_examples = any(
            re.search(r"example|usage", d, re.IGNORECASE) is not None for d in docstrings
        )

        # Calculate ethical alignment
        license_factor = 0.2 if has_license or has_copyright else 0.0
        author_factor = 0.1 if has_author else 0.0
        param_factor = min(0.3, param_docs / max(len(docstrings), 1) * 0.3)
        return_factor = min(0.2, return_docs / max(len(docstrings), 1) * 0.2)
        example_factor = 0.2 if has_examples else 0.0

        return license_factor + author_factor + param_factor + return_factor + example_factor

    def _calculate_cadence(
        self,
        functions: list[dict[str, Any]],
        classes: list[dict[str, Any]],
        content: str,
    ) -> float:
        """
        Calculate code cadence/rhythm.

        Parameters:
        - functions: List of functions
        - classes: List of classes
        - content: File content

        Returns:
        - Cadence in range [0,1]
        """
        lines = content.splitlines()

        # Check line length consistency
        line_lengths = [len(line) for line in lines if line.strip()]

        if not line_lengths:
            return 0.5

        avg_length = sum(line_lengths) / len(line_lengths)
        variance = sum((length - avg_length) ** 2 for length in line_lengths) / len(line_lengths)
        normalized_variance = min(1.0, variance / (avg_length**2))
        length_consistency = 1.0 - normalized_variance

        # Check function size consistency
        func_sizes = [f["body_length"] for f in functions]

        if func_sizes:
            avg_size = sum(func_sizes) / len(func_sizes)
            size_variance = sum((size - avg_size) ** 2 for size in func_sizes) / len(func_sizes)
            normalized_size_variance = min(1.0, size_variance / (avg_size**2))
            size_consistency = 1.0 - normalized_size_variance
        else:
            size_consistency = 0.5

        # Check indentation consistency
        indentation_levels = []
        for line in lines:
            if line.strip():
                spaces = len(line) - len(line.lstrip())
                indentation_levels.append(spaces)

        if indentation_levels:
            # Check if indentation is consistent (multiples of 2 or 4)
            indent_by_2 = all(level % 2 == 0 for level in indentation_levels)
            indent_by_4 = all(level % 4 == 0 for level in indentation_levels)

            indent_consistency = 1.0 if indent_by_2 or indent_by_4 else 0.5
        else:
            indent_consistency = 0.5

        # Combine cadence factors
        return (length_consistency * 0.4) + (size_consistency * 0.4) + (indent_consistency * 0.2)

    def detect_patterns(self, fragments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Detect patterns in a list of fragments.

        Parameters:
        - fragments: List of fragments to analyze

        Returns:
        - List of detected patterns
        """
        patterns = []

        # Group fragments by similarity
        similarity_groups = self._group_by_similarity(fragments)

        # Create patterns from groups
        for group_id, group in enumerate(similarity_groups):
            if len(group) < 2:
                continue

            # Calculate group metrics
            group_blessings = [f.get("blessing", {}) for f in group]
            group_blessing = self.metrics.coherence_vector(group_blessings)

            pattern = {
                "id": f"pattern_{group_id}",
                "type": "similarity_group",
                "fragments": [f.get("file", "") for f in group],
                "fragment_count": len(group),
                "group_blessing": group_blessing,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            patterns.append(pattern)

        # Detect functional patterns
        functional_patterns = self._detect_functional_patterns(fragments)
        patterns.extend(functional_patterns)

        # Detect structural patterns
        structural_patterns = self._detect_structural_patterns(fragments)
        patterns.extend(structural_patterns)

        return patterns

    def _group_by_similarity(self, fragments: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """
        Group fragments by similarity.

        Parameters:
        - fragments: List of fragments to group

        Returns:
        - List of fragment groups
        """
        if not fragments:
            return []

        # Extract blessing vectors
        vectors = []
        for fragment in fragments:
            blessing = fragment.get("blessing", {})
            vector = [
                blessing.get("entropy", 0.5),
                blessing.get("κ", 0.5),
                blessing.get("ε", 0.5),
                blessing.get("P", 0.5),
                blessing.get("cadence", 0.5),
            ]
            vectors.append(vector)

        # Calculate similarity matrix
        if HAVE_SKLEARN:
            from sklearn.metrics.pairwise import cosine_similarity

            similarity_matrix = cosine_similarity(vectors)

            # Group by similarity threshold
            threshold = 0.9
            groups = []
            used = set()

            for i in range(len(fragments)):
                if i in used:
                    continue

                group = [fragments[i]]
                used.add(i)

                for j in range(len(fragments)):
                    if j in used or i == j:
                        continue

                    if similarity_matrix[i, j] >= threshold:
                        group.append(fragments[j])
                        used.add(j)

                groups.append(group)

            return groups
        # Fallback if sklearn is not available
        logger.warning("sklearn not available, using simplified grouping")

        # Group by file extension
        extension_groups = {}

        for fragment in fragments:
            file_path = fragment.get("file", "")
            ext = Path(file_path).suffix

            if ext not in extension_groups:
                extension_groups[ext] = []

            extension_groups[ext].append(fragment)

        return list(extension_groups.values())

    def _detect_functional_patterns(self, fragments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Detect functional patterns in fragments.

        Parameters:
        - fragments: List of fragments to analyze

        Returns:
        - List of functional patterns
        """
        patterns = []

        # Group fragments by function signatures
        function_groups = {}

        for fragment in fragments:
            functions = fragment.get("functions", [])

            for function in functions:
                name = function.get("name", "")
                args = function.get("args", 0)

                # Create a signature
                signature = f"{name}({args})"

                if signature not in function_groups:
                    function_groups[signature] = []

                function_groups[signature].append({"fragment": fragment, "function": function})

        # Create patterns for common functions
        for signature, group in function_groups.items():
            if len(group) < 2:
                continue

            fragments = [item["fragment"] for item in group]
            group_blessings = [f.get("blessing", {}) for f in fragments]
            group_blessing = self.metrics.coherence_vector(group_blessings)

            pattern = {
                "id": f"func_pattern_{signature}",
                "type": "functional_pattern",
                "signature": signature,
                "fragments": [f.get("file", "") for f in fragments],
                "fragment_count": len(fragments),
                "group_blessing": group_blessing,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            patterns.append(pattern)

        return patterns

    def _detect_structural_patterns(self, fragments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Detect structural patterns in fragments.

        Parameters:
        - fragments: List of fragments to analyze

        Returns:
        - List of structural patterns
        """
        patterns = []

        # Group fragments by class structure
        class_groups = {}

        for fragment in fragments:
            classes = fragment.get("classes", [])

            for cls in classes:
                name = cls.get("name", "")
                method_count = cls.get("method_count", 0)

                # Create a structure signature
                structure = f"{name}({method_count})"

                if structure not in class_groups:
                    class_groups[structure] = []

                class_groups[structure].append({"fragment": fragment, "class": cls})

        # Create patterns for common structures
        for structure, group in class_groups.items():
            if len(group) < 2:
                continue

            fragments = [item["fragment"] for item in group]
            group_blessings = [f.get("blessing", {}) for f in fragments]
            group_blessing = self.metrics.coherence_vector(group_blessings)

            pattern = {
                "id": f"struct_pattern_{structure}",
                "type": "structural_pattern",
                "structure": structure,
                "fragments": [f.get("file", "") for f in fragments],
                "fragment_count": len(fragments),
                "group_blessing": group_blessing,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            patterns.append(pattern)

        return patterns

    def suggest_combinations(
        self,
        fragments: list[dict[str, Any]],
        top_n: int = 10,
        max_group_size: int = 3,
        field_context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Suggest combinations of fragments based on purpose and coherence.

        Parameters:
        - fragments: List of fragments to combine
        - top_n: Number of top combinations to return
        - max_group_size: Maximum size of combination groups
        - field_context: Optional field context for filtering

        Returns:
        - List of suggested combinations
        """
        if not fragments:
            return []

        if field_context is None:
            field_context = {}

        purpose = field_context.get("purpose", "stability")
        epc_min = field_context.get("epc_min", 0.4)

        # Generate all valid combinations
        import itertools

        all_combos = []

        for size in range(2, max_group_size + 1):
            for combo in itertools.combinations(fragments, size):
                all_combos.append(list(combo))

        if not all_combos:
            return []

        # Calculate scores for each combination
        scored_combos = []

        for combo in all_combos:
            # Calculate group blessing
            group_blessings = [f.get("blessing", {}) for f in combo]
            group_blessing = self.metrics.coherence_vector(group_blessings)

            # Calculate purpose alignment
            purpose_alignment = self._calculate_purpose_alignment(combo, purpose)

            # Calculate emergence score
            emergence_score = self._calculate_emergence_score(combo)

            # Calculate group resonance
            group_resonance = group_blessing.get("group_coherence", 0.0)

            # Calculate overall score
            score = (
                group_blessing.get("mean_epc", 0.0) * 0.3
                + purpose_alignment * 0.3
                + emergence_score * 0.2
                + group_resonance * 0.2
            )

            # Only include combinations with sufficient EPC
            if group_blessing.get("mean_epc", 0.0) < epc_min:
                continue

            scored_combo = {
                "files": [f.get("file", "") for f in combo],
                "file_count": len(combo),
                "purpose": purpose,
                "purpose_alignment": purpose_alignment,
                "emergence_score": emergence_score,
                "group_resonance": group_resonance,
                "epc": group_blessing.get("mean_epc", 0.0),
                "score": score,
                "group_blessing": group_blessing,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            scored_combos.append(scored_combo)

        # Sort by score and return top N
        scored_combos.sort(key=lambda c: c["score"], reverse=True)

        return scored_combos[:top_n]

    def _calculate_purpose_alignment(self, combo: list[dict[str, Any]], purpose: str) -> float:
        """
        Calculate alignment of a combination with a purpose.

        Parameters:
        - combo: List of fragments in the combination
        - purpose: Purpose to align with

        Returns:
        - Purpose alignment in range [0,1]
        """
        # Define purpose-specific scoring
        purpose_weights = {
            "stability": {
                "κ": -0.4,  # Lower contradiction is better
                "ε": 0.4,  # Higher ethical alignment is better
                "cadence": 0.2,  # Higher cadence is better
            },
            "emergence": {
                "entropy": 0.4,  # Higher entropy is better
                "κ": 0.2,  # Higher contradiction can be good for emergence
                "P": 0.4,  # Higher presence is better
            },
            "coherence": {
                "κ": -0.5,  # Lower contradiction is better
                "cadence": 0.5,  # Higher cadence is better
            },
            "innovation": {
                "entropy": 0.5,  # Higher entropy is better
                "κ": 0.3,  # Some contradiction is good for innovation
                "ε": 0.2,  # Ethical alignment still matters
            },
        }

        # Get weights for the specified purpose
        weights = purpose_weights.get(purpose, purpose_weights["stability"])

        # Calculate weighted average
        total_weight = sum(abs(w) for w in weights.values())

        if total_weight == 0:
            return 0.5

        weighted_sum = 0.0

        for fragment in combo:
            blessing = fragment.get("blessing", {})

            for key, weight in weights.items():
                value = blessing.get(key, 0.5)

                # For negative weights, invert the value
                if weight < 0:
                    value = 1.0 - value
                    weight = abs(weight)

                weighted_sum += value * weight

        # Normalize by total weight and fragment count
        return weighted_sum / (total_weight * len(combo))

    def _calculate_emergence_score(self, combo: list[dict[str, Any]]) -> float:
        """
        Calculate emergence potential of a combination.

        Parameters:
        - combo: List of fragments in the combination

        Returns:
        - Emergence score in range [0,1]
        """
        if not combo:
            return 0.0

        # Extract blessing vectors
        blessings = [f.get("blessing", {}) for f in combo]

        # Calculate entropy diversity
        entropies = [b.get("entropy", 0.5) for b in blessings]
        entropy_mean = sum(entropies) / len(entropies)
        entropy_variance = sum((e - entropy_mean) ** 2 for e in entropies) / len(entropies)
        entropy_diversity = min(1.0, entropy_variance * 5)  # Scale up to [0,1]

        # Calculate contradiction balance
        contradictions = [b.get("κ", 0.5) for b in blessings]
        contradiction_mean = sum(contradictions) / len(contradictions)
        contradiction_balance = 1.0 - abs(contradiction_mean - 0.5) * 2  # Optimal at 0.5

        # Calculate ethical alignment
        ethics = [b.get("ε", 0.5) for b in blessings]
        ethical_alignment = sum(ethics) / len(ethics)

        # Calculate presence synergy
        presences = [b.get("P", 0.5) for b in blessings]
        presence_mean = sum(presences) / len(presences)

        # Calculate emergence score
        return (
            entropy_diversity * 0.3
            + contradiction_balance * 0.3
            + ethical_alignment * 0.2
            + presence_mean * 0.2
        )


# Singleton instance
analyzer = PatternAnalyzer()


def analyze_codebase(
    project_root: str, max_depth: int = 2, output_dir: str | None = None
) -> list[dict[str, Any]]:
    """
    Analyze a codebase and extract fragments.

    Parameters:
    - project_root: Root directory of the project to analyze
    - max_depth: Maximum directory depth to scan
    - output_dir: Optional output directory for analysis results

    Returns:
    - List of analyzed fragments
    """
    global analyzer

    logger.info(f"Analyzing codebase at {project_root} with max depth {max_depth}")

    fragments = []

    # Walk the directory tree
    for root, dirs, files in os.walk(project_root):
        # Calculate current depth
        rel_path = os.path.relpath(root, project_root)
        depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1

        # Skip if too deep
        if depth > max_depth:
            dirs.clear()  # Don't descend further
            continue

        # Analyze Python files
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file

                # Analyze the file
                fragment = analyzer.analyze_file(str(file_path))
                fragments.append(fragment)

    logger.info(f"Analyzed {len(fragments)} fragments")

    # Save fragments to file if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        fragments_file = output_path / "fragments.json"
        with fragments_file.open("w", encoding="utf-8") as f:
            json.dump(fragments, f, indent=2)

        logger.info(f"Saved fragments to {fragments_file}")

    return fragments


def detect_patterns(
    fragments: list[dict[str, Any]], config: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """
    Detect patterns in a list of fragments.

    Parameters:
    - fragments: List of fragments to analyze
    - config: Optional configuration dictionary

    Returns:
    - List of detected patterns
    """
    global analyzer

    if config:
        analyzer = PatternAnalyzer(config)

    logger.info(f"Detecting patterns in {len(fragments)} fragments")

    patterns = analyzer.detect_patterns(fragments)

    logger.info(f"Detected {len(patterns)} patterns")

    return patterns


def suggest_combinations(
    fragments: list[dict[str, Any]],
    top_n: int = 10,
    max_group_size: int = 3,
    field_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Suggest combinations of fragments based on purpose and coherence.

    Parameters:
    - fragments: List of fragments to combine
    - top_n: Number of top combinations to return
    - max_group_size: Maximum size of combination groups
    - field_context: Optional field context for filtering

    Returns:
    - List of suggested combinations
    """
    global analyzer

    logger.info(f"Suggesting combinations for {len(fragments)} fragments")

    combinations = analyzer.suggest_combinations(
        fragments,
        top_n=top_n,
        max_group_size=max_group_size,
        field_context=field_context,
    )

    logger.info(f"Suggested {len(combinations)} combinations")

    return combinations
