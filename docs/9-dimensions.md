# The 9 Dimensions of Differential Symbolic Calculus

## Overview

PBJRAG analyzes code across **9 dimensions of presence**, treating code as a living symbolic field rather than static text. Each dimension captures a different aspect of code quality, evolution, and coherence.

These dimensions are inspired by philosophical and mathematical concepts of symbolic fields, adapted for practical code analysis.

---

## The 9 Dimensions

### 1. Σ - Semantic Dimension

**What it measures:** Meaning, purpose, and clarity of the code.

**Metrics:**
- Function/variable naming quality
- Comment clarity and relevance
- API design coherence
- Intent expressiveness

**High Semantic Presence:**
```python
def calculate_compound_interest(principal: float, rate: float, years: int) -> float:
    """Calculate compound interest using the standard formula."""
    return principal * (1 + rate) ** years
```

**Low Semantic Presence:**
```python
def calc(p, r, t):
    return p * (1 + r) ** t
```

**Impact on Blessing:** High semantic presence contributes to Φ+ tier.

---

### 2. Ε - Emotional Dimension

**What it measures:** Developer intent, communication patterns, and emotional signals in code.

**Metrics:**
- Comment tone and helpfulness
- Code expressiveness vs. terseness
- Error message clarity
- Documentation empathy

**High Emotional Presence:**
```python
# This function handles edge cases gracefully to avoid surprising the caller
def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    if denominator == 0:
        logger.warning("Division by zero attempted - returning None")
        return None
    return numerator / denominator
```

**Low Emotional Presence:**
```python
def div(a, b):
    return a / b  # Will crash on zero
```

**Impact on Blessing:** Positive emotional presence enhances ethical alignment.

---

### 3. Θ - Ethical Dimension (Qualia)

**What it measures:** Code quality, best practices, and value alignment.

**Metrics:**
- Follows language idioms
- Security best practices
- Error handling completeness
- Test coverage
- Accessibility considerations

**High Ethical Presence:**
```python
def process_user_input(raw_input: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    sanitized = html.escape(raw_input)
    validated = validate_length(sanitized, max_length=1000)
    return validated
```

**Low Ethical Presence:**
```python
def process(x):
    eval(x)  # Dangerous!
```

**Impact on Blessing:** Primary driver of blessing tier. Φ+ requires ethics ≥ 0.6.

---

### 4. Τ - Temporal Dimension

**What it measures:** Evolution patterns, historical context, and change velocity.

**Metrics:**
- Code stability over time
- Refactoring frequency
- Technical debt accumulation
- API version compatibility

**High Temporal Presence:**
```python
# Stable API - unchanged for 3 years
@deprecated(version="2.0", alternative="new_api")
def legacy_function():
    """Maintained for backward compatibility until v3.0"""
    pass
```

**Low Temporal Presence:**
```python
# Changed 15 times this month
def unstable_function():
    pass
```

**Impact on Blessing:** Stable temporal patterns indicate "Stillness" phase.

---

### 5. Ξ - Entropic Dimension

**What it measures:** Chaos, unpredictability, and disorder.

**Metrics:**
- Code complexity (cyclomatic)
- Nesting depth
- Unpredictable control flow
- Magic numbers/strings

**High Entropy (Bad):**
```python
def process(x):
    if x > 10:
        if x < 100:
            if x % 2 == 0:
                return x * 2.5 + 17  # Magic numbers!
            else:
                return x / 3.7 - 42
    return 0
```

**Low Entropy (Good):**
```python
def calculate_discount(price: float, tier: str) -> float:
    DISCOUNT_RATES = {"bronze": 0.05, "silver": 0.10, "gold": 0.15}
    return price * DISCOUNT_RATES.get(tier, 0)
```

**Impact on Blessing:** High entropy pushes code toward Φ- tier and "Grinding" phase.

---

### 6. Ρ - Rhythmic Dimension

**What it measures:** Cadence, flow, patterns, and organizational structure.

