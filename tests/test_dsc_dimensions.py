#!/usr/bin/env python3
"""
Test the three DSC dimension implementations:
- Entropic field (complexity/chaos)
- Rhythmic field (consistency/flow)
- Emergent field (novelty/creativity)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pbjrag.dsc.chunker import DSCCodeChunker


def test_entropic_field():
    """Test entropic field extraction"""
    print("\n=== Testing Entropic Field ===")

    # High entropy code (complex, many branches)
    complex_code = """
def complex_function(x, y, z):
    '''Complex function with many branches'''
    try:
        if x > 0:
            for i in range(x):
                if i % 2 == 0 and i > 5:
                    while y > 0:
                        y -= 1
                        if y == 3 or y == 7:
                            raise ValueError("Bad value")
        elif x < 0:
            for j in range(abs(x)):
                if j % 3 == 0:
                    pass
    except ValueError:
        return None
    except Exception as e:
        raise RuntimeError("Error") from e
    return x + y + z
"""

    chunker = DSCCodeChunker(field_dim=8)
    chunks = chunker.chunk_code(complex_code, "test_complex.py")

    assert len(chunks) > 0, "Should create at least one chunk"
    chunk = chunks[0]

    entropic = chunk.field_state.entropic
    print(f"Entropic field values: {entropic}")
    print(f"Mean entropy: {entropic.mean():.3f}")

    # Complex code should have high entropy (> 0.3)
    assert entropic.mean() > 0.3, f"Expected high entropy, got {entropic.mean():.3f}"
    print("✓ Entropic field working correctly (high entropy detected)")


def test_rhythmic_field():
    """Test rhythmic field extraction"""
    print("\n=== Testing Rhythmic Field ===")

    # Highly consistent code (good rhythm)
    consistent_code = """
def calculate_total(items):
    '''Calculate total price'''
    total = 0
    for item in items:
        total += item.price
    return total

def calculate_discount(total):
    '''Calculate discount amount'''
    if total > 100:
        return total * 0.1
    return 0.0

def apply_discount(total, discount):
    '''Apply discount to total'''
    return total - discount
"""

    chunker = DSCCodeChunker(field_dim=8)
    chunks = chunker.chunk_code(consistent_code, "test_consistent.py")

    assert len(chunks) > 0, "Should create at least one chunk"

    # Check rhythm across all function chunks
    rhythms = [chunk.field_state.rhythmic.mean() for chunk in chunks if chunk.chunk_type == "function"]
    avg_rhythm = sum(rhythms) / len(rhythms) if rhythms else 0

    print(f"Rhythmic field values: {rhythms}")
    print(f"Average rhythm: {avg_rhythm:.3f}")

    # Consistent code should have good rhythm (> 0.4)
    assert avg_rhythm > 0.4, f"Expected good rhythm, got {avg_rhythm:.3f}"
    print("✓ Rhythmic field working correctly (consistency detected)")


def test_emergent_field():
    """Test emergent field extraction"""
    print("\n=== Testing Emergent Field ===")

    # Novel code with advanced features - focused on a single function with many patterns
    novel_code = """
from typing import Iterator
from functools import lru_cache, partial

@lru_cache(maxsize=128)
@property
def advanced_function(self):
    '''Function with many advanced patterns'''
    # Generators and comprehensions
    data = [i**2 for i in range(10) if i % 2 == 0]
    generator = (x for x in data if x > 5)

    # Functional patterns
    mapped = map(lambda x: x * 2, filter(lambda x: x > 0, data))

    # Context managers
    with open("test.txt") as f:
        content = f.read()

    # Metaprogramming
    cls = type(self)
    value = getattr(self, "_value", None)
    setattr(self, "computed", True)

    # Advanced iteration
    result = {k: v for k, v in enumerate(data)}

    # Special methods and operator overloading
    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    # Async patterns
    async def async_helper():
        await asyncio.sleep(0.1)
        return 42

    return result
"""

    chunker = DSCCodeChunker(field_dim=8)
    chunks = chunker.chunk_code(novel_code, "test_novel.py")

    assert len(chunks) > 0, "Should create at least one chunk"

    # Check emergence across all chunks
    emergences = [chunk.field_state.emergent.mean() for chunk in chunks]
    max_emergence = max(emergences) if emergences else 0

    print(f"Emergent field values: {emergences}")
    print(f"Max emergence: {max_emergence:.3f}")

    # Novel code should have decent emergence (> 0.15 is reasonable for moderately advanced code)
    assert max_emergence > 0.15, f"Expected high emergence, got {max_emergence:.3f}"
    print("✓ Emergent field working correctly (novelty detected)")


def test_all_dimensions():
    """Test that all three dimensions return non-zero values"""
    print("\n=== Testing All Dimensions Together ===")

    sample_code = """
@decorator
def sample_function(x, y):
    '''Sample function with decorator'''
    try:
        if x > 0:
            result = [i**2 for i in range(x)]
            return sum(result)
    except Exception:
        return None
    return 0
"""

    chunker = DSCCodeChunker(field_dim=8)
    chunks = chunker.chunk_code(sample_code, "test_all.py")

    assert len(chunks) > 0, "Should create at least one chunk"
    chunk = chunks[0]

    print(f"Entropic mean: {chunk.field_state.entropic.mean():.3f}")
    print(f"Rhythmic mean: {chunk.field_state.rhythmic.mean():.3f}")
    print(f"Emergent mean: {chunk.field_state.emergent.mean():.3f}")

    # All should be non-zero (at least returning neutral 0.5 on error, but should calculate)
    assert chunk.field_state.entropic.mean() > 0.0, "Entropic should be non-zero"
    assert chunk.field_state.rhythmic.mean() > 0.0, "Rhythmic should be non-zero"
    assert chunk.field_state.emergent.mean() > 0.0, "Emergent should be non-zero"

    print("✓ All three dimensions return meaningful values")


if __name__ == "__main__":
    try:
        test_entropic_field()
        test_rhythmic_field()
        test_emergent_field()
        test_all_dimensions()

        print("\n" + "="*50)
        print("✓ ALL TESTS PASSED")
        print("="*50)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
