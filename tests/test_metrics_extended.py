"""
Extended test coverage for CoreMetrics - targeting uncovered lines and edge cases.

This test suite focuses on:
1. Edge cases (None values, zero/negative inputs, boundary conditions)
2. Uncovered code paths (lines 108, 112, 130, 285-313, 338-363, 376, 426-468, 489, 494, 499)
3. Vector quantization with various precisions
4. All blessing tiers (Φ+, Φ~, Φ-)
5. RECCS score calculation and zones
6. Coherence vector calculations
7. Blessing recommendations
"""

import numpy as np
import pytest

from pbjrag.crown_jewel import CoreMetrics, create_blessing_vector
from pbjrag.crown_jewel.metrics import (
    CoherenceCurve,
    calculate_reccs_score,
    coherence_vector,
    recommend_blessing,
)


class TestCoherenceCurveEdgeCases:
    """Test CoherenceCurve with edge cases and boundary conditions."""

    def test_pareto_weight_with_zero(self):
        """Test _pareto_weight with zero value (line 34-35)."""
        curve = CoherenceCurve()
        result = curve._pareto_weight(0.0)
        assert result == 0.0

    def test_pareto_weight_with_negative(self):
        """Test _pareto_weight with negative value (line 34-35)."""
        curve = CoherenceCurve()
        result = curve._pareto_weight(-0.5)
        assert result == 0.0

    def test_pareto_weight_with_small_positive(self):
        """Test _pareto_weight with small positive value."""
        curve = CoherenceCurve()
        result = curve._pareto_weight(0.01)
        assert 0.0 <= result <= 1.0

    def test_pareto_weight_with_one(self):
        """Test _pareto_weight with maximum value."""
        curve = CoherenceCurve()
        result = curve._pareto_weight(1.0)
        assert 0.0 <= result <= 1.0

    def test_pareto_weight_custom_alpha(self):
        """Test _pareto_weight with custom alpha."""
        curve = CoherenceCurve(pareto_alpha=5.0)
        result = curve._pareto_weight(0.5)
        assert 0.0 <= result <= 1.0

    def test_bless_weight_boundary_positive(self):
        """Test bless_weight at exact positive thresholds (lines 60-66)."""
        curve = CoherenceCurve()
        vector = {
            "epc": 0.6,  # Exact threshold
            "qualia": 0.6,  # Exact threshold
            "contradiction": 0.45,  # Exact threshold
            "presence": 0.5,  # Exact threshold
        }
        result = curve.bless_weight(vector)
        assert result == "Φ+"

    def test_bless_weight_boundary_neutral(self):
        """Test bless_weight at exact neutral thresholds (lines 69-70)."""
        curve = CoherenceCurve()
        vector = {
            "epc": 0.45,  # Exact threshold
            "qualia": 0.45,  # Exact threshold
            "contradiction": 0.6,  # Exact threshold
            "presence": 0.3,
        }
        result = curve.bless_weight(vector)
        assert result == "Φ~"

    def test_bless_weight_missing_keys(self):
        """Test bless_weight with missing keys (uses defaults lines 46-49)."""
        curve = CoherenceCurve()
        vector = {}
        result = curve.bless_weight(vector)
        assert result in ["Φ+", "Φ~", "Φ-"]

    def test_bless_weight_partial_keys(self):
        """Test bless_weight with partial keys."""
        curve = CoherenceCurve()
        vector = {"epc": 0.7}
        result = curve.bless_weight(vector)
        assert result in ["Φ+", "Φ~", "Φ-"]


