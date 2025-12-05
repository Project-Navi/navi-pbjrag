"""
Core Metrics Module - Unified blessing vector calculations and metrics for Crown Jewel Planner.

This module consolidates all symbolic metrics, blessing calculations, and coherence curves
into a single, comprehensive system for quantifying code qualities.
"""

from typing import Any, Dict, List, Optional

import numpy as np


class CoherenceCurve:
    """
    Implements a Pareto-weighted coherence curve for blessing evaluation.
    Replaces the traditional blessing amplifier with a more elegant mathematical approach.
    """

    def __init__(self, pareto_alpha: float = 2.0, stability_threshold: float = 0.5):
        """
        Initialize CoherenceCurve for weighted blessing evaluation.

        Parameters:
        - pareto_alpha: How sharply the Pareto curve rises (sensitivity to high values)
        - stability_threshold: Field coherence weighting—higher means more selectivity
        """
        self.pareto_alpha = pareto_alpha
        self.stability_threshold = stability_threshold

    def _pareto_weight(self, value: float) -> float:
        """
        Apply a stabilized Pareto-weighting and sigmoid clamp to a scalar in [0,1].
        """
        if value <= 0:
            return 0.0
        k = self.pareto_alpha * (1 + self.stability_threshold)
        weighted = value * (1 + k / (value**self.pareto_alpha + 1e-6))
        normalized = 2 / (1 + np.exp(-2 * weighted)) - 1
        return float(np.clip(normalized, 0.0, 1.0))

    def bless_weight(self, vector: Dict[str, Any]) -> str:
        """
        Recommends a blessing tier based on a vector of metrics, inspired by v6.1.
        """
        # Extract key metrics
        epc = vector.get("epc", 0.0)
        ethics = vector.get("qualia", 0.5)
        contradiction = vector.get("contradiction", 0.5)
        presence = vector.get("presence", 0.5)

        # Define thresholds inspired by symbolic_metrics.py and harmonic_compass_v6_1.py
        positive_thresholds = {
            "epc": 0.6,
            "ethics": 0.6,
            "contradiction": 0.45,
            "presence": 0.5,
        }

        # Check for positive blessing (Φ+)
        if (
            epc >= positive_thresholds["epc"]
            and ethics >= positive_thresholds["ethics"]
            and contradiction <= positive_thresholds["contradiction"]
            and presence >= positive_thresholds["presence"]
        ):
            return "Φ+"

        # Check for neutral blessing (Φ~) - slightly relaxed thresholds
        if epc >= 0.45 and ethics >= 0.45 and contradiction <= 0.6:
            return "Φ~"

        # Default to negative blessing (Φ-)
        return "Φ-"


