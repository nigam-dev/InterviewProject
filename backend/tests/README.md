# Backend Tests

This folder contains all test scripts for the Cricket Team Optimizer backend.

## Test Files

### 1. `test_backend.py` - Core Functionality Test
Tests the main backend components:
- Data loader (CSV reading & validation)
- Score calculator (performance formula)
- Team optimizer (Linear Programming)

**Run:**
```bash
python tests/test_backend.py
```

**Example Output:**
- ✓ Loads 30 players
- ✓ Calculates scores
- ✓ Optimizes team with budget=$100, size=7
- Shows top 5 scorers and selected team

---

### 2. `test_performance.py` - Performance Benchmarks
Measures execution time and memory efficiency:
- CSV loading time
- Score calculation time
- Optimization time
- Data type verification (Int64, float64)

**Run:**
```bash
python tests/test_performance.py
```

**Expected Results:**
- Load players: ~5-10ms
- Calculate scores: ~1-2ms
- Optimize team: ~40-50ms
- Total: <60ms

---

### 3. `test_budgets.py` - Simple Budget Tests
Tests optimization with budgets: 50, 100, 150

**Run:**
```bash
python tests/test_budgets.py
```

**Note:** All three budgets are infeasible (minimum is $153)

---

### 4. `test_all_budgets.py` - Comprehensive Budget Tests
Full constraint verification with multiple budget scenarios:
- **Phase 1:** Infeasible budgets (50, 100, 150)
- **Phase 2:** Feasible budgets (153, 175, 200)

**Run:**
```bash
python tests/test_all_budgets.py
```

**Verifies:**
- ✓ Team size = 11 players
- ✓ Total cost ≤ budget
- ✓ Score maximized

---

## Quick Test All

Run all tests:
```bash
python tests/test_backend.py
python tests/test_performance.py
python tests/test_all_budgets.py
```

## Requirements

- Backend server must be running on `http://localhost:8000` for budget tests
- Python 3.13+ with virtual environment activated
- All dependencies installed from `requirements.txt`

## Notes

- Minimum budget for 11 players: **$153**
- Optimal team (highest score): **$174** (score: 6605.8)
- All tests use cached data for performance