class TestCoreMetricsQuantization:
    """Test quantization with various edge cases."""

    def test_quantize_scalar_with_none(self):
        """Test quantize_scalar with None value (line 108)."""
        metrics = CoreMetrics()
        result = metrics.quantize_scalar(None)
        assert result == 0.0

    def test_quantize_scalar_with_zero_precision(self):
        """Test quantize_scalar with zero precision (line 112)."""
        metrics = CoreMetrics()
        result = metrics.quantize_scalar(3.14159, precision=0)
        assert result == 3.0

    def test_quantize_scalar_with_negative_precision(self):
        """Test quantize_scalar with negative precision (line 112)."""
        metrics = CoreMetrics()
        result = metrics.quantize_scalar(3.14159, precision=-1)
        assert result == 3.0

    def test_quantize_scalar_high_precision(self):
        """Test quantize_scalar with high precision."""
        metrics = CoreMetrics()
        result = metrics.quantize_scalar(3.14159265359, precision=8)
        assert result == 3.14159265

    def test_quantize_vector_empty(self):
        """Test quantize_vector with empty dict (line 130)."""
        metrics = CoreMetrics()
        result = metrics.quantize_vector({})
        assert result == {}

    def test_quantize_vector_with_none_values(self):
        """Test quantize_vector with None values (line 130)."""
        metrics = CoreMetrics()
        vector = {"a": 1.23456, "b": None, "c": 7.89012}
        result = metrics.quantize_vector(vector)
        assert result["a"] == 1.2346
        assert result["b"] == 0.0
        assert result["c"] == 7.8901

    def test_quantize_vector_custom_precision(self):
        """Test quantize_vector with custom precision (line 130)."""
        metrics = CoreMetrics()
        vector = {"x": 1.23456, "y": 2.34567}
        result = metrics.quantize_vector(vector, precision=2)
        assert result["x"] == 1.23
        assert result["y"] == 2.35

    def test_quantize_vector_zero_precision(self):
        """Test quantize_vector with zero precision."""
        metrics = CoreMetrics()
        vector = {"a": 3.7, "b": 4.2}
        result = metrics.quantize_vector(vector, precision=0)
        assert result["a"] == 4.0
        assert result["b"] == 4.0


class TestRECCSScore:
    """Test RECCS score calculation and zones (lines 285-363)."""

    def test_calculate_reccs_score_basic(self):
        """Test basic RECCS score calculation (lines 285-320)."""
        metrics = CoreMetrics()
        result = metrics.calculate_reccs_score(
            entropy=0.5, complexity=0.5, contradiction=0.5, symbolism=0.5
        )
        assert "score" in result
        assert "zone" in result
        assert "entropy" in result
        assert "complexity" in result
        assert "contradiction" in result
        assert "symbolism" in result

    def test_calculate_reccs_score_custom_weights(self):
        """Test RECCS with custom weights from config (lines 285-293)."""
        config = {
            "reccs": {
                "weights": {
                    "entropy": 0.3,
                    "complexity": 0.3,
                    "contradiction": 0.2,
                    "symbolism": 0.2,
                }
            }
        }
        metrics = CoreMetrics(config)
        result = metrics.calculate_reccs_score(
            entropy=0.6, complexity=0.7, contradiction=0.3, symbolism=0.8
        )
        assert result["score"] > 0.0

    def test_calculate_reccs_zone_chaos(self):
        """Test RECCS chaos zone (lines 338-339)."""
        metrics = CoreMetrics()
        result = metrics.calculate_reccs_score(
            entropy=0.8, complexity=0.8, contradiction=0.4, symbolism=0.5
        )
        assert result["zone"] == "chaos"

    def test_calculate_reccs_zone_sterile(self):
        """Test RECCS sterile zone (lines 342-343)."""
        metrics = CoreMetrics()
        result = metrics.calculate_reccs_score(
            entropy=0.2, complexity=0.2, contradiction=0.5, symbolism=0.3
        )
        assert result["zone"] == "sterile"

    def test_calculate_reccs_zone_conflict(self):
        """Test RECCS conflict zone (lines 346-347)."""
        metrics = CoreMetrics()
        result = metrics.calculate_reccs_score(
            entropy=0.5, complexity=0.5, contradiction=0.8, symbolism=0.5
        )
        assert result["zone"] == "conflict"

    def test_calculate_reccs_zone_resonance(self):
        """Test RECCS resonance zone (lines 350-351)."""
        metrics = CoreMetrics()
        result = metrics.calculate_reccs_score(
            entropy=0.5, complexity=0.5, contradiction=0.3, symbolism=0.8
        )
        assert result["zone"] == "resonance"

    def test_calculate_reccs_zone_flow(self):
        """Test RECCS flow zone (lines 354-360)."""
        metrics = CoreMetrics()
        result = metrics.calculate_reccs_score(
            entropy=0.5, complexity=0.5, contradiction=0.3, symbolism=0.6
        )
        assert result["zone"] == "flow"

    def test_calculate_reccs_zone_transition(self):
        """Test RECCS transition zone (default, line 363)."""
        metrics = CoreMetrics()
        result = metrics.calculate_reccs_score(
            entropy=0.35, complexity=0.75, contradiction=0.5, symbolism=0.4
        )
        assert result["zone"] == "transition"

    def test_calculate_reccs_out_of_range_values(self):
        """Test RECCS with out-of-range values (lines 296-299)."""
        metrics = CoreMetrics()
        result = metrics.calculate_reccs_score(
            entropy=1.5,  # Over 1.0
            complexity=-0.2,  # Under 0.0
            contradiction=0.5,
            symbolism=2.0,  # Over 1.0
        )
        # Should normalize to [0,1]
        assert 0.0 <= result["entropy"] <= 1.0
        assert 0.0 <= result["complexity"] <= 1.0
        assert 0.0 <= result["symbolism"] <= 1.0


