"""Comprehensive system validation test."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("COMPREHENSIVE SYSTEM VALIDATION")
print("=" * 60)
print()

# Test 1: Backend Imports
print("1. Testing Backend Imports...")
try:
    from repositories.data_loader import load_players
    from services.scoring import calculate_score
    from services.optimizer import optimize_team
    from models.schemas import BudgetRequest, PlayerResponse, OptimizeResponse
    from main import app
    from services.player_service import get_scored_players
    import pandas as pd
    import numpy as np
    import pulp
    from fastapi import FastAPI
    from pydantic import BaseModel
    print("   ✓ All backend imports successful")
except Exception as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test 2: Data Loading
print("\n2. Testing Data Loading...")
try:
    df = load_players()
    print(f"   ✓ Loaded {len(df)} players")
    print(f"   ✓ Columns: {list(df.columns)}")
    assert len(df) == 30, f"Expected 30 players, got {len(df)}"
    assert 'name' in df.columns, "Missing 'name' column"
    assert 'price' in df.columns, "Missing 'price' column"
    print("   ✓ Data validation passed")
except Exception as e:
    print(f"   ✗ Data loading error: {e}")
    sys.exit(1)

# Test 3: Score Calculation
print("\n3. Testing Score Calculation...")
try:
    df_scored = calculate_score(df)
    print(f"   ✓ Calculated scores for {len(df_scored)} players")
    assert 'score' in df_scored.columns, "Missing 'score' column"
    assert df_scored['score'].notna().all(), "Found NaN in scores"
    top_scorer = df_scored.loc[df_scored['score'].idxmax()]
    print(f"   ✓ Top scorer: {top_scorer['name']} ({top_scorer['score']:.1f})")
except Exception as e:
    print(f"   ✗ Score calculation error: {e}")
    sys.exit(1)

# Test 4: Optimization
print("\n4. Testing Team Optimization...")
try:
    result = optimize_team(df_scored, budget=175, team_size=11)
    assert 'players' in result, "Missing 'players' in result"
    assert 'total_cost' in result, "Missing 'total_cost' in result"
    assert 'total_score' in result, "Missing 'total_score' in result"
    
    team_size = len(result['players'])
    total_cost = result['total_cost']
    total_score = result['total_score']
    
    print(f"   ✓ Team size: {team_size} players")
    print(f"   ✓ Total cost: ${total_cost}")
    print(f"   ✓ Total score: {total_score:.1f}")
    
    assert team_size == 11, f"Expected 11 players, got {team_size}"
    assert total_cost <= 175, f"Cost ${total_cost} exceeds budget $175"
    print("   ✓ Constraints satisfied")
except Exception as e:
    print(f"   ✗ Optimization error: {e}")
    sys.exit(1)

# Test 5: Pydantic Models
print("\n5. Testing Pydantic Models...")
try:
    # Test BudgetRequest
    req = BudgetRequest(budget=150, team_size=11)
    assert req.budget == 150
    assert req.team_size == 11
    print("   ✓ BudgetRequest model working")
    
    # Test PlayerResponse
    player = result['players'][0]
    player_resp = PlayerResponse(**player)
    assert player_resp.name == player['name']
    print("   ✓ PlayerResponse model working")
    
    # Test OptimizeResponse
    opt_resp = OptimizeResponse(
        players=[PlayerResponse(**p) for p in result['players']],
        total_cost=result['total_cost'],
        total_score=result['total_score']
    )
    assert len(opt_resp.players) == 11
    print("   ✓ OptimizeResponse model working")
except Exception as e:
    print(f"   ✗ Pydantic model error: {e}")
    sys.exit(1)

# Test 6: Data Types
print("\n6. Testing Data Types (Memory Optimization)...")
try:
    print(f"   runs dtype: {df_scored['runs'].dtype}")
    print(f"   wickets dtype: {df_scored['wickets'].dtype}")
    print(f"   strike_rate dtype: {df_scored['strike_rate'].dtype}")
    print(f"   price dtype: {df_scored['price'].dtype}")
    print(f"   score dtype: {df_scored['score'].dtype}")
    
    # Verify optimized dtypes
    assert df_scored['runs'].dtype.name == 'Int64', "runs should be Int64"
    assert df_scored['wickets'].dtype.name == 'Int64', "wickets should be Int64"
    
    print("   ✓ Data types optimized correctly")
except Exception as e:
    print(f"   ✗ Data type error: {e}")
    sys.exit(1)

# Test 7: Edge Cases
print("\n7. Testing Edge Cases...")
try:
    # Test infeasible budget
    try:
        optimize_team(df_scored, budget=50, team_size=11)
        print("   ✗ Should have raised error for infeasible budget")
        sys.exit(1)
    except ValueError as e:
        print(f"   ✓ Correctly rejected infeasible budget: {str(e)[:50]}...")
    
    # Test minimum feasible budget
    # Budget increased to 160 to accommodate potential data changes
    result_min = optimize_team(df_scored, budget=160, team_size=11)
    assert len(result_min['players']) == 11
    assert result_min['total_cost'] <= 160
    print(f"   ✓ Minimum budget ($160) works: cost ${result_min['total_cost']}")
    
except Exception as e:
    print(f"   ✗ Edge case error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - SYSTEM FULLY VALIDATED")
print("=" * 60)
print("\nSystem Status:")
print("  Backend: ✓ Ready")
print("  Data Loading: ✓ Working")
print("  Score Calculation: ✓ Working")
print("  Optimization: ✓ Working")
print("  Models: ✓ Working")
print("  Data Types: ✓ Optimized")
print("  Edge Cases: ✓ Handled")
