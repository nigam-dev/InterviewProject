from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_full_system_flow():
    """
    Integration test checking the full flow:
    1. Load players data via API
    2. Optimize team with constraints
    3. Validate constraints and strategy results
    """
    
    # 1. Load All Players
    # -------------------
    response = client.get("/players")
    assert response.status_code == 200, "Failed to fetch players"
    players = response.json()
    assert len(players) > 0, "No players loaded"
    
    # Verify player structure
    sample_player = players[0]
    required_fields = ["name", "role", "price", "score"]
    for field in required_fields:
        assert field in sample_player, f"Missing field {field} in player response"

    # 2. Optimize Team (MAX_SCORE)
    # ----------------------------
    # Use a safe budget to ensure a solution exists. 
    # Based on data, price avg ~10-15? 175 is the UI default.
    budget = 175
    team_size = 11
    
    payload = {
        "budget": budget,
        "team_size": team_size,
        "strategy": "MAX_SCORE"
    }
    
    response = client.post("/optimize", json=payload)
    if response.status_code != 200:
        pytest.fail(f"Optimization failed: {response.text}")
        
    result = response.json()
    
    # 3. Validate Constraints
    # -----------------------
    selected_players = result["players"]
    
    # A. Team Size
    assert len(selected_players) == team_size, f"Expected {team_size} players, got {len(selected_players)}"
    
    # B. Budget Constraint
    total_cost = result["total_cost"]
    assert total_cost <= budget, f"Total cost {total_cost} exceeds budget {budget}"
    
    # C. Role Constraints (Default: WK=1, BAT=4, BOWL=3, ALL=3)
    roles = [p["role"] for p in selected_players]
    role_counts = {role: roles.count(role) for role in set(roles)}
    
    assert role_counts.get("WK", 0) == 1, f"Expected 1 WK, got {role_counts.get('WK', 0)}"
    assert role_counts.get("BAT", 0) == 4, f"Expected 4 BAT, got {role_counts.get('BAT', 0)}"
    assert role_counts.get("BOWL", 0) == 3, f"Expected 3 BOWL, got {role_counts.get('BOWL', 0)}"
    assert role_counts.get("ALL", 0) == 3, f"Expected 3 ALL, got {role_counts.get('ALL', 0)}"

    # 4. Strategy Variation (MAX_SCORE_PER_COST)
    # ------------------------------------------
    payload_eff = {
        "budget": budget,
        "team_size": team_size,
        "strategy": "MAX_SCORE_PER_COST"
    }
    
    response_eff = client.post("/optimize", json=payload_eff)
    assert response_eff.status_code == 200
    
    result_eff = response_eff.json()
    assert len(result_eff["players"]) == 11
    assert result_eff["total_cost"] <= budget
    
    # Efficiency strategy often results in cheaper teams (but not always, depends on score/cost ratio)
    # We just ensure it produces a valid valid team.
    
    print("\n✓ Full system integration test passed")
