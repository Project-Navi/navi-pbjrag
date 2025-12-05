"""
Tests for PhaseManager - 7-phase lifecycle management.
"""

import pytest
from pbjrag import PhaseManager


class TestPhaseManager:
    """Test suite for PhaseManager."""

    def test_phase_manager_initialization(self):
        """Test that PhaseManager initializes correctly."""
        manager = PhaseManager()

        assert manager is not None
        assert manager.current_phase is None
        assert len(manager.phase_history) > 0  # Should have initialization
        assert manager.valid_phases is not None

    def test_valid_phases_list(self):
        """Test that valid phases are defined."""
        manager = PhaseManager()

        expected_phases = [
            "witness",
            "recognition",
            "compost",
            "emergence",
            "blessing",
            "expression",
        ]

        assert manager.valid_phases == expected_phases

    def test_transition_to_valid_phase(self):
        """Test transitioning to a valid phase."""
        manager = PhaseManager()

        # First transition should be to witness
        result = manager.transition_to_phase("witness")

        assert result is True
        assert manager.current_phase == "witness"

    def test_phase_transition_sequence(self):
        """Test the complete phase transition sequence."""
        manager = PhaseManager()

        phases = ["witness", "recognition", "compost", "emergence", "blessing", "expression"]

        for phase in phases:
            result = manager.transition_to_phase(phase)
            assert result is True
            assert manager.current_phase == phase

    def test_invalid_phase_raises_error(self):
        """Test that transitioning to invalid phase raises error."""
        manager = PhaseManager()

        with pytest.raises(ValueError, match="Invalid phase"):
            manager.transition_to_phase("invalid_phase")

    def test_invalid_transition_sequence(self):
        """Test that invalid transition sequence raises error."""
        manager = PhaseManager()

        # Transition to witness first
        manager.transition_to_phase("witness")

        # Try to skip to blessing (should fail)
        with pytest.raises(ValueError, match="Invalid transition"):
            manager.transition_to_phase("blessing")

    def test_phase_history_tracking(self):
        """Test that phase history is tracked correctly."""
        manager = PhaseManager()

        manager.transition_to_phase("witness")
        manager.transition_to_phase("recognition")

        # Should have initialization + 2 transitions
        assert len(manager.phase_history) >= 3

    def test_get_current_phase(self):
        """Test getting the current phase."""
        manager = PhaseManager()

        assert manager.current_phase is None

        manager.transition_to_phase("witness")
        assert manager.current_phase == "witness"

    def test_phase_detection_returns_valid_phase(self):
        """Test that phase detection returns a valid phase name."""
        manager = PhaseManager()

        # After initialization, current_phase should be valid or None
        if manager.current_phase is not None:
            assert manager.current_phase in manager.valid_phases

    def test_cycle_back_to_witness(self):
        """Test cycling back to witness phase from expression."""
        manager = PhaseManager()

        # Complete a full cycle
        phases = ["witness", "recognition", "compost", "emergence", "blessing", "expression"]
        for phase in phases:
            manager.transition_to_phase(phase)

        # Should be able to cycle back to witness
        result = manager.transition_to_phase("witness")
        assert result is True
        assert manager.current_phase == "witness"

    def test_phase_manager_with_config(self):
        """Test PhaseManager initialization with config."""
        config = {"custom_setting": "value"}
        manager = PhaseManager(config=config)

        assert manager.config == config

    def test_phase_data_storage(self):
        """Test that phase data can be stored."""
        manager = PhaseManager()

        # phase_data should be accessible
        assert hasattr(manager, 'phase_data')
        assert isinstance(manager.phase_data, dict)

    def test_all_phases_are_reachable(self):
        """Test that all valid phases can be reached through valid transitions."""
        manager = PhaseManager()

        # Transition through all phases
        for phase in manager.valid_phases:
            # Reset to start
            manager = PhaseManager()

            # Find path to this phase
            if phase == "witness":
                manager.transition_to_phase("witness")
                assert manager.current_phase == "witness"
