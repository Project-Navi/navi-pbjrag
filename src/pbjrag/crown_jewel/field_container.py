"""
Field Container Module - Unified storage for fragments, patterns, and field state.

This module consolidates functionality from setup_field, sdk_compost_engine, and
potential_capacitor into a single, comprehensive system for managing field state.
"""

from collections.abc import Callable
import datetime
import json
import logging
from pathlib import Path
from typing import Any

from .metrics import CoreMetrics, create_blessing_vector

logger = logging.getLogger(__name__)


class FieldContainer:
    """
    Unified container for field state, fragments, patterns, and potential combinations.
    Consolidates functionality from setup_field, sdk_compost_engine, and potential_capacitor.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the field container with optional configuration.

        Parameters:
        - config: Optional configuration dictionary
        """
        self.config = config or {}
        self.metrics = CoreMetrics(config)

        # Core field state
        self.environment = {}
        self.user_input = {}
        self.dependencies = {}
        self.installed_dependencies = set()
        self.patterns = []
        self.conflicts = []
        self.solutions = []

        # Compost and capacitor state
        self.compost = []
        self.capacitor = []
        self.decay_threshold = self.config.get("decay_threshold", 0.3)
        self.capacitor_threshold = self.config.get("capacitor_threshold", 0.4)

        # Field memory
        self.fragments = []
        self.blessed_groups = []
        self.field_coherence = 0.0

        # Timestamps for decay calculations
        self.last_pulse = datetime.datetime.now()

    def update_environment(self, env_data: dict[str, Any]) -> None:
        """
        Update the field environment with new data.

        Parameters:
        - env_data: Dictionary of environment data to update
        """
        self.environment.update(env_data)

    def get_environment(self) -> dict[str, Any]:
        """
        Get the current field environment.

        Returns:
        - Complete environment dictionary
        """
        return self.environment

    def update_user_input(self, input_data: dict[str, Any]) -> None:
        """
        Update user input data in the field.

        Parameters:
        - input_data: Dictionary of user input to update
        """
        self.user_input.update(input_data)

    def get_user_input(self) -> dict[str, Any]:
        """
        Get the current user input data.

        Returns:
        - Complete user input dictionary
        """
        return self.user_input

    def update_dependencies(self, deps: dict[str, Any]) -> None:
        """
        Update dependency information in the field.

        Parameters:
        - deps: Dictionary of dependency information to update
        """
        self.dependencies.update(deps)

    def get_dependencies(self) -> dict[str, Any]:
        """
        Get the current dependency information.

        Returns:
        - Complete dependencies dictionary
        """
        return self.dependencies

    def add_installed_dependency(self, dep_name: str) -> None:
        """
        Add a dependency to the set of installed dependencies.

        Parameters:
        - dep_name: Name of the installed dependency
        """
        self.installed_dependencies.add(dep_name)

    def get_installed_dependencies(self) -> set[str]:
        """
        Get the set of installed dependencies.

        Returns:
        - Set of installed dependency names
        """
        return self.installed_dependencies

    def add_pattern(self, pattern: dict[str, Any]) -> None:
        """
        Add a pattern to the field.

        Parameters:
        - pattern: Pattern data to add
        """
        # Ensure the pattern has a timestamp
        if "timestamp" not in pattern:
            pattern["timestamp"] = datetime.datetime.now().isoformat()

        # Add blessing vector if not present
        if "blessing" not in pattern and all(
            k in pattern for k in ["entropy", "complexity", "contradiction"]
        ):
            pattern["blessing"] = create_blessing_vector(
                entropy=pattern.get("entropy", 0.5),
                contradiction=pattern.get("contradiction", 0.5),
                qualia=pattern.get("ethical_alignment", 0.5),
                presence=pattern.get("presence", 0.5),
            )

        self.patterns.append(pattern)

    def update_pattern(self, pattern_id: str, updates: dict[str, Any]) -> bool:
        """
        Update an existing pattern in the field.

        Parameters:
        - pattern_id: ID of the pattern to update
        - updates: Dictionary of updates to apply

        Returns:
        - True if pattern was found and updated, False otherwise
        """
        for i, pattern in enumerate(self.patterns):
            if pattern.get("id") == pattern_id:
                self.patterns[i].update(updates)
                return True
        return False

    def get_patterns(
        self, filter_fn: Callable[[dict[str, Any]], bool] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get patterns from the field, optionally filtered.

        Parameters:
        - filter_fn: Optional filter function

        Returns:
        - List of matching patterns
        """
        if filter_fn is None:
            return self.patterns

        return [p for p in self.patterns if filter_fn(p)]

    def add_conflict(self, conflict: dict[str, Any]) -> None:
        """
        Add a conflict to the field.

        Parameters:
        - conflict: Conflict data to add
        """
        if "timestamp" not in conflict:
            conflict["timestamp"] = datetime.datetime.now().isoformat()

        self.conflicts.append(conflict)

    def resolve_conflict(self, conflict_id: str, resolution: dict[str, Any]) -> bool:
        """
        Resolve an existing conflict in the field.

        Parameters:
        - conflict_id: ID of the conflict to resolve
        - resolution: Resolution data

        Returns:
        - True if conflict was found and resolved, False otherwise
        """
        for i, conflict in enumerate(self.conflicts):
            if conflict.get("id") == conflict_id:
                self.conflicts[i]["resolved"] = True
                self.conflicts[i]["resolution"] = resolution
                self.conflicts[i]["resolution_timestamp"] = datetime.datetime.now().isoformat()
                return True
        return False

    def get_conflicts(self, include_resolved: bool = False) -> list[dict[str, Any]]:
        """
        Get conflicts from the field.

        Parameters:
        - include_resolved: Whether to include resolved conflicts

        Returns:
        - List of matching conflicts
        """
        if include_resolved:
            return self.conflicts

        return [c for c in self.conflicts if not c.get("resolved", False)]

    def add_solution(self, solution: dict[str, Any]) -> None:
        """
        Add a solution to the field.

        Parameters:
        - solution: Solution data to add
        """
        if "timestamp" not in solution:
            solution["timestamp"] = datetime.datetime.now().isoformat()

        self.solutions.append(solution)

    def get_solutions(self) -> list[dict[str, Any]]:
        """
        Get solutions from the field.

        Returns:
        - List of solutions
        """
        return self.solutions

    def add_fragment(self, fragment: dict[str, Any]) -> None:
        """
        Add a fragment to the field memory.

        Parameters:
        - fragment: Fragment data to add
        """
        # Ensure the fragment has a timestamp
        if "timestamp" not in fragment:
            fragment["timestamp"] = datetime.datetime.now().isoformat()

        # Add blessing vector if not present
        if "blessing" not in fragment and all(
            k in fragment for k in ["entropy", "complexity", "contradiction"]
        ):
            fragment["blessing"] = create_blessing_vector(
                entropy=fragment.get("entropy", 0.5),
                contradiction=fragment.get("contradiction", 0.5),
                qualia=fragment.get("ethical_alignment", 0.5),
                presence=fragment.get("presence", 0.5),
            )

        self.fragments.append(fragment)

    def get_fragments(
        self, filter_fn: Callable[[dict[str, Any]], bool] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get fragments from the field memory, optionally filtered.

        Parameters:
        - filter_fn: Optional filter function

        Returns:
        - List of matching fragments
        """
        if filter_fn is None:
            return self.fragments

        return [f for f in self.fragments if filter_fn(f)]

    def store_in_compost(self, item: dict[str, Any], reason: str = "") -> None:
        """
        Store an item in the compost for potential future use.

        Parameters:
        - item: Item to store in compost
        - reason: Optional reason for composting
        """
        if "compost_timestamp" not in item:
            item["compost_timestamp"] = datetime.datetime.now().isoformat()

        if reason:
            item["compost_reason"] = reason

        self.compost.append(item)

    def decay_compost(self, max_age_days: float = 7.0) -> int:
        """
        Decay items in the compost that are older than the specified age.

        Parameters:
        - max_age_days: Maximum age in days before decay

        Returns:
        - Number of items decayed
        """
        now = datetime.datetime.now()
        max_age = datetime.timedelta(days=max_age_days)

        decayed = 0
        remaining = []

        for item in self.compost:
            timestamp = item.get("compost_timestamp")
            if timestamp:
                try:
                    item_time = datetime.datetime.fromisoformat(timestamp)
                    if now - item_time > max_age:
                        decayed += 1
                        continue
                except (ValueError, TypeError):
                    pass

            remaining.append(item)

        self.compost = remaining
        return decayed

    def get_compost(
        self, filter_fn: Callable[[dict[str, Any]], bool] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get items from the compost, optionally filtered.

        Parameters:
        - filter_fn: Optional filter function

        Returns:
        - List of matching compost items
        """
        if filter_fn is None:
            return self.compost

        return [c for c in self.compost if filter_fn(c)]

    def hold_in_capacitor(self, item: dict[str, Any], reason: str = "") -> None:
        """
        Hold an item in the capacitor for potential future emergence.

        Parameters:
        - item: Item to hold in capacitor
        - reason: Optional reason for holding
        """
        if "capacitor_timestamp" not in item:
            item["capacitor_timestamp"] = datetime.datetime.now().isoformat()

        if reason:
            item["capacitor_reason"] = reason

        self.capacitor.append(item)

    def pulse_check(self, field_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Check for items in the capacitor that are ready for release based on field context.

        Parameters:
        - field_context: Optional field context for evaluating readiness

        Returns:
        - List of items ready for release
        """
        if field_context is None:
            field_context = {}

        now = datetime.datetime.now()
        time_since_pulse = (now - self.last_pulse).total_seconds() / 3600.0  # Hours

        # Adjust threshold based on time since last pulse
        threshold_adjustment = min(0.2, time_since_pulse / 24.0)  # Max 0.2 reduction per day
        current_threshold = max(0.0, self.capacitor_threshold - threshold_adjustment)

        ready_items = []
        remaining = []

        for item in self.capacitor:
            # Check if the item has a blessing vector
            blessing = item.get("blessing", {})
            if not blessing:
                blessing = item.get("group_blessing", {})

            # If item has EPC and it's above threshold, mark for release
            epc = blessing.get("epc", 0.0)
            if epc >= current_threshold:
                item["release_timestamp"] = now.isoformat()
                item["release_context"] = field_context
                ready_items.append(item)
            else:
                remaining.append(item)

        self.capacitor = remaining
        self.last_pulse = now

        return ready_items

    def pulse_release_all(self) -> list[dict[str, Any]]:
        """
        Release all items from the capacitor regardless of readiness.

        Returns:
        - List of all released items
        """
        now = datetime.datetime.now()
        released = self.capacitor

        for item in released:
            item["release_timestamp"] = now.isoformat()
            item["force_released"] = True

        self.capacitor = []
        self.last_pulse = now

        return released

    def get_capacitor(self) -> list[dict[str, Any]]:
        """
        Get all items currently held in the capacitor.

        Returns:
        - List of capacitor items
        """
        return self.capacitor

    def add_blessed_group(self, group: dict[str, Any]) -> None:
        """
        Add a blessed group to the field memory.

        Parameters:
        - group: Group data to add
        """
        if "timestamp" not in group:
            group["timestamp"] = datetime.datetime.now().isoformat()

        self.blessed_groups.append(group)

    def get_blessed_groups(self) -> list[dict[str, Any]]:
        """
        Get all blessed groups from the field memory.

        Returns:
        - List of blessed groups
        """
        return self.blessed_groups

    def calculate_field_coherence(self) -> float:
        """
        Calculate the overall coherence of the field based on patterns and fragments.

        Returns:
        - Field coherence value in range [0,1]
        """
        # Extract blessing vectors from patterns and fragments
        pattern_blessings = [p.get("blessing", {}) for p in self.patterns if "blessing" in p]
        fragment_blessings = [f.get("blessing", {}) for f in self.fragments if "blessing" in f]
        group_blessings = [
            g.get("group_blessing", {}) for g in self.blessed_groups if "group_blessing" in g
        ]

        all_blessings = pattern_blessings + fragment_blessings + group_blessings

        if not all_blessings:
            return 0.0

        # Calculate mean EPC
        epcs = [b.get("epc", 0.0) for b in all_blessings]
        mean_epc = sum(epcs) / len(epcs)

        # Count blessing tiers
        phi_plus = sum(1 for b in all_blessings if b.get("Φ") == "Φ+")
        phi_tilde = sum(1 for b in all_blessings if b.get("Φ") == "Φ~")

        total = len(all_blessings)

        # Calculate weighted coherence
        weighted_coherence = (phi_plus * 1.0 + phi_tilde * 0.5) / total if total > 0 else 0.0

        # Combine mean EPC and weighted coherence
        field_coherence = (mean_epc * 0.6) + (weighted_coherence * 0.4)

        self.field_coherence = field_coherence
        return field_coherence

    def dissolve_rigid_structures(self) -> None:
        """
        Dissolve rigid structures in the field as part of the compost phase.
        Moves low-coherence patterns to compost and resets some field state.
        """
        # Move low-coherence patterns to compost
        rigid_patterns = []
        flexible_patterns = []

        for pattern in self.patterns:
            blessing = pattern.get("blessing", {})
            if blessing.get("Φ") == "Φ-" or blessing.get("epc", 0.0) < self.decay_threshold:
                pattern["dissolution_timestamp"] = datetime.datetime.now().isoformat()
                rigid_patterns.append(pattern)
            else:
                flexible_patterns.append(pattern)

        # Store rigid patterns in compost
        for pattern in rigid_patterns:
            self.store_in_compost(pattern, reason="Dissolved during rigid structure dissolution")

        # Update patterns list
        self.patterns = flexible_patterns

        # Log the dissolution
        logger.info(f"Dissolved {len(rigid_patterns)} rigid patterns into compost")

    def allow_emergence(self) -> list[dict[str, Any]]:
        """
        Allow new patterns to emerge from the field as part of the emergence phase.

        Returns:
        - List of newly emerged patterns
        """
        # Check for items ready to emerge from the capacitor
        emerged_items = self.pulse_check()

        # Add emerged items as blessed groups
        for item in emerged_items:
            self.add_blessed_group(item)

        # Log the emergence
        logger.info(f"Allowed {len(emerged_items)} patterns to emerge from the capacitor")

        return emerged_items

    def amplify_coherent_patterns(self) -> list[dict[str, Any]]:
        """
        Amplify coherent patterns in the field as part of the blessing phase.

        Returns:
        - List of amplified patterns
        """
        amplified = []

        # Use CoherenceCurve to re-bless patterns
        for pattern in self.patterns:
            blessing = pattern.get("blessing", {})
            if blessing:
                epc = blessing.get("epc", 0.0)
                # Re-bless the pattern
                new_blessing = blessing.copy()
                new_blessing["Φ"] = self.metrics.coherence_curve.bless_weight(epc)

                if new_blessing["Φ"] != blessing.get("Φ"):
                    pattern["blessing"] = new_blessing
                    pattern["amplified"] = True
                    pattern["amplification_timestamp"] = datetime.datetime.now().isoformat()
                    amplified.append(pattern)

        # Log the amplification
        logger.info(f"Amplified {len(amplified)} coherent patterns")

        return amplified

    def manifest_solution(self) -> dict[str, Any]:
        """
        Manifest a solution from the field as part of the expression phase.

        Returns:
        - Manifested solution
        """
        # Get blessed groups and sort by EPC
        groups = sorted(
            self.blessed_groups,
            key=lambda g: g.get("group_blessing", {}).get("epc", 0.0),
            reverse=True,
        )

        if not groups:
            return {
                "success": False,
                "message": "No blessed groups available for solution",
            }

        # Use the highest-EPC group as the solution
        top_group = groups[0]

        # Create solution
        solution = {
            "success": True,
            "message": "Solution manifested successfully",
            "timestamp": datetime.datetime.now().isoformat(),
            "group": top_group,
            "field_coherence": self.field_coherence,
            "blessing": top_group.get("group_blessing", {}),
        }

        # Add to solutions
        self.add_solution(solution)

        # Log the manifestation
        logger.info(
            f"Manifested solution with EPC: "
            f"{top_group.get('group_blessing', {}).get('epc', 0.0):.4f}"
        )

        return solution

    def save_field_state(self, output_dir: str) -> dict[str, str]:
        """
        Save the current field state to files in the specified directory.

        Parameters:
        - output_dir: Directory to save field state files

        Returns:
        - Dictionary mapping file types to file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create file paths
        fragments_file = output_path / f"fragments_{timestamp}.json"
        patterns_file = output_path / f"patterns_{timestamp}.json"
        groups_file = output_path / f"blessed_groups_{timestamp}.json"
        compost_file = output_path / f"compost_{timestamp}.json"
        capacitor_file = output_path / f"capacitor_{timestamp}.json"
        solutions_file = output_path / f"solutions_{timestamp}.json"
        field_summary_file = output_path / f"field_summary_{timestamp}.json"

        # Save fragments
        with fragments_file.open("w", encoding="utf-8") as f:
            json.dump(self.fragments, f, indent=2)

        # Save patterns
        with patterns_file.open("w", encoding="utf-8") as f:
            json.dump(self.patterns, f, indent=2)

        # Save blessed groups
        with groups_file.open("w", encoding="utf-8") as f:
            json.dump(self.blessed_groups, f, indent=2)

        # Save compost
        with compost_file.open("w", encoding="utf-8") as f:
            json.dump(self.compost, f, indent=2)

        # Save capacitor
        with capacitor_file.open("w", encoding="utf-8") as f:
            json.dump(self.capacitor, f, indent=2)

        # Save solutions
        with solutions_file.open("w", encoding="utf-8") as f:
            json.dump(self.solutions, f, indent=2)

        # Create and save field summary
        field_summary = {
            "timestamp": timestamp,
            "field_coherence": self.field_coherence,
            "fragment_count": len(self.fragments),
            "pattern_count": len(self.patterns),
            "blessed_group_count": len(self.blessed_groups),
            "compost_count": len(self.compost),
            "capacitor_count": len(self.capacitor),
            "solution_count": len(self.solutions),
            "environment": self.environment,
            "user_input": self.user_input,
            "dependencies": self.dependencies,
            "installed_dependencies": list(self.installed_dependencies),
        }

        with field_summary_file.open("w", encoding="utf-8") as f:
            json.dump(field_summary, f, indent=2)

        # Log the save
        logger.info(f"Saved field state to {output_dir}")

        return {
            "fragments": str(fragments_file),
            "patterns": str(patterns_file),
            "blessed_groups": str(groups_file),
            "compost": str(compost_file),
            "capacitor": str(capacitor_file),
            "solutions": str(solutions_file),
            "field_summary": str(field_summary_file),
        }

    def load_field_state(self, input_dir: str, timestamp: str | None = None) -> bool:
        """
        Load field state from files in the specified directory.

        Parameters:
        - input_dir: Directory containing field state files
        - timestamp: Optional specific timestamp to load

        Returns:
        - True if field state was loaded successfully, False otherwise
        """
        input_path = Path(input_dir)

        if not input_path.exists():
            logger.error(f"Input directory does not exist: {input_dir}")
            return False

        # Find the latest timestamp if not specified
        if timestamp is None:
            timestamp_pattern = r"field_summary_(\d{8}_\d{6}).json"
            summaries = list(input_path.glob("field_summary_*.json"))
            if not summaries:
                logger.error(f"No field summaries found in {input_dir}")
                return False

            # Sort by timestamp in filename
            summaries.sort(key=lambda p: p.name, reverse=True)
            latest = summaries[0]

            # Extract timestamp from filename
            import re

            match = re.search(timestamp_pattern, latest.name)
            if match:
                timestamp = match.group(1)
            else:
                logger.error(f"Could not extract timestamp from {latest.name}")
                return False

        # Create file paths
        fragments_file = input_path / f"fragments_{timestamp}.json"
        patterns_file = input_path / f"patterns_{timestamp}.json"
        groups_file = input_path / f"blessed_groups_{timestamp}.json"
        compost_file = input_path / f"compost_{timestamp}.json"
        capacitor_file = input_path / f"capacitor_{timestamp}.json"
        solutions_file = input_path / f"solutions_{timestamp}.json"
        field_summary_file = input_path / f"field_summary_{timestamp}.json"

        # Check if required files exist
        if not field_summary_file.exists():
            logger.error(f"Field summary file does not exist: {field_summary_file}")
            return False

        # Load field summary
        try:
            with field_summary_file.open(encoding="utf-8") as f:
                field_summary = json.load(f)

            # Load fragments if file exists
            if fragments_file.exists():
                with fragments_file.open(encoding="utf-8") as f:
                    self.fragments = json.load(f)

            # Load patterns if file exists
            if patterns_file.exists():
                with patterns_file.open(encoding="utf-8") as f:
                    self.patterns = json.load(f)

            # Load blessed groups if file exists
            if groups_file.exists():
                with groups_file.open(encoding="utf-8") as f:
                    self.blessed_groups = json.load(f)

            # Load compost if file exists
            if compost_file.exists():
                with compost_file.open(encoding="utf-8") as f:
                    self.compost = json.load(f)

            # Load capacitor if file exists
            if capacitor_file.exists():
                with capacitor_file.open(encoding="utf-8") as f:
                    self.capacitor = json.load(f)

            # Load solutions if file exists
            if solutions_file.exists():
                with solutions_file.open(encoding="utf-8") as f:
                    self.solutions = json.load(f)

            # Update field state from summary
            self.field_coherence = field_summary.get("field_coherence", 0.0)
            self.environment = field_summary.get("environment", {})
            self.user_input = field_summary.get("user_input", {})
            self.dependencies = field_summary.get("dependencies", {})
            self.installed_dependencies = set(field_summary.get("installed_dependencies", []))

            # Log the load
            logger.info(f"Loaded field state from {input_dir} with timestamp {timestamp}")

            return True

        except Exception as e:
            logger.error(f"Error loading field state: {str(e)}")
            return False


# Singleton instance for easy access
field = FieldContainer()


def get_field() -> FieldContainer:
    """Get the singleton field container instance."""
    return field


def create_field(config: dict[str, Any] | None = None) -> FieldContainer:
    """Create a new field container instance with the specified configuration."""
    global field
    field = FieldContainer(config)
    return field
