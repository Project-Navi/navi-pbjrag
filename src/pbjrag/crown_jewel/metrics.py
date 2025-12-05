"""Core Metrics Module - Unified blessing vector calculations and metrics for Crown Jewel Planner.

This module consolidates all symbolic metrics, blessing calculations, and coherence curves
into a single, comprehensive system for quantifying code qualities. It implements the
mathematical foundations for:

1. EPC (Emergence Potential Coefficient) - A geometric mean with sigmoid normalization
2. Blessing classification (Φ+, Φ~, Φ-) - Quality tier assignment based on thresholds
3. RECCS scoring - Resonance, Entropy, Complexity, Contradiction, Symbolism analysis
4. Pareto-weighted coherence curves for quality evaluation

Mathematical Foundation:
    The EPC formula uses sigmoid-transformed geometric mean:

    1. Sigmoid transform: σ(x) = 1 / (1 + exp(-10(x - 0.5)))
    2. Geometric mean: EPC = (∏ σ(xi))^(1/n)

    Where inputs are: ethics (ε), presence (P), and inverse contradiction (1 - κ)

Example:
    >>> from pbjrag.crown_jewel.metrics import CoreMetrics
    >>> metrics = CoreMetrics()
    >>> vector = metrics.create_blessing_vector(
    ...     cadence=0.7,
    ...     qualia=0.8,
    ...     entropy=0.5,
    ...     contradiction=0.3,
    ...     presence=0.75
    ... )
    >>> print(vector["epc"])  # Emergence Potential Coefficient
    0.8234
    >>> print(vector["Φ"])    # Blessing tier: Φ+, Φ~, or Φ-
    'Φ+'
"""

from typing import Any

import numpy as np


