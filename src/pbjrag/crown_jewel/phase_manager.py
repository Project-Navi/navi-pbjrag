"""
Phase Manager Module - Manages phase transitions and state for the Crown Jewel Planner.

This module provides a streamlined phase transition system that tracks phase history
and manages the ritual flow of the Crown Jewel Planner.
"""

import datetime
from typing import Any, Dict, List, Optional


class PhaseManager:
    """
    Manages phase transitions and state for the Crown Jewel Planner.
    Provides a clean interface for phase rituals and transitions.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the phase manager with optional configuration.

        Parameters:
        - config: Optional configuration dictionary
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
        """
        Transition to the specified phase.

        Parameters:
        - phase: Phase to transition to

        Returns:
        - True if transition was successful, False otherwise
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
        """
        Check if a transition to the target phase is valid.

        Parameters:
        - target_phase: Phase to transition to

        Returns:
        - True if transition is valid, False otherwise
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
        """
        Add a phase transition to the history.

        Parameters:
        - phase: Phase that was transitioned to
        """
        entry = {"phase": phase, "timestamp": datetime.datetime.now().isoformat()}

        self.phase_history.append(entry)

    def get_phase_history(self) -> List[Dict[str, Any]]:
        """
        Get the phase transition history.

        Returns:
        - List of phase transition entries
        """
        return self.phase_history

    def get_phase_data(self, phase: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data for the specified phase or the current phase.

        Parameters:
        - phase: Optional phase to get data for

        Returns:
        - Phase data
        """
        target_phase = phase if phase is not None else self.current_phase

        if target_phase is None:
            return {}

        return self.phase_data.get(target_phase, {})

    def update_phase_data(
        self, data: Dict[str, Any], phase: Optional[str] = None
    ) -> None:
        """
        Update data for the specified phase or the current phase.

        Parameters:
        - data: Data to update
        - phase: Optional phase to update data for
        """
        target_phase = phase if phase is not None else self.current_phase

        if target_phase is None:
            return

        if target_phase not in self.phase_data:
            self.phase_data[target_phase] = {}

        self.phase_data[target_phase].update(data)

    def reset(self) -> None:
        """Reset the phase manager to its initial state."""
        self.current_phase = None
        self.phase_history = []
        self.phase_data = {}

        # Add initialization to history
        self._add_to_history("initialization")