class CoreMetrics:
    """
    Unified metrics system for blessing, quantization, and field analysis.
    Consolidates functionality from symbolic_metrics, blessing_metrics, and related modules.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the CoreMetrics system with optional configuration.

        Parameters:
        - config: Optional configuration dictionary for customizing metrics behavior
        """
        self.config = config or {}
        self.quantization_precision = self.config.get("quantization_precision", 4)
        self.coherence_curve = CoherenceCurve(
            pareto_alpha=self.config.get("pareto_alpha", 2.0),
            stability_threshold=self.config.get("stability_threshold", 0.5),
        )

    def quantize_scalar(self, value: float, precision: Optional[int] = None) -> float:
        """
        Quantize a scalar value to the specified precision.

        Parameters:
        - value: The scalar value to quantize
        - precision: Optional override for quantization precision

        Returns:
        - Quantized scalar value
        """
        if value is None:
            return 0.0

        p = precision if precision is not None else self.quantization_precision
        if p <= 0:
            return float(round(value))

        scale = 10**p
        return float(round(value * scale) / scale)

    def quantize_vector(
        self, vector: Dict[str, float], precision: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Quantize all values in a vector to the specified precision.

        Parameters:
        - vector: Dictionary of scalar values to quantize
        - precision: Optional override for quantization precision

        Returns:
        - Dictionary with all values quantized
        """
        return {k: self.quantize_scalar(v, precision) for k, v in vector.items()}

    def compute_epc(self, contradiction: float, ethics: float, presence: float) -> float:
        """
        Compute the Emergence Potential Coefficient (EPC), adapted from v6.1.
        This version uses a balanced geometric mean for a more holistic score.
        """
        # Ensure inputs are in [0,1] range
        c = np.clip(contradiction, 0.0, 1.0)
        e = np.clip(ethics, 0.0, 1.0)
        p = np.clip(presence, 0.0, 1.0)

        # Use a balanced set of factors. Inverse contradiction is a key component.
        values = np.array([e, p, (1 - c)], dtype=float)

        # Apply sigmoid transformation to normalize values and create S-curves
        normalized = 1 / (1 + np.exp(-10 * (values - 0.5)))

        # Calculate geometric mean for balanced influence, as seen in symbolic_metrics.py
        epc = np.prod(normalized) ** (1 / len(normalized))

        return self.quantize_scalar(float(epc))

    def create_blessing_vector(
        self,
        cadence: float = 0.0,
        qualia: float = 0.5,
        entropy: float = 0.5,
        contradiction: float = 0.5,
        presence: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Create a comprehensive blessing vector from core metrics.

        Parameters:
        - cadence: Rhythm/flow measure in range [0,1]
        - qualia: Ethical quality (ε) in range [0,1]
        - entropy: Information density/disorder in range [0,1]
        - contradiction: Contradiction pressure (κ) in range [0,1]
        - presence: Presence density (ρ) in range [0,1]

        Returns:
        - Complete blessing vector with derived metrics
        """
        # Normalize inputs
        cadence = max(0.0, min(1.0, cadence))
        qualia = max(0.0, min(1.0, qualia))
        entropy = max(0.0, min(1.0, entropy))
        contradiction = max(0.0, min(1.0, contradiction))
        presence = max(0.0, min(1.0, presence))

        # Calculate EPC
        epc = self.compute_epc(contradiction, qualia, presence)

        # Determine cadence class
        cadence_class = self.determine_cadence_class(cadence)

        # Calculate tone
        tone = self.determine_tone(qualia, entropy, contradiction)

        # Create the blessing vector
        vector = {
            "cadence": self.quantize_scalar(cadence),
            "ε": self.quantize_scalar(qualia),  # Ethical alignment
            "entropy": self.quantize_scalar(entropy),
            "κ": self.quantize_scalar(contradiction),  # Contradiction pressure
            "P": self.quantize_scalar(presence),  # Presence density
            "epc": epc,
            "cadence_class": cadence_class,
            "tone": tone,
            "qualia": qualia,  # For bless_weight compatibility
            "contradiction": contradiction,  # For bless_weight compatibility
            "presence": presence,  # For bless_weight compatibility
        }

        # Calculate blessing tier after vector is complete
        vector["Φ"] = self.coherence_curve.bless_weight(vector)

        return vector

    def determine_cadence_class(self, cadence: float) -> str:
        """
        Determine the cadence class based on the cadence value.

        Parameters:
        - cadence: Cadence value in range [0,1]

        Returns:
        - Cadence class as string
        """
        classes = self.config.get("cadence", {}).get(
            "classes",
            {
                "staccato": (0.0, 0.3),
                "andante": (0.3, 0.6),
                "legato": (0.6, 0.85),
                "flow": (0.85, 1.0),
            },
        )

        for class_name, (min_val, max_val) in classes.items():
            if min_val <= cadence < max_val:
                return class_name

        return "unknown"

    def determine_tone(self, qualia: float, entropy: float, contradiction: float) -> str:
        """
        Determine the tone based on qualia, entropy, and contradiction.

        Parameters:
        - qualia: Ethical quality (ε) in range [0,1]
        - entropy: Information density/disorder in range [0,1]
        - contradiction: Contradiction pressure (κ) in range [0,1]

        Returns:
        - Tone as string
        """
        tones = self.config.get(
            "tones",
            {
                "dissonant": lambda q, e, c: c > 0.7,
                "harmonic": lambda q, e, c: q > 0.7 and c < 0.3,
                "neutral": lambda q, e, c: 0.4 <= q <= 0.6 and 0.4 <= c <= 0.6,
                "entropic": lambda q, e, c: e > 0.7,
                "crystalline": lambda q, e, c: e < 0.3 and q > 0.5,
            },
        )

        for tone, condition in tones.items():
            if condition(qualia, entropy, contradiction):
                return tone

        return "mixed"

    def calculate_reccs_score(
        self, entropy: float, complexity: float, contradiction: float, symbolism: float
    ) -> Dict[str, float]:
        """
        Calculate RECCS (Resonance, Entropy, Complexity, Contradiction, Symbolism) score.

        Parameters:
        - entropy: Information density/disorder in range [0,1]
        - complexity: Structural complexity in range [0,1]
        - contradiction: Contradiction pressure in range [0,1]
        - symbolism: Symbolic richness in range [0,1]

        Returns:
        - Dictionary with RECCS components and overall score
        """
        # Get weights from config or use defaults
        weights = self.config.get("reccs", {}).get(
            "weights",
            {
                "entropy": 0.25,
                "complexity": 0.25,
                "contradiction": 0.25,
                "symbolism": 0.25,
            },
        )

        # Normalize inputs
        e = max(0.0, min(1.0, entropy))
        c = max(0.0, min(1.0, complexity))
        k = max(0.0, min(1.0, contradiction))
        s = max(0.0, min(1.0, symbolism))

        # Calculate weighted score
        score = (
            e * weights["entropy"]
            + c * weights["complexity"]
            + (1 - k) * weights["contradiction"]  # Invert contradiction for positive contribution
            + s * weights["symbolism"]
        )

        # Determine RECCS zone
        zone = self._determine_reccs_zone(e, c, k, s)

        return {
            "entropy": self.quantize_scalar(e),
            "complexity": self.quantize_scalar(c),
            "contradiction": self.quantize_scalar(k),
            "symbolism": self.quantize_scalar(s),
            "score": self.quantize_scalar(score),
            "zone": zone,
        }

    def _determine_reccs_zone(
        self, entropy: float, complexity: float, contradiction: float, symbolism: float
    ) -> str:
        """
        Determine the RECCS zone based on component values.

        Parameters:
        - entropy: Information density/disorder in range [0,1]
        - complexity: Structural complexity in range [0,1]
        - contradiction: Contradiction pressure in range [0,1]
        - symbolism: Symbolic richness in range [0,1]

        Returns:
        - RECCS zone as string
        """
        # High entropy, high complexity = chaos zone
        if entropy > 0.7 and complexity > 0.7:
            return "chaos"

        # Low entropy, low complexity = sterile zone
        if entropy < 0.3 and complexity < 0.3:
            return "sterile"

        # High contradiction = conflict zone
        if contradiction > 0.7:
            return "conflict"

        # High symbolism, moderate entropy/complexity = resonance zone
        if symbolism > 0.7 and 0.3 <= entropy <= 0.7 and 0.3 <= complexity <= 0.7:
            return "resonance"

        # Balanced values = flow zone
        if (
            0.4 <= entropy <= 0.6
            and 0.4 <= complexity <= 0.6
            and contradiction < 0.4
            and symbolism > 0.5
        ):
            return "flow"

        # Default
        return "transition"

    def coherence_vector(self, vectors: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate the coherence vector for a group of blessing vectors.

        Parameters:
        - vectors: List of blessing vectors to analyze

        Returns:
        - Coherence metrics for the group
        """
        if not vectors:
            return {"group_coherence": 0.0, "alignment": 0.0, "resonance": 0.0}

        # Extract key metrics from each vector
        epcs = [v.get("epc", 0.0) for v in vectors]
        ethics = [v.get("ε", 0.0) for v in vectors]
        contradictions = [v.get("κ", 0.0) for v in vectors]

        # Calculate mean values
        mean_epc = sum(epcs) / len(epcs)
        mean_ethics = sum(ethics) / len(ethics)
        mean_contradiction = sum(contradictions) / len(contradictions)

        # Calculate variance as a measure of alignment
        epc_variance = sum((x - mean_epc) ** 2 for x in epcs) / len(epcs)
        alignment = 1.0 - min(1.0, epc_variance * 4)  # Transform variance to [0,1] scale

        # Calculate resonance based on ethics and reduced contradiction
        resonance = mean_ethics * (1.0 - mean_contradiction)

        # Calculate overall group coherence
        group_coherence = (mean_epc * 0.5) + (alignment * 0.3) + (resonance * 0.2)

        # Create a minimal vector for blessing calculation
        blessing_vector = {
            "epc": mean_epc,
            "qualia": 0.5,  # Default neutral value
            "contradiction": 0.5,  # Default neutral value
            "presence": group_coherence,  # Use group coherence as presence
        }

        return {
            "group_coherence": self.quantize_scalar(group_coherence),
            "alignment": self.quantize_scalar(alignment),
            "resonance": self.quantize_scalar(resonance),
            "mean_epc": self.quantize_scalar(mean_epc),
            "blessing": self.coherence_curve.bless_weight(blessing_vector),
        }

    def recommend_blessing(self, vector: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate blessing recommendations based on a blessing vector.

        Parameters:
        - vector: Blessing vector to analyze

        Returns:
        - Dictionary with blessing recommendations
        """
        cadence = vector.get("cadence", 0.0)
        ethics = vector.get("ε", 0.0)
        contradiction = vector.get("κ", 0.0)

        # Determine blessing tier
        blessing = self.coherence_curve.bless_weight(vector)

        # Generate recommendations based on vector values
        recommendations = []

        if blessing == "Φ-":
            if contradiction > 0.7:
                recommendations.append("Reduce contradiction by resolving conflicting patterns")
            if ethics < 0.3:
                recommendations.append(
                    "Improve ethical alignment through clearer intent and documentation"
                )
            if cadence < 0.3:
                recommendations.append("Improve flow and rhythm through consistent patterns")
        elif blessing == "Φ~":
            if contradiction > 0.5:
                recommendations.append("Address moderate contradiction to improve coherence")
            if ethics < 0.5:
                recommendations.append("Strengthen ethical alignment for better resonance")
            if cadence < 0.5:
                recommendations.append("Enhance cadence for improved flow")

        # Add tier-specific guidance
        tier_guidance = {
            "Φ+": "Maintain current coherence and consider as a pattern for other components",
            "Φ~": "Component has potential but needs refinement in key areas",
            "Φ-": "Significant improvement needed for proper field coherence",
        }

        return {
            "blessing": blessing,
            "recommendations": recommendations,
            "guidance": tier_guidance.get(blessing, ""),
            "priority": {"Φ+": "low", "Φ~": "medium", "Φ-": "high"}.get(blessing, "medium"),
        }


# Singleton instance for easy access
metrics = CoreMetrics()


def create_blessing_vector(*args, **kwargs):
    """Convenience function for creating blessing vectors using the singleton instance."""
    return metrics.create_blessing_vector(*args, **kwargs)


def calculate_reccs_score(*args, **kwargs):
    """Convenience function for calculating RECCS scores using the singleton instance."""
    return metrics.calculate_reccs_score(*args, **kwargs)


def coherence_vector(*args, **kwargs):
    """Convenience function for calculating coherence vectors using the singleton instance."""
    return metrics.coherence_vector(*args, **kwargs)


def recommend_blessing(*args, **kwargs):
    """Convenience function for generating blessing recommendations using the singleton instance."""
    return metrics.recommend_blessing(*args, **kwargs)
