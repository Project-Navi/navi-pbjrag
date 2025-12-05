"""
Tests for CoreMetrics - Blessing calculation and metrics.
"""

import pytest
import numpy as np
from pbjrag.crown_jewel import CoreMetrics, create_blessing_vector, FieldContainer


class TestCoreMetrics:
    """Test suite for CoreMetrics."""

    def test_core_metrics_initialization(self):
        """Test that CoreMetrics initializes correctly."""
        metrics = CoreMetrics()

        assert metrics is not None
        assert metrics.quantization_precision == 4
        assert metrics.coherence_curve is not None

    def test_core_metrics_with_config(self):
        """Test CoreMetrics initialization with custom config."""
        config = {
            "quantization_precision": 6,
            "pareto_alpha": 3.0,
            "stability_threshold": 0.7,
        }
        metrics = CoreMetrics(config=config)

        assert metrics.quantization_precision == 6
        assert metrics.coherence_curve.pareto_alpha == 3.0
        assert metrics.coherence_curve.stability_threshold == 0.7

    def test_create_blessing_vector_returns_dict(self):
        """Test that create_blessing_vector returns correct structure."""
        metrics = CoreMetrics()

        # Call create_blessing_vector with the correct signature
        blessing_vector = metrics.create_blessing_vector(
            cadence=0.5,
            qualia=0.6,
            entropy=0.4,
            contradiction=0.3,
            presence=0.7
        )

        assert isinstance(blessing_vector, dict)

    def test_blessing_vector_contains_metrics(self, sample_blessing_vector):
        """Test that blessing vector contains expected metrics."""
        # Test with a pre-made blessing vector
        assert "epc" in sample_blessing_vector
        assert "qualia" in sample_blessing_vector
        assert "contradiction" in sample_blessing_vector
        assert "presence" in sample_blessing_vector

    def test_blessing_tier_calculation_positive(self):
        """Test blessing tier calculation for Φ+ (positive blessing)."""
        metrics = CoreMetrics()

        # High quality blessing vector
        vector = {
            "epc": 0.75,
            "qualia": 0.70,
            "contradiction": 0.30,
            "presence": 0.65,
        }

        tier = metrics.coherence_curve.bless_weight(vector)

        assert tier == "Φ+"

    def test_blessing_tier_calculation_neutral(self):
        """Test blessing tier calculation for Φ~ (neutral blessing)."""
        metrics = CoreMetrics()

        # Medium quality blessing vector
        vector = {
            "epc": 0.50,
            "qualia": 0.50,
            "contradiction": 0.55,
            "presence": 0.45,
        }

        tier = metrics.coherence_curve.bless_weight(vector)

        assert tier == "Φ~"

    def test_blessing_tier_calculation_negative(self):
        """Test blessing tier calculation for Φ- (negative blessing)."""
        metrics = CoreMetrics()

        # Low quality blessing vector
        vector = {
            "epc": 0.20,
            "qualia": 0.25,
            "contradiction": 0.80,
            "presence": 0.15,
        }

        tier = metrics.coherence_curve.bless_weight(vector)

        assert tier == "Φ-"

    def test_all_blessing_tiers_are_valid(self):
        """Test that all possible blessing tiers are one of the three valid tiers."""
        metrics = CoreMetrics()

        valid_tiers = {"Φ+", "Φ~", "Φ-"}

        # Test various blessing vectors
        test_vectors = [
            {"epc": 0.9, "qualia": 0.9, "contradiction": 0.1, "presence": 0.9},
            {"epc": 0.5, "qualia": 0.5, "contradiction": 0.5, "presence": 0.5},
            {"epc": 0.1, "qualia": 0.1, "contradiction": 0.9, "presence": 0.1},
        ]

        for vector in test_vectors:
            tier = metrics.coherence_curve.bless_weight(vector)
            assert tier in valid_tiers

    def test_quantize_scalar(self):
        """Test scalar quantization."""
        metrics = CoreMetrics()

        value = 3.14159265359
        quantized = metrics.quantize_scalar(value)

        assert isinstance(quantized, float)
        # Should be quantized to 4 decimal places
        assert quantized == round(value, 4)

    def test_quantize_scalar_with_precision(self):
        """Test scalar quantization with custom precision."""
        metrics = CoreMetrics()

        value = 3.14159265359
        quantized = metrics.quantize_scalar(value, precision=2)

        assert quantized == 3.14

    def test_blessing_score_ranges(self, sample_blessing_vector):
        """Test that blessing scores are within valid ranges."""
        # All blessing metrics should be between 0 and 1
        for key, value in sample_blessing_vector.items():
            if isinstance(value, (int, float)):
                assert 0.0 <= value <= 1.0, f"{key} value {value} out of range [0, 1]"

    def test_coherence_curve_pareto_weight(self):
        """Test Pareto weighting function."""
        metrics = CoreMetrics()

        # Test boundary values
        assert metrics.coherence_curve._pareto_weight(0.0) == 0.0
        assert 0.0 <= metrics.coherence_curve._pareto_weight(0.5) <= 1.0
        assert 0.0 <= metrics.coherence_curve._pareto_weight(1.0) <= 1.0

    def test_edge_case_zero_values(self):
        """Test blessing tier calculation with zero values."""
        metrics = CoreMetrics()

        vector = {
            "epc": 0.0,
            "qualia": 0.0,
            "contradiction": 0.0,
            "presence": 0.0,
        }

        tier = metrics.coherence_curve.bless_weight(vector)
        assert tier in ["Φ+", "Φ~", "Φ-"]

    def test_edge_case_max_values(self):
        """Test blessing tier calculation with maximum values."""
        metrics = CoreMetrics()

        vector = {
            "epc": 1.0,
            "qualia": 1.0,
            "contradiction": 0.0,
            "presence": 1.0,
        }

        tier = metrics.coherence_curve.bless_weight(vector)
        assert tier == "Φ+"