class TestCoherenceVector:
    """Test coherence_vector calculation (lines 376-414)."""

    def test_coherence_vector_empty_list(self):
        """Test coherence_vector with empty list (line 376)."""
        metrics = CoreMetrics()
        result = metrics.coherence_vector([])
        assert result["group_coherence"] == 0.0
        assert result["alignment"] == 0.0
        assert result["resonance"] == 0.0

    def test_coherence_vector_single_vector(self):
        """Test coherence_vector with single vector."""
        metrics = CoreMetrics()
        vectors = [{"epc": 0.7, "ε": 0.6, "κ": 0.3}]
        result = metrics.coherence_vector(vectors)
        assert "group_coherence" in result
        assert "alignment" in result
        assert "resonance" in result
        assert "blessing" in result

    def test_coherence_vector_multiple_vectors(self):
        """Test coherence_vector with multiple vectors."""
        metrics = CoreMetrics()
        vectors = [
            {"epc": 0.7, "ε": 0.6, "κ": 0.3},
            {"epc": 0.8, "ε": 0.7, "κ": 0.2},
            {"epc": 0.6, "ε": 0.5, "κ": 0.4},
        ]
        result = metrics.coherence_vector(vectors)
        assert result["group_coherence"] > 0.0
        assert result["alignment"] > 0.0
        assert result["mean_epc"] > 0.0

    def test_coherence_vector_high_variance(self):
        """Test coherence_vector with high variance (low alignment)."""
        metrics = CoreMetrics()
        vectors = [
            {"epc": 0.1, "ε": 0.1, "κ": 0.9},
            {"epc": 0.9, "ε": 0.9, "κ": 0.1},
        ]
        result = metrics.coherence_vector(vectors)
        # High variance should result in lower alignment
        assert result["alignment"] < 0.5

    def test_coherence_vector_missing_keys(self):
        """Test coherence_vector with missing keys (uses defaults)."""
        metrics = CoreMetrics()
        vectors = [{"epc": 0.5}, {"epc": 0.6}]
        result = metrics.coherence_vector(vectors)
        assert "group_coherence" in result


