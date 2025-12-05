# FCPA Fix Plan - navi-pbjrag

**Created:** 2025-12-05
**Baseline Audit:** FCPA Audit System v2.0
**Target:** Move from TOSS → CURE → Production-Ready

---

## Baseline Metrics (Pre-Fix)

| Metric | Value | Target |
|--------|-------|--------|
| **Forensic Score** | 70/100 | ≥85/100 |
| **Runability Score** | 57/100 | ≥80/100 |
| **Blessing Score** | 0.676 (Φ~) | ≥0.75 (Φ+) |
| **Test Coverage** | 4/10 (~55%) | ≥8/10 (80%) |
| **Installation** | 1/10 | ≥8/10 |
| **Developer Experience** | 2/10 | ≥7/10 |
| **Ethical Score** | 0.403 | ≥0.60 |

---

## Critical Issues Identified

### HIGH Priority
1. **Missing `requirements.txt`** - Blocks reproducibility and CI
2. **No pytest.ini** - Tests exist but no runner config
3. **Low test coverage** - 4/10 on practical assessment

### MEDIUM Priority
4. **No type hints** - DX is 2/10
5. **No sample `.env`** - Configuration undocumented
6. **Sparse inline comments** - Ethical score 0.403

### LOW Priority (Deferred)
7. High cyclomatic complexity in `pattern_analyzer.py` (23)
8. No authentication endpoints
9. Shallow VCS history

---

## Architectural Fix Strategy

### Phase 1: Foundation (HIGH Priority) - Target: +15 Runability

#### CR-001: Add requirements.txt
**Rationale:** Without explicit dependencies, `pip install -e .` works but `pip install -r requirements.txt` fails. The pyproject.toml has dependencies but no explicit pinned file for CI.

**Action:**
```bash
# Generate from pyproject.toml extras
pip freeze | grep -E "^(numpy|qdrant|chromadb|pytest)" > requirements.txt
# Add dev dependencies
echo "pytest>=8.0.0" >> requirements.txt
echo "pytest-cov>=5.0.0" >> requirements.txt
```

**Verification:** `pip install -r requirements.txt` succeeds in clean venv

---

#### CR-002: Add pytest.ini
**Rationale:** Tests exist (56 tests, 55% coverage) but no pytest configuration. FCPA scored tests 4/10 because no runner config detected.

**Action:** Create `pytest.ini` with proper configuration

**Verification:** `pytest --cov=src/pbjrag` runs with no warnings

---

### Phase 2: Quality (MEDIUM Priority) - Target: +10 Blessing

#### CR-003: Expand test coverage for golden nuggets
**Rationale:** FCPA identified 9 golden nuggets with 0% test coverage for some:
- PhaseManager (0.90 blessing) - has tests ✓
- CoreMetrics (0.84 blessing) - has tests ✓
- FieldContainer (0.78 blessing) - needs more tests
- DSCChromaStore - needs integration tests

**Action:** Add tests for untested golden nuggets

---

#### CR-004: Improve Developer Experience
**Rationale:** DX is 2/10. Issues:
- No `.env.example`
- No type hints in some modules
- Error messages not helpful

**Action:**
- Add `.env.example` with all config vars
- Add `py.typed` marker for PEP 561
- Add error handling in CLI

---

## Implementation Order

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Foundation (Runability +15)                       │
│  ├── 1. requirements.txt                                    │
│  ├── 2. pytest.ini                                          │
│  └── 3. .env.example                                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: Quality (Blessing +0.07)                          │
│  ├── 4. Add py.typed marker                                 │
│  ├── 5. Expand test coverage                                │
│  └── 6. Improve error messages                              │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: Verify                                            │
│  └── Run FCPA audit, compare metrics                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Expected Outcomes

| Metric | Before | After (Target) | Delta |
|--------|--------|----------------|-------|
| Forensic | 70 | 80 | +10 |
| Runability | 57 | 75 | +18 |
| Blessing | 0.676 | 0.73 | +0.054 |
| Installation | 1/10 | 8/10 | +7 |
| Tests | 4/10 | 8/10 | +4 |
| Dev Experience | 2/10 | 6/10 | +4 |
| Lifecycle Decision | TOSS | CURE | ✓ |

---

## NOT Doing (Deferred to Future Sprint)

1. **Microservice decomposition** - Too invasive for current scope
2. **Authentication endpoints** - Library doesn't need auth
3. **Refactor pattern_analyzer.py** - Works fine, just complex
4. **API reference docs (Sphinx)** - Nice to have, not critical

---

*This plan follows SPARC methodology: Architecturally-aligned, incremental, testable changes.*