**Metrics:**
- Consistent formatting
- Predictable patterns
- Balanced function sizes
- Regular module structure

**High Rhythmic Presence:**
```python
# Consistent pattern across all handlers
def handle_create(request): pass
def handle_read(request): pass
def handle_update(request): pass
def handle_delete(request): pass
```

**Low Rhythmic Presence:**
```python
# Inconsistent structure
def CreateUser(): pass
def read_post(id): pass
def UpdateRecord(data, id, user): pass
def del_comment(): pass
```

**Impact on Blessing:** Strong rhythm supports "Stillness" and Φ+ classification.

---

### 7. Ω - Contradiction Dimension

**What it measures:** Tensions, conflicts, paradoxes, and internal inconsistencies.

**Metrics:**
- Type inconsistencies
- Naming contradictions
- Conflicting design patterns
- Violated DRY principle

**High Contradiction (Bad):**
```python
class User:
    def get_user_age(self): return self.years_old
    def set_age(self, age): self.user_age = age
    def fetch_age(self): return self.age_in_years
```

**Low Contradiction (Good):**
```python
class User:
    def get_age(self): return self.age
    def set_age(self, age): self.age = age
```

**Impact on Blessing:** Critical threshold - Φ+ requires contradiction ≤ 0.45.

---

### 8. Γ - Relational Dimension

**What it measures:** Dependencies, connections, coupling, and relationships.

**Metrics:**
- Module coupling strength
- Dependency tree depth
- Import organization
- Interface clarity

**High Relational Presence:**
```python
# Clear dependency injection
class EmailService:
    def __init__(self, smtp_client: SMTPClient):
        self.client = smtp_client

    def send(self, message: Email) -> bool:
        return self.client.send(message)
```

**Low Relational Presence:**
```python
# Tight coupling
class EmailService:
    def send(self, msg):
        import smtplib  # Hidden dependency!
        smtplib.SMTP().send(msg)
```

**Impact on Blessing:** Well-managed relationships enhance coherence.

---

### 9. Μ - Emergent Dimension

**What it measures:** Novelty, surprise, creative potential, and innovation.

**Metrics:**
- Novel pattern usage
- Creative problem solving
- Unexpected abstractions
- Innovation quality

**High Emergence:**
```python
# Novel pattern: fluent builder with context management
class QueryBuilder:
    def __enter__(self):
        return self

    def where(self, condition):
        self.conditions.append(condition)
        return self

    def __exit__(self, *args):
        return self.execute()
```

**Low Emergence:**
```python
# Standard CRUD boilerplate
def create(data): db.insert(data)
def read(id): return db.get(id)
```

**Impact on Blessing:** High emergence indicates "Emergent" phase (0.8-0.9).

---

## How Dimensions Combine

### Blessing Tier Calculation

The **EPC (Emergence Potential Coefficient)** combines three key dimensions:

```python
EPC = geometric_mean([
    sigmoid(ethics),      # Θ - Ethical alignment
    sigmoid(presence),    # Ρ - Rhythmic presence
    sigmoid(1 - contradiction)  # Ω - Inverted contradiction
])
```

**Multi-dimensional thresholds:**

```
Φ+ (Excellent):
    EPC ≥ 0.6 AND ethics ≥ 0.6 AND contradiction ≤ 0.45 AND presence ≥ 0.5

Φ~ (Good):
    EPC ≥ 0.45 AND ethics ≥ 0.45 AND contradiction ≤ 0.6

Φ- (Needs Work):
    Otherwise
```

### Phase Detection

Phases use **presence (Ρ)** and **entropy (Ξ)**:

```python
phase_score = (presence - entropy + 1) / 2

if phase_score < 0.2: return "Compost"
elif phase_score < 0.35: return "Reflection"
elif phase_score < 0.5: return "Becoming"
elif phase_score < 0.65: return "Stillness"
elif phase_score < 0.8: return "Turning"
elif phase_score < 0.9: return "Emergent"
else: return "Grinding"
```