class TestBlessingRecommendations:
    """Test blessing recommendations (lines 426-475)."""

    def test_recommend_blessing_negative_high_contradiction(self):
        """Test recommendations for Φ- with high contradiction (lines 437-439)."""
        metrics = CoreMetrics()
        vector = {
            "epc": 0.2,
            "qualia": 0.5,
            "ε": 0.5,
            "κ": 0.8,  # High contradiction
            "cadence": 0.5,
            "contradiction": 0.8,
            "presence": 0.3,
        }
        result = metrics.recommend_blessing(vector)
        assert result["blessing"] == "Φ-"
        assert any("contradiction" in rec.lower() for rec in result["recommendations"])
        assert result["priority"] == "high"

    def test_recommend_blessing_negative_low_ethics(self):
        """Test recommendations for Φ- with low ethics (lines 441-443)."""
        metrics = CoreMetrics()
        vector = {
            "epc": 0.2,
            "qualia": 0.2,
            "ε": 0.2,  # Low ethics
            "κ": 0.5,
            "cadence": 0.5,
            "contradiction": 0.5,
            "presence": 0.3,
        }
        result = metrics.recommend_blessing(vector)
        assert result["blessing"] == "Φ-"
        assert any("ethical" in rec.lower() for rec in result["recommendations"])

    def test_recommend_blessing_negative_low_cadence(self):
        """Test recommendations for Φ- with low cadence (lines 445-447)."""
        metrics = CoreMetrics()
        vector = {
            "epc": 0.2,
            "qualia": 0.5,
            "ε": 0.5,
            "κ": 0.5,
            "cadence": 0.1,  # Low cadence
            "contradiction": 0.5,
            "presence": 0.3,
        }
        result = metrics.recommend_blessing(vector)
        assert result["blessing"] == "Φ-"
        assert any(
            "cadence" in rec.lower() or "flow" in rec.lower() for rec in result["recommendations"]
        )

    def test_recommend_blessing_neutral_moderate_contradiction(self):
        """Test recommendations for Φ~ with moderate contradiction (lines 450-452)."""
        metrics = CoreMetrics()
        vector = {
            "epc": 0.5,
            "qualia": 0.5,
            "ε": 0.5,
            "κ": 0.55,  # Moderate contradiction
            "cadence": 0.5,
            "contradiction": 0.55,
            "presence": 0.5,
        }
        result = metrics.recommend_blessing(vector)
        assert result["blessing"] == "Φ~"
        assert any("contradiction" in rec.lower() for rec in result["recommendations"])
        assert result["priority"] == "medium"

    def test_recommend_blessing_neutral_improve_ethics(self):
        """Test recommendations for Φ~ with low ethics (lines 454-456)."""
        metrics = CoreMetrics()
        vector = {
            "epc": 0.5,
            "qualia": 0.45,
            "ε": 0.45,  # Below 0.5
            "κ": 0.4,
            "cadence": 0.5,
            "contradiction": 0.4,
            "presence": 0.5,
        }
        result = metrics.recommend_blessing(vector)
        assert result["blessing"] == "Φ~"
        assert any(
            "ethical" in rec.lower() or "alignment" in rec.lower()
            for rec in result["recommendations"]
        )

    def test_recommend_blessing_neutral_improve_cadence(self):
        """Test recommendations for Φ~ with low cadence (lines 458-459)."""
        metrics = CoreMetrics()
        vector = {
            "epc": 0.5,
            "qualia": 0.5,
            "ε": 0.5,
            "κ": 0.4,
            "cadence": 0.4,  # Low cadence
            "contradiction": 0.4,
            "presence": 0.5,
        }
        result = metrics.recommend_blessing(vector)
        assert result["blessing"] == "Φ~"
        assert any("cadence" in rec.lower() for rec in result["recommendations"])

    def test_recommend_blessing_positive(self):
        """Test recommendations for Φ+ (lines 463-464)."""
        metrics = CoreMetrics()
        vector = {
            "epc": 0.7,
            "qualia": 0.7,
            "ε": 0.7,
            "κ": 0.3,
            "cadence": 0.7,
            "contradiction": 0.3,
            "presence": 0.7,
        }
        result = metrics.recommend_blessing(vector)
        assert result["blessing"] == "Φ+"
        assert "Maintain" in result["guidance"]
        assert result["priority"] == "low"

    def test_recommend_blessing_complete_structure(self):
        """Test that recommendations have complete structure (lines 468-475)."""
        metrics = CoreMetrics()
        vector = {
            "epc": 0.5,
            "qualia": 0.5,
            "ε": 0.5,
            "κ": 0.5,
            "cadence": 0.5,
            "contradiction": 0.5,
            "presence": 0.5,
        }
        result = metrics.recommend_blessing(vector)
        assert "blessing" in result
        assert "recommendations" in result
        assert "guidance" in result
        assert "priority" in result
        assert isinstance(result["recommendations"], list)


