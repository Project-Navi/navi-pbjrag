# DSC Dimension Implementations

## Overview

This document describes the implementation of three critical DSC (Differential Symbolic Calculus) field dimensions in the navi-pbjrag chunker. These dimensions measure different aspects of code quality and characteristics to enable sophisticated code analysis.

## Implemented Dimensions

### 1. Entropic Field - Code Complexity/Chaos Measurement

**Location**: `/home/ndspence/GitHub/navi-pbjrag/src/pbjrag/dsc/chunker.py:996-1090`

**Purpose**: Measures code entropy, complexity, and unpredictability through control flow analysis.

**Metrics Calculated** (8 dimensions):
1. **McCabe Cyclomatic Complexity** (0.3 weight)
   - Counts decision points: if, for, while, and, or
   - Normalized by dividing by 10 (high complexity threshold)

2. **Exception Handler Complexity** (0.2 weight)
   - Counts try/except blocks
   - Normalized by dividing by 5

3. **Branch Density** (0.15 weight)
   - Control flow statements per line
   - Measures concentration of branches

4. **Loop Complexity** (0.15 weight)
   - Counts for/while/async for loops
   - Nested loops increase entropy

5. **Boolean Complexity** (0.1 weight)
   - Counts and/or operators
   - Complex conditions increase unpredictability

6. **Try Block Nesting** (0.05 weight)
   - Nested error handling complexity

7. **Raise Statement Count** (0.05 weight)
   - Exception flow indicators

8. **Overall Entropy Score** (weighted average)

**Range**: 0.0 (simple) to 1.0 (highly complex)

**Example Results**:
- Simple function: ~0.02 (very low entropy)
- Complex branching logic: ~0.58 (high entropy)

---

### 2. Rhythmic Field - Code Consistency/Flow Measurement

**Location**: `/home/ndspence/GitHub/navi-pbjrag/src/pbjrag/dsc/chunker.py:1092-1241`

**Purpose**: Measures code rhythm, consistency, and organizational patterns.

**Metrics Calculated** (8 dimensions):
1. **Naming Convention Consistency** (0.25 weight)
   - Checks snake_case vs camelCase dominance
   - Higher score when one convention dominates

2. **Indentation Consistency** (0.20 weight)
   - Checks for consistent 4-space or 2-space patterns
   - Measures adherence to indentation rhythm

3. **Line Length Variance** (0.15 weight)
   - Uses coefficient of variation (std/mean)
   - Lower variance = higher rhythm

4. **Function Size Consistency** (0.15 weight)
   - Ideal: 10-20 lines per function
   - Penalties for too short or too long

5. **Whitespace Rhythm** (0.10 weight)
   - Consistent blank line usage (1-2 blanks ideal)
   - Measures visual breathing space

6. **Statement Density** (0.15 weight)
   - Statements per line ratio
   - Ideal: ~1 statement per line

7. **Overall Rhythmic Consistency** (mean of 0-5)

8. **Code Flow Score** (weighted combination)

**Range**: 0.0 (chaotic) to 1.0 (highly consistent)

**Example Results**:
- Clean, consistent code: ~0.70 (good rhythm)
- Inconsistent formatting: ~0.58 (medium rhythm)
- Simple functions: ~0.69 (high rhythm)

---

### 3. Emergent Field - Novelty/Creativity Measurement

**Location**: `/home/ndspence/GitHub/navi-pbjrag/src/pbjrag/dsc/chunker.py:1243-1379`

**Purpose**: Measures code novelty, sophistication, and creative patterns.

**Metrics Calculated** (8 dimensions):
1. **Decorator Usage** (0.20 weight)
   - Counts @decorators on functions/classes
   - Indicates sophisticated patterns

2. **Advanced Python Features** (0.20 weight)
   - Walrus operator (:=)
   - Match statements (Python 3.10+)
   - Context managers (with statements)
   - Async/await patterns

3. **Metaprogramming Indicators** (0.15 weight)
   - `__dict__`, `__class__`, getattr, setattr
   - type(), metaclass, __new__, __init_subclass__

4. **Generator/Comprehension Usage** (0.15 weight)
   - List/set/dict comprehensions
   - Generator expressions
   - yield/yield from

5. **Functional Patterns** (0.10 weight)
   - Lambda functions
   - map, filter, reduce, partial
   - Functional programming keywords

6. **Pattern Diversity** (0.10 weight)
   - Variety of AST node types used
   - 30+ types = very diverse

7. **Special Methods** (0.10 weight)
   - Operator overloading (`__eq__`, `__hash__`, etc.)
   - Excludes common ones (`__init__`, `__new__`, `__del__`)

8. **Overall Emergence Score** (weighted combination)

**Range**: 0.0 (conventional) to 1.0 (highly novel)

**Example Results**:
- Simple code: ~0.05 (low emergence)
- Advanced features: ~0.12-0.63 (medium-high emergence)
- Metaprogramming/decorators: ~0.40+ (high emergence)

---

## Error Handling

All three methods implement graceful error handling:
- If calculation fails, returns neutral score (0.5)
- Prevents crashes from malformed or edge-case code
- Ensures chunker always produces results

## Testing

Comprehensive test suite validates the implementations:

### Basic Tests (`tests/test_dsc_dimensions.py`):
- ✓ Entropic field detects high complexity (0.583 for complex code)
- ✓ Rhythmic field detects consistency (0.693 for clean code)
- ✓ Emergent field detects novelty (0.629 for advanced code)
- ✓ All dimensions return non-zero values

### Comparison Tests (`tests/test_dimension_comparison.py`):
- ✓ Simple clean code: Low entropy, high rhythm, low emergence
- ✓ Complex branching: High entropy, medium rhythm, low emergence
- ✓ Advanced Python: Low entropy, good rhythm, high emergence
- ✓ Inconsistent code: Medium entropy, medium rhythm, low emergence

## Usage Example

```python
from pbjrag.dsc.chunker import DSCCodeChunker

# Initialize chunker
chunker = DSCCodeChunker(field_dim=8)

# Chunk code
code = """
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)
"""

chunks = chunker.chunk_code(code, "example.py")

# Access dimension metrics
for chunk in chunks:
    print(f"Entropy: {chunk.field_state.entropic.mean():.3f}")
    print(f"Rhythm: {chunk.field_state.rhythmic.mean():.3f}")
    print(f"Emergence: {chunk.field_state.emergent.mean():.3f}")
```

## Integration with DSC System

These dimensions integrate with the existing DSC chunker:

1. **Field State Extraction** (`_extract_field_state`):
   - Called during chunk creation
   - Combines all 9 field dimensions

2. **Blessing Calculation** (`_calculate_blessing_enhanced`):
   - Uses field states to determine code "blessing" tier
   - Calculates EPC (Emergence Potential Coefficient)
   - Determines phase (compost, reflection, becoming, etc.)

3. **Crown Jewel Integration**:
   - Field states converted to blessing vectors
   - Stored in FieldContainer for pattern detection
   - Used for chunk resonance calculations

## Performance

- **Efficient AST Walking**: Single pass analysis for multiple metrics
- **Normalized Metrics**: All values scaled to [0.0, 1.0] range
- **Graceful Degradation**: Neutral values (0.5) on errors
- **No External Dependencies**: Uses only Python stdlib (ast, numpy)

## Future Enhancements

Possible improvements:
1. Machine learning calibration of weights
2. Language-specific adaptations
3. Historical tracking of dimension changes
4. Correlation analysis between dimensions
5. Visualization of field states

---

**Implementation Date**: 2025-12-05
**Author**: Python ML Engineer
**Status**: Complete and Tested ✓
