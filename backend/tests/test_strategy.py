import pandas as pd
import pytest
from optimizer import optimize_team
from models import OptimizationStrategy

@pytest.fixture
def optimization_dataset():
    """Create a dataset that allows for a valid team selection."""
    # Create 15 players with different roles and prices
    # Roles: 2 WK, 5 BAT, 4 BOWL, 4 ALL
    data = []
    
    # Wicket Keepers (need 1)
    data.append({"name": "WK1", "role": "WK", "price": 10.0, "score": 100})
    data.append({"name": "WK2", "role": "WK", "price": 8.0, "score": 80})
    
    # Batsmen (need 4)
    for i in range(1, 6):
        data.append({"name": f"BAT{i}", "role": "BAT", "price": 9.0, "score": 90})
        
    # Bowlers (need 3)
    for i in range(1, 5):
        data.append({"name": f"BOWL{i}", "role": "BOWL", "price": 8.5, "score": 85})
        
    # All Rounders (need 3)
    for i in range(1, 5):
        data.append({"name": f"ALL{i}", "role": "ALL", "price": 11.0, "score": 110})
        
    return pd.DataFrame(data)

def test_optimize_team_budget_constraint(optimization_dataset):
    """Test that the optimization respects the budget constraint."""
    budget = 110.0  # Sufficient budget (min cost ~102.5)
    result = optimize_team(optimization_dataset, budget=budget, team_size=11)
    
    total_cost = result["total_cost"]
    assert total_cost <= budget
    assert len(result["players"]) == 11

def test_optimize_team_size_constraint(optimization_dataset):
    """Test that the optimization returns exactly the requested team size."""
    team_size = 11
    result = optimize_team(optimization_dataset, budget=200.0, team_size=team_size)
    
    assert len(result["players"]) == team_size

def test_optimize_team_role_constraints(optimization_dataset):
    """Test that default role constraints are met using default logic."""
    # Default constraints: WK=1, BAT=4, BOWL=3, ALL=3 = 11 total
    result = optimize_team(optimization_dataset, budget=200.0, team_size=11)
    
    roles = [p["role"] for p in result["players"]]
    
    assert roles.count("WK") == 1
    assert roles.count("BAT") == 4
    assert roles.count("BOWL") == 3
    assert roles.count("ALL") == 3

def test_optimize_team_impossible_budget(optimization_dataset):
    """Test that optimization fails if budget is too low."""
    # Minimum cost for 11 players in dataset is around 102.5. So budget 50 should fail.
    with pytest.raises(ValueError, match="No optimal solution found"):
        optimize_team(optimization_dataset, budget=50.0, team_size=11)

def test_optimization_strategies_logic():
    """Test that different strategies yield expected results."""
    # Create simple dataset
    data = [
        {"name": "P1", "role": "GEN", "price": 10.0, "score": 100},  # Eff: 10
        {"name": "P2", "role": "GEN", "price": 5.0,  "score": 60},   # Eff: 12
        {"name": "P3", "role": "GEN", "price": 5.0,  "score": 60},   # Eff: 12
    ]
    df = pd.DataFrame(data)
    
    # Custom constraints: Select 2 GEN players
    constraints = {"GEN": 2} # Total team size 2
    
    # Strategy 1: MAX_SCORE
    # Should pick P1 (100) and one of P2/P3 (60) = Total 160
    res_score = optimize_team(
        df, 
        budget=20, 
        team_size=2, 
        role_constraints=constraints,
        strategy=OptimizationStrategy.MAX_SCORE
    )
    names_score = sorted([p["name"] for p in res_score["players"]])
    # P1 must be in it
    assert "P1" in names_score
    assert res_score["total_score"] == 160.0

    # Strategy 2: MAX_SCORE_PER_COST
    # Should pick P2 (12 eff) and P3 (12 eff) = Total efficiency 24
    # (P1+P2 would be sum eff 10+12=22)
    # Total score will be 120 (lower than 160), but efficiency sum is higher.
    res_eff = optimize_team(
        df, 
        budget=20, 
        team_size=2, 
        role_constraints=constraints,
        strategy=OptimizationStrategy.MAX_SCORE_PER_COST
    )
    names_eff = sorted([p["name"] for p in res_eff["players"]])
    assert names_eff == ["P2", "P3"]
    assert res_eff["total_score"] == 120.0