class TestConvenienceFunctions:
    """Test convenience functions (lines 484, 489, 494, 499)."""

    def test_create_blessing_vector_function(self):
        """Test create_blessing_vector convenience function (line 484)."""
        result = create_blessing_vector(
            cadence=0.5, qualia=0.6, entropy=0.4, contradiction=0.3, presence=0.7
        )
        assert isinstance(result, dict)
        assert "epc" in result
        assert "Φ" in result

    def test_calculate_reccs_score_function(self):
        """Test calculate_reccs_score convenience function (line 489)."""
        result = calculate_reccs_score(
            entropy=0.5, complexity=0.5, contradiction=0.5, symbolism=0.5
        )
        assert isinstance(result, dict)
        assert "score" in result
        assert "zone" in result

    def test_coherence_vector_function(self):
        """Test coherence_vector convenience function (line 494)."""
        vectors = [{"epc": 0.7, "ε": 0.6, "κ": 0.3}]
        result = coherence_vector(vectors)
        assert isinstance(result, dict)
        assert "group_coherence" in result

    def test_recommend_blessing_function(self):
        """Test recommend_blessing convenience function (line 499)."""
        vector = {
            "epc": 0.5,
            "qualia": 0.5,
            "ε": 0.5,
            "κ": 0.5,
            "cadence": 0.5,
            "contradiction": 0.5,
            "presence": 0.5,
        }
        result = recommend_blessing(vector)
        assert isinstance(result, dict)
        assert "blessing" in result
        assert "recommendations" in result


class TestCadenceAndToneDetermination:
    """Test cadence and tone determination (lines 236, 265)."""

    def test_determine_cadence_class_staccato(self):
        """Test cadence class determination - staccato."""
        metrics = CoreMetrics()
        result = metrics.determine_cadence_class(0.2)
        assert result == "staccato"

    def test_determine_cadence_class_andante(self):
        """Test cadence class determination - andante."""
        metrics = CoreMetrics()
        result = metrics.determine_cadence_class(0.45)
        assert result == "andante"

    def test_determine_cadence_class_legato(self):
        """Test cadence class determination - legato."""
        metrics = CoreMetrics()
        result = metrics.determine_cadence_class(0.7)
        assert result == "legato"

    def test_determine_cadence_class_flow(self):
        """Test cadence class determination - flow."""
        metrics = CoreMetrics()
        result = metrics.determine_cadence_class(0.9)
        assert result == "flow"

    def test_determine_cadence_class_boundary(self):
        """Test cadence class at exact boundary (line 236)."""
        metrics = CoreMetrics()
        result = metrics.determine_cadence_class(1.0)
        # At boundary, may return "unknown"
        assert result in ["flow", "unknown"]

    def test_determine_tone_dissonant(self):
        """Test tone determination - dissonant."""
        metrics = CoreMetrics()
        result = metrics.determine_tone(qualia=0.5, entropy=0.5, contradiction=0.8)
        assert result == "dissonant"

    def test_determine_tone_harmonic(self):
        """Test tone determination - harmonic."""
        metrics = CoreMetrics()
        result = metrics.determine_tone(qualia=0.8, entropy=0.5, contradiction=0.2)
        assert result == "harmonic"

    def test_determine_tone_neutral(self):
        """Test tone determination - neutral."""
        metrics = CoreMetrics()
        result = metrics.determine_tone(qualia=0.5, entropy=0.5, contradiction=0.5)
        assert result == "neutral"

    def test_determine_tone_entropic(self):
        """Test tone determination - entropic."""
        metrics = CoreMetrics()
        result = metrics.determine_tone(qualia=0.3, entropy=0.8, contradiction=0.5)
        assert result == "entropic"

    def test_determine_tone_crystalline(self):
        """Test tone determination - crystalline."""
        metrics = CoreMetrics()
        result = metrics.determine_tone(qualia=0.6, entropy=0.2, contradiction=0.2)
        assert result == "crystalline"

    def test_determine_tone_mixed(self):
        """Test tone determination - mixed (default, line 265)."""
        metrics = CoreMetrics()
        result = metrics.determine_tone(qualia=0.35, entropy=0.45, contradiction=0.55)
        assert result == "mixed"