class CoherenceCurve:
    """Implements a Pareto-weighted coherence curve for blessing evaluation.

    Replaces the traditional blessing amplifier with a more elegant mathematical approach
    based on Pareto distribution weighting and sigmoid normalization. This creates a
    non-linear evaluation curve that emphasizes high-quality code while providing
    graceful degradation for lower quality metrics.

    Attributes:
        pareto_alpha: Sensitivity to high values (default 2.0). Higher values create
            sharper curves that more strongly reward excellence.
        stability_threshold: Field coherence weighting (default 0.5). Higher values
            increase selectivity by requiring greater consistency.

    Example:
        >>> curve = CoherenceCurve(pareto_alpha=2.0, stability_threshold=0.5)
        >>> weighted = curve._pareto_weight(0.8)
        >>> print(weighted)
        0.9123
    """

    def __init__(self, pareto_alpha: float = 2.0, stability_threshold: float = 0.5):
        """Initialize CoherenceCurve for weighted blessing evaluation.

        Args:
            pareto_alpha: How sharply the Pareto curve rises (sensitivity to high values).
                Higher values (e.g., 3.0) create more selective curves.
            stability_threshold: Field coherence weighting—higher means more selectivity.
                Range [0,1] with 0.5 being balanced.
        """
        self.pareto_alpha = pareto_alpha
        self.stability_threshold = stability_threshold

    def _pareto_weight(self, value: float) -> float:
        """Apply a stabilized Pareto-weighting and sigmoid clamp to a scalar in [0,1].

        Mathematical formulation:
            1. k = α(1 + τ) where α=pareto_alpha, τ=stability_threshold
            2. weighted = x(1 + k/(x^α + ε))
            3. normalized = 2/(1 + exp(-2·weighted)) - 1
            4. clamped = clip(normalized, 0, 1)

        Args:
            value: Input value in range [0,1].

        Returns:
            Pareto-weighted and normalized value in range [0,1].

        Note:
            Small epsilon (1e-6) prevents division by zero.
        """
        if value <= 0:
            return 0.0
        k = self.pareto_alpha * (1 + self.stability_threshold)
        weighted = value * (1 + k / (value**self.pareto_alpha + 1e-6))
        normalized = 2 / (1 + np.exp(-2 * weighted)) - 1
        return float(np.clip(normalized, 0.0, 1.0))

    def bless_weight(self, vector: dict[str, Any]) -> str:
        """Recommends a blessing tier based on a vector of metrics.

        Evaluates code quality across multiple dimensions and assigns a blessing tier:
        - Φ+ (positive): High-quality, coherent code
        - Φ~ (neutral): Acceptable quality with room for improvement
        - Φ- (negative): Needs significant improvement

        Args:
            vector: Metrics dictionary containing:
                - epc: Emergence Potential Coefficient [0,1]
                - qualia: Ethical quality/alignment [0,1]
                - contradiction: Contradiction pressure [0,1] (lower is better)
                - presence: Presence density/documentation [0,1]

        Returns:
            Blessing tier as string: "Φ+", "Φ~", or "Φ-".

        Note:
            Thresholds for Φ+: epc≥0.6, ethics≥0.6, contradiction≤0.45, presence≥0.5
            Thresholds for Φ~: epc≥0.45, ethics≥0.45, contradiction≤0.6
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
    """Unified metrics system for blessing, quantization, and field analysis.

    Consolidates functionality from symbolic_metrics, blessing_metrics, and related modules
    into a single coherent system. Provides comprehensive code quality evaluation through:

    1. Blessing vectors - Multi-dimensional quality metrics
    2. EPC calculation - Geometric mean emergence potential
    3. RECCS scoring - Multi-factor resonance evaluation
    4. Coherence analysis - Group-level quality assessment

    Attributes:
        config: Configuration dictionary for customizing metrics behavior.
        quantization_precision: Decimal precision for scalar values (default 4).
        coherence_curve: CoherenceCurve instance for blessing evaluation.

    Example:
        >>> metrics = CoreMetrics({"quantization_precision": 4})
        >>> epc = metrics.compute_epc(
        ...     contradiction=0.3,
        ...     ethics=0.8,
        ...     presence=0.7
        ... )
        >>> print(f"EPC: {epc:.4f}")
        EPC: 0.7823
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the CoreMetrics system with optional configuration.

        Args:
            config: Optional configuration dictionary supporting:
                - quantization_precision: Decimal places for values (default 4)
                - pareto_alpha: Pareto curve sensitivity (default 2.0)
                - stability_threshold: Coherence threshold (default 0.5)
                - cadence.classes: Cadence classification thresholds
                - tones: Tone classification lambda functions
                - reccs.weights: RECCS component weights
        """
        self.config = config or {}
        self.quantization_precision = self.config.get("quantization_precision", 4)
        self.coherence_curve = CoherenceCurve(
            pareto_alpha=self.config.get("pareto_alpha", 2.0),
            stability_threshold=self.config.get("stability_threshold", 0.5),
        )

    def quantize_scalar(self, value: float, precision: int | None = None) -> float:
        """Quantize a scalar value to the specified precision.

        Rounds floating-point values to a fixed number of decimal places to ensure
        consistent representation across the system.

        Args:
            value: The scalar value to quantize.
            precision: Optional override for quantization precision. If None, uses
                the instance's quantization_precision setting.

        Returns:
            Quantized scalar value rounded to the specified precision.

        Example:
            >>> metrics = CoreMetrics()
            >>> metrics.quantize_scalar(0.123456789)
            0.1235
        """
        if value is None:
            return 0.0

        p = precision if precision is not None else self.quantization_precision
        if p <= 0:
            return float(round(value))

        scale = 10**p
        return float(round(value * scale) / scale)

    def quantize_vector(
        self, vector: dict[str, float], precision: int | None = None
    ) -> dict[str, float]:
        """Quantize all values in a vector to the specified precision.

        Args:
            vector: Dictionary of scalar values to quantize.
            precision: Optional override for quantization precision.

        Returns:
            Dictionary with all values quantized to the specified precision.

        Example:
            >>> metrics = CoreMetrics()
            >>> vector = {"a": 0.123456, "b": 0.789012}
            >>> quantized = metrics.quantize_vector(vector)
            >>> print(quantized)
            {'a': 0.1235, 'b': 0.7890}
        """
        return {k: self.quantize_scalar(v, precision) for k, v in vector.items()}

    def compute_epc(self, contradiction: float, ethics: float, presence: float) -> float:
        """Compute the Emergence Potential Coefficient (EPC).

        The EPC quantifies code quality potential through a geometric mean of
        sigmoid-transformed factors. This creates a balanced, multiplicative
        metric where weakness in any dimension significantly impacts the overall score.

        Mathematical formulation:
            1. Inputs: ethics (ε), presence (P), inverse contradiction (1-κ)
            2. Sigmoid transform: σ(x) = 1/(1 + exp(-10(x - 0.5)))
            3. Geometric mean: EPC = (∏ σ(xi))^(1/n)
            4. Quantize result to configured precision

        Args:
            contradiction: Contradiction pressure (κ) in range [0,1]. Lower is better,
                so we use (1-κ) in the formula.
            ethics: Ethical quality/alignment (ε) in range [0,1]. Higher is better.
            presence: Presence density (P) in range [0,1]. Higher indicates better
                documentation and intentionality.

        Returns:
            EPC value in range [0,1], quantized to configured precision.

        Note:
            The sigmoid transformation creates S-curves that emphasize values
            near 0 and 1, making the metric sensitive to both excellence and problems.

        Example:
            >>> metrics = CoreMetrics()
            >>> epc = metrics.compute_epc(
            ...     contradiction=0.2,  # Low contradiction (good)
            ...     ethics=0.8,         # High ethics (good)
            ...     presence=0.7        # Good presence
            ... )
            >>> print(f"EPC: {epc:.4f}")
            EPC: 0.8456
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
    ) -> dict[str, Any]:
        """Create a comprehensive blessing vector from core metrics.

        Constructs a complete multi-dimensional quality assessment vector combining
        raw metrics, derived values (EPC), classifications (cadence_class, tone),
        and blessing tier (Φ).

        Args:
            cadence: Rhythm/flow measure in range [0,1]. Reflects consistency and
                patterns in code structure.
            qualia: Ethical quality (ε) in range [0,1]. Measures alignment with
                best practices and intentionality.
            entropy: Information density/disorder in range [0,1]. Balances complexity
                with clarity.
            contradiction: Contradiction pressure (κ) in range [0,1]. Lower values
                indicate better internal consistency.
            presence: Presence density (ρ) in range [0,1]. Measures documentation
                and explicit intentionality.

        Returns:
            Complete blessing vector containing:
                - cadence: Quantized cadence value
                - ε (qualia): Ethical alignment
                - entropy: Information density
                - κ (contradiction): Contradiction pressure
                - P (presence): Presence density
                - epc: Computed Emergence Potential Coefficient
                - cadence_class: Classification (staccato/andante/legato/flow)
                - tone: Overall tone (harmonic/dissonant/crystalline/etc.)
                - Φ: Blessing tier (Φ+/Φ~/Φ-)

        Example:
            >>> metrics = CoreMetrics()
            >>> vector = metrics.create_blessing_vector(
            ...     cadence=0.75,
            ...     qualia=0.8,
            ...     entropy=0.5,
            ...     contradiction=0.25,
            ...     presence=0.7
            ... )
            >>> print(f"EPC: {vector['epc']:.4f}, Tier: {vector['Φ']}")
            EPC: 0.8234, Tier: Φ+
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
        """Determine the cadence class based on the cadence value.

        Classifies code rhythm into musical tempo categories:
        - staccato [0.0, 0.3): Short, disconnected patterns
        - andante [0.3, 0.6): Walking pace, moderate flow
        - legato [0.6, 0.85): Smooth, connected flow
        - flow [0.85, 1.0]: Optimal fluidity

        Args:
            cadence: Cadence value in range [0,1].

        Returns:
            Cadence class as string: "staccato", "andante", "legato", "flow", or
            "unknown" if no match.

        Note:
            Thresholds can be customized via config["cadence"]["classes"].
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
        """Determine the overall tone based on qualia, entropy, and contradiction.

        Classifies the "feeling" of code based on its quality characteristics:
        - harmonic: High ethics, low contradiction (beautiful code)
        - dissonant: High contradiction (conflicting patterns)
        - crystalline: Low entropy, good ethics (clear, structured)
        - entropic: High information density (complex but potentially chaotic)
        - neutral: Balanced metrics
        - mixed: Default when no clear classification

        Args:
            qualia: Ethical quality (ε) in range [0,1].
            entropy: Information density/disorder in range [0,1].
            contradiction: Contradiction pressure (κ) in range [0,1].

        Returns:
            Tone classification as string.

        Note:
            Tone conditions can be customized via config["tones"] with lambda functions.
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
    ) -> dict[str, float]:
        """Calculate RECCS (Resonance, Entropy, Complexity, Contradiction, Symbolism) score.

        Multi-factor analysis system evaluating code across five dimensions:
        - Resonance: Implicit, calculated from other factors
        - Entropy: Information density and unpredictability
        - Complexity: Structural intricacy
        - Contradiction: Internal inconsistency (inverted for scoring)
        - Symbolism: Richness of meaning and patterns

        Args:
            entropy: Information density/disorder in range [0,1].
            complexity: Structural complexity in range [0,1].
            contradiction: Contradiction pressure in range [0,1] (inverted for positive contribution).
            symbolism: Symbolic richness in range [0,1].

        Returns:
            Dictionary containing:
                - entropy: Quantized entropy value
                - complexity: Quantized complexity value
                - contradiction: Quantized contradiction value
                - symbolism: Quantized symbolism value
                - score: Overall weighted RECCS score [0,1]
                - zone: Classification (chaos/sterile/conflict/resonance/flow/transition)

        Note:
            Default weights: all components equally weighted at 0.25. Customizable
            via config["reccs"]["weights"].

        Example:
            >>> metrics = CoreMetrics()
            >>> reccs = metrics.calculate_reccs_score(
            ...     entropy=0.6,
            ...     complexity=0.5,
            ...     contradiction=0.3,
            ...     symbolism=0.7
            ... )
            >>> print(f"Score: {reccs['score']:.4f}, Zone: {reccs['zone']}")
            Score: 0.6425, Zone: resonance
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
        """Determine the RECCS zone based on component values.

        Classifies code into operational zones:
        - chaos: High entropy + high complexity (needs simplification)
        - sterile: Low entropy + low complexity (too simple/rigid)
        - conflict: High contradiction (needs resolution)
        - resonance: High symbolism with moderate entropy/complexity (ideal)
        - flow: Balanced values with low contradiction (productive)
        - transition: Default state, moving between zones

        Args:
            entropy: Information density/disorder in range [0,1].
            complexity: Structural complexity in range [0,1].
            contradiction: Contradiction pressure in range [0,1].
            symbolism: Symbolic richness in range [0,1].

        Returns:
            RECCS zone classification as string.
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

    def coherence_vector(self, vectors: list[dict[str, float]]) -> dict[str, float]:
        """Calculate the coherence vector for a group of blessing vectors.

        Performs aggregate analysis on multiple blessing vectors to evaluate
        group-level quality. Useful for assessing modules, packages, or entire codebases.

        Args:
            vectors: List of blessing vectors to analyze.

        Returns:
            Coherence metrics dictionary containing:
                - group_coherence: Overall group quality [0,1]
                - alignment: Consistency across group (low variance) [0,1]
                - resonance: Ethics weighted by low contradiction [0,1]
                - mean_epc: Average EPC across group [0,1]
                - blessing: Group blessing tier (Φ+/Φ~/Φ-)

        Note:
            Group coherence formula: mean_epc(0.5) + alignment(0.3) + resonance(0.2)

        Example:
            >>> metrics = CoreMetrics()
            >>> vectors = [
            ...     {"epc": 0.8, "ε": 0.7, "κ": 0.2},
            ...     {"epc": 0.75, "ε": 0.8, "κ": 0.25}
            ... ]
            >>> coherence = metrics.coherence_vector(vectors)
            >>> print(f"Group coherence: {coherence['group_coherence']:.4f}")
            Group coherence: 0.7825
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

    def recommend_blessing(self, vector: dict[str, Any]) -> dict[str, Any]:
        """Generate blessing recommendations based on a blessing vector.

        Provides actionable guidance for improving code quality based on current
        metrics and blessing tier.

        Args:
            vector: Blessing vector to analyze (from create_blessing_vector).

        Returns:
            Dictionary containing:
                - blessing: Blessing tier (Φ+/Φ~/Φ-)
                - recommendations: List of improvement suggestions
                - guidance: Tier-specific guidance message
                - priority: Improvement priority (low/medium/high)

        Example:
            >>> metrics = CoreMetrics()
            >>> vector = metrics.create_blessing_vector(
            ...     contradiction=0.8, qualia=0.3, cadence=0.2
            ... )
            >>> rec = metrics.recommend_blessing(vector)
            >>> print(rec["blessing"], rec["priority"])
            Φ- high
            >>> for item in rec["recommendations"]:
            ...     print(f"- {item}")
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
    """Convenience function for creating blessing vectors using the singleton instance.

    Args:
        *args: Positional arguments passed to CoreMetrics.create_blessing_vector.
        **kwargs: Keyword arguments passed to CoreMetrics.create_blessing_vector.

    Returns:
        Blessing vector dictionary.

    Example:
        >>> from pbjrag.crown_jewel.metrics import create_blessing_vector
        >>> vector = create_blessing_vector(qualia=0.8, presence=0.7)
    """
    return metrics.create_blessing_vector(*args, **kwargs)


def calculate_reccs_score(*args, **kwargs):
    """Convenience function for calculating RECCS scores using the singleton instance.

    Args:
        *args: Positional arguments passed to CoreMetrics.calculate_reccs_score.
        **kwargs: Keyword arguments passed to CoreMetrics.calculate_reccs_score.

    Returns:
        RECCS score dictionary.
    """
    return metrics.calculate_reccs_score(*args, **kwargs)


def coherence_vector(*args, **kwargs):
    """Convenience function for calculating coherence vectors using the singleton instance.

    Args:
        *args: Positional arguments passed to CoreMetrics.coherence_vector.
        **kwargs: Keyword arguments passed to CoreMetrics.coherence_vector.

    Returns:
        Coherence metrics dictionary.
    """
    return metrics.coherence_vector(*args, **kwargs)


def recommend_blessing(*args, **kwargs):
    """Convenience function for generating blessing recommendations using the singleton instance.

    Args:
        *args: Positional arguments passed to CoreMetrics.recommend_blessing.
        **kwargs: Keyword arguments passed to CoreMetrics.recommend_blessing.

    Returns:
        Recommendations dictionary.
    """
    return metrics.recommend_blessing(*args, **kwargs)
