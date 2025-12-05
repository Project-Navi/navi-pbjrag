"""Phase Manager Module - Manages phase transitions and state for the Crown Jewel Planner.

This module provides a streamlined phase transition system that tracks phase history
and manages the ritual flow of the Crown Jewel Planner through its 7-phase lifecycle:

1. **initialization** → **witness**: System startup and code observation
2. **witness** → **recognition**: Pattern identification
3. **recognition** → **compost**: Breaking down rigid structures
4. **compost** → **emergence**: Allowing new patterns to surface
5. **emergence** → **blessing**: Quality evaluation
6. **blessing** → **expression**: Solution manifestation
7. **expression** → **witness**: Cycling back for continuous improvement

The phase manager enforces valid transitions, maintains history, and stores
phase-specific data for each stage of the planning ritual.

Example:
    >>> from pbjrag.crown_jewel.phase_manager import PhaseManager
    >>> pm = PhaseManager()
    >>> pm.transition_to_phase("witness")
    True
    >>> pm.update_phase_data({"fragments_count": 42})
    >>> print(pm.current_phase)
    'witness'
    >>> history = pm.get_phase_history()
"""

import datetime
from typing import Any


class PhaseManager:
    """Manages phase transitions and state for the Crown Jewel Planner.

    Provides a clean interface for phase rituals and transitions through the
    7-phase lifecycle. Enforces sequential flow while allowing cycling from
    expression back to witness for continuous improvement.

    Attributes:
        config: Optional configuration dictionary.
        valid_phases: List of allowed phase names.
        current_phase: Currently active phase (None during initialization).
        phase_history: Chronological list of phase transitions with timestamps.
        phase_data: Dictionary mapping phases to their associated data.

    Phase Sequence:
        initialization → witness → recognition → compost → emergence →
        blessing → expression → witness (cycle)

    Example:
        >>> pm = PhaseManager()
        >>> pm.transition_to_phase("witness")
        True
        >>> pm.transition_to_phase("recognition")
        True
        >>> pm.update_phase_data({"patterns_found": 15})
        >>> print(pm.get_phase_data()["patterns_found"])
        15
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the phase manager with optional configuration.

        Args:
            config: Optional configuration dictionary. Currently unused but
                reserved for future extensibility.

        Note:
            The phase manager starts in "initialization" phase with an empty
            history entry. First valid transition is to "witness" phase.
        """
        self.config = config or {}

        # Define valid phases
        self.valid_phases = [
            "witness",
            "recognition",
            "compost",
            "emergence",
            "blessing",
            "expression",
        ]

        # Initialize phase state
        self.current_phase = None
        self.phase_history = []
        self.phase_data = {}

        # Add initialization to history
        self._add_to_history("initialization")

    def transition_to_phase(self, phase: str) -> bool:
        """Transition to the specified phase.

        Validates the target phase and checks whether the transition is allowed
        from the current phase. Updates current_phase and adds entry to history.

        Args:
            phase: Phase to transition to. Must be one of the valid_phases.

        Returns:
            True if transition was successful.

        Raises:
            ValueError: If phase is not in valid_phases or if transition is
                not allowed from the current phase.

        Example:
            >>> pm = PhaseManager()
            >>> pm.transition_to_phase("witness")
            True
            >>> pm.transition_to_phase("compost")  # Invalid: skips recognition
            ValueError: Invalid transition from witness to compost
        """
        # Validate phase
        if phase not in self.valid_phases:
            raise ValueError(
                f"Invalid phase: {phase}. Valid phases are: {', '.join(self.valid_phases)}"
            )

        # Check for valid transition
        if not self._is_valid_transition(phase):
            raise ValueError(f"Invalid transition from {self.current_phase} to {phase}")

        # Update current phase
        self.current_phase = phase

        # Add to history
        self._add_to_history(phase)

        return True

    def _is_valid_transition(self, target_phase: str) -> bool:
        """Check if a transition to the target phase is valid.

        Implements the sequential phase flow with cycling allowed from expression
        back to witness for continuous improvement.

        Args:
            target_phase: Phase to transition to.

        Returns:
            True if transition is valid from current_phase to target_phase,
            False otherwise.

        Note:
            Valid transitions:
            - initialization → witness
            - witness → recognition
            - recognition → compost
            - compost → emergence
            - emergence → blessing
            - blessing → expression
            - expression → witness (cycle)
        """
        # If no current phase, any valid phase is acceptable
        if self.current_phase is None:
            return target_phase in self.valid_phases

        # Define valid transitions
        valid_transitions = {
            "initialization": ["witness"],
            "witness": ["recognition"],
            "recognition": ["compost"],
            "compost": ["emergence"],
            "emergence": ["blessing"],
            "blessing": ["expression"],
            "expression": ["witness"],  # Allow cycling back to witness
        }

        # Check if transition is valid
        return target_phase in valid_transitions.get(self.current_phase, [])

    def _add_to_history(self, phase: str) -> None:
        """Add a phase transition to the history.

        Creates a history entry with the phase name and ISO-formatted timestamp.

        Args:
            phase: Phase that was transitioned to.

        Note:
            Timestamps use datetime.datetime.now().isoformat() for consistency
            with other Crown Jewel modules.
        """
        entry = {"phase": phase, "timestamp": datetime.datetime.now().isoformat()}

        self.phase_history.append(entry)

    def get_phase_history(self) -> list[dict[str, Any]]:
        """Get the phase transition history.

        Returns:
            List of phase transition entries, each containing:
                - phase: Phase name
                - timestamp: ISO-formatted timestamp string

        Example:
            >>> pm = PhaseManager()
            >>> pm.transition_to_phase("witness")
            >>> pm.transition_to_phase("recognition")
            >>> history = pm.get_phase_history()
            >>> for entry in history:
            ...     print(f"{entry['phase']}: {entry['timestamp']}")
            initialization: 2024-01-15T10:30:00.123456
            witness: 2024-01-15T10:30:05.234567
            recognition: 2024-01-15T10:30:10.345678
        """
        return self.phase_history

    def get_phase_data(self, phase: str | None = None) -> dict[str, Any]:
        """Get data for the specified phase or the current phase.

        Args:
            phase: Optional phase to get data for. If None, returns data for
                the current phase.

        Returns:
            Phase data dictionary. Returns empty dict if no data exists for
            the specified phase or if current_phase is None.

        Example:
            >>> pm = PhaseManager()
            >>> pm.transition_to_phase("witness")
            >>> pm.update_phase_data({"fragments": 42})
            >>> data = pm.get_phase_data()
            >>> print(data["fragments"])
            42
        """
        target_phase = phase if phase is not None else self.current_phase

        if target_phase is None:
            return {}

        return self.phase_data.get(target_phase, {})

    def update_phase_data(self, data: dict[str, Any], phase: str | None = None) -> None:
        """Update data for the specified phase or the current phase.

        Merges the provided data dictionary with existing phase data. If the
        phase has no existing data, creates a new entry.

        Args:
            data: Data dictionary to merge with existing phase data.
            phase: Optional phase to update data for. If None, updates data
                for the current phase.

        Note:
            If current_phase is None and no phase is specified, this method
            returns without doing anything.

        Example:
            >>> pm = PhaseManager()
            >>> pm.transition_to_phase("witness")
            >>> pm.update_phase_data({"fragments": 42, "files": ["a.py"]})
            >>> pm.update_phase_data({"patterns": 5})
            >>> data = pm.get_phase_data()
            >>> print(data)
            {'fragments': 42, 'files': ['a.py'], 'patterns': 5}
        """
        target_phase = phase if phase is not None else self.current_phase

        if target_phase is None:
            return

        if target_phase not in self.phase_data:
            self.phase_data[target_phase] = {}

        self.phase_data[target_phase].update(data)

    def reset(self) -> None:
        """Reset the phase manager to its initial state.

        Clears current_phase, phase_history, and phase_data, then adds a new
        "initialization" entry to the history. This is useful for starting a
        new planning session or recovering from errors.

        Example:
            >>> pm = PhaseManager()
            >>> pm.transition_to_phase("witness")
            >>> pm.update_phase_data({"data": "value"})
            >>> pm.reset()
            >>> print(pm.current_phase)
            None
            >>> print(len(pm.get_phase_history()))
            1
            >>> print(pm.get_phase_history()[0]["phase"])
            initialization
        """
        self.current_phase = None
        self.phase_history = []
        self.phase_data = {}

        # Add initialization to history
        self._add_to_history("initialization")