class TestEPCComputation:
    """Test EPC computation edge cases."""

    def test_compute_epc_all_zeros(self):
        """Test EPC with all zero values."""
        metrics = CoreMetrics()
        result = metrics.compute_epc(contradiction=0.0, ethics=0.0, presence=0.0)
        assert 0.0 <= result <= 1.0

    def test_compute_epc_all_ones(self):
        """Test EPC with all maximum values."""
        metrics = CoreMetrics()
        result = metrics.compute_epc(contradiction=0.0, ethics=1.0, presence=1.0)
        assert 0.0 <= result <= 1.0

    def test_compute_epc_out_of_range(self):
        """Test EPC with out-of-range values (should clip)."""
        metrics = CoreMetrics()
        result = metrics.compute_epc(contradiction=-0.5, ethics=1.5, presence=2.0)
        assert 0.0 <= result <= 1.0

    def test_compute_epc_balanced(self):
        """Test EPC with balanced values."""
        metrics = CoreMetrics()
        result = metrics.compute_epc(contradiction=0.5, ethics=0.5, presence=0.5)
        assert 0.0 <= result <= 1.0


class TestCreateBlessingVectorComplete:
    """Test create_blessing_vector with various scenarios."""

    def test_create_blessing_vector_out_of_range_normalization(self):
        """Test create_blessing_vector normalizes out-of-range values."""
        metrics = CoreMetrics()
        result = metrics.create_blessing_vector(
            cadence=-0.5,  # Will be normalized to 0.0
            qualia=1.5,  # Will be normalized to 1.0
            entropy=2.0,  # Will be normalized to 1.0
            contradiction=-1.0,  # Will be normalized to 0.0
            presence=0.5,
        )
        assert 0.0 <= result["cadence"] <= 1.0
        assert 0.0 <= result["qualia"] <= 1.0
        assert 0.0 <= result["entropy"] <= 1.0
        assert 0.0 <= result["κ"] <= 1.0

    def test_create_blessing_vector_all_fields_present(self):
        """Test create_blessing_vector creates all required fields."""
        metrics = CoreMetrics()
        result = metrics.create_blessing_vector()
        required_fields = [
            "cadence",
            "ε",
            "entropy",
            "κ",
            "P",
            "epc",
            "cadence_class",
            "tone",
            "Φ",
            "qualia",
            "contradiction",
            "presence",
        ]
        for field in required_fields:
            assert field in result

    def test_create_blessing_vector_various_combinations(self):
        """Test create_blessing_vector with various metric combinations."""
        metrics = CoreMetrics()

        # High quality
        high_quality = metrics.create_blessing_vector(
            cadence=0.8, qualia=0.9, entropy=0.3, contradiction=0.2, presence=0.8
        )
        assert high_quality["Φ"] == "Φ+"

        # Low quality
        low_quality = metrics.create_blessing_vector(
            cadence=0.2, qualia=0.2, entropy=0.8, contradiction=0.9, presence=0.2
        )
        assert low_quality["Φ"] == "Φ-"

        # Medium quality
        medium_quality = metrics.create_blessing_vector(
            cadence=0.5, qualia=0.5, entropy=0.5, contradiction=0.5, presence=0.5
        )
        assert medium_quality["Φ"] in ["Φ~", "Φ-"]


class TestCustomConfigOptions:
    """Test CoreMetrics with custom configuration options."""

    def test_custom_cadence_classes(self):
        """Test custom cadence classes from config."""
        config = {
            "cadence": {
                "classes": {
                    "slow": (0.0, 0.4),
                    "medium": (0.4, 0.7),
                    "fast": (0.7, 1.0),
                }
            }
        }
        metrics = CoreMetrics(config)
        assert metrics.determine_cadence_class(0.3) == "slow"
        assert metrics.determine_cadence_class(0.5) == "medium"
        assert metrics.determine_cadence_class(0.8) == "fast"

    def test_custom_tones(self):
        """Test custom tone definitions from config."""
        config = {
            "tones": {
                "custom_tone": lambda q, e, c: q > 0.8 and e < 0.2,
            }
        }
        metrics = CoreMetrics(config)
        result = metrics.determine_tone(qualia=0.9, entropy=0.1, contradiction=0.5)
        assert result == "custom_tone"