---

## Practical Examples

### Example 1: Excellent Code (Φ+)

```python
def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number using memoization.

    Args:
        n: Position in sequence (0-indexed)

    Returns:
        The nth Fibonacci number

    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    cache = {0: 0, 1: 1}

    def fib(x: int) -> int:
        if x not in cache:
            cache[x] = fib(x - 1) + fib(x - 2)
        return cache[x]

    return fib(n)
```

**Dimensional Analysis:**
- Σ Semantic: 0.9 (clear naming, purpose)
- Ε Emotional: 0.8 (helpful docs)
- Θ Ethical: 0.85 (error handling, validation)
- Τ Temporal: 0.7 (stable pattern)
- Ξ Entropic: 0.2 (low complexity)
- Ρ Rhythmic: 0.9 (consistent structure)
- Ω Contradiction: 0.15 (no conflicts)
- Γ Relational: 0.8 (clean interface)
- Μ Emergent: 0.4 (standard approach)

**Result:** Φ+ (EPC: 0.78, Phase: Stillness)

---

### Example 2: Problematic Code (Φ-)

```python
def proc(x, y, z=None):
    if x:
        if y > 10:
            return z or x * 2.5
        else:
            z = y / 3
    return z if z else x
```

**Dimensional Analysis:**
- Σ Semantic: 0.2 (unclear purpose)
- Ε Emotional: 0.1 (no documentation)
- Θ Ethical: 0.3 (no validation)
- Τ Temporal: 0.5 (unknown history)
- Ξ Entropic: 0.8 (high complexity)
- Ρ Rhythmic: 0.3 (chaotic flow)
- Ω Contradiction: 0.7 (type confusion)
- Γ Relational: 0.4 (unclear dependencies)
- Μ Emergent: 0.2 (no innovation)

**Result:** Φ- (EPC: 0.31, Phase: Compost)

---

## Using Dimensions in Practice

### Query by Dimension

```python
from pbjrag import DSCAnalyzer

analyzer = DSCAnalyzer()
chunks = analyzer.analyze_project("./my_app")

# Find high-ethical code
ethical_code = [
    chunk for chunk in chunks
    if chunk.blessing.dimensions.get("ethical", 0) > 0.7
]

# Find chaotic code (high entropy)
chaotic_code = [
    chunk for chunk in chunks
    if chunk.blessing.dimensions.get("entropic", 0) > 0.6
]

# Find innovative code (high emergence)
novel_code = [
    chunk for chunk in chunks
    if chunk.blessing.dimensions.get("emergent", 0) > 0.7
]
```

### Custom Dimension Weights

```python
from pbjrag.crown_jewel import CoreMetrics

# Emphasize ethics and rhythm
metrics = CoreMetrics(config={
    "dimension_weights": {
        "ethical": 1.5,
        "rhythmic": 1.3,
        "contradiction": 0.8
    }
})
```

---

## Mathematical Foundations

### Sigmoid Normalization

Each dimension is normalized via sigmoid to create S-curves:

```python
normalized = 1 / (1 + exp(-10 * (value - 0.5)))
```

This ensures:
- Values near 0.5 get balanced treatment
- Extreme values (0.0, 1.0) are emphasized
- Smooth transitions across the range

### Geometric Mean

The EPC uses geometric mean for holistic scoring:

```python
EPC = (ethics * presence * (1 - contradiction)) ^ (1/3)
```

Benefits:
- All dimensions must contribute (no zeros)
- Balanced influence
- Penalizes extreme imbalances

---

## Conclusion

The 9 dimensions provide a comprehensive, multi-faceted view of code quality that goes far beyond traditional metrics like cyclomatic complexity or line count. By treating code as a living symbolic field with measurable presence across these dimensions, PBJRAG enables deeper insights into code health, evolution, and potential.

Each dimension reveals a different truth about your code - together, they paint a complete picture.
