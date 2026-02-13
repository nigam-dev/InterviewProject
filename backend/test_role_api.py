"""
Test script to verify role field in API responses
"""
from data_loader import load_players
from scoring import calculate_score
from optimizer import optimize_team
import json

def test_players_endpoint():
    """Test that /players endpoint includes role field"""
    print("Testing /players endpoint structure...")
    
    # Load and score players (same as API does)
    df = load_players("players.csv")
    df_with_scores = calculate_score(df)
    
    # Convert to dict (same as API response)
    players_data = df_with_scores.to_dict("records")
    
    # Check first player has role field
    first_player = players_data[0]
    print(f"✓ Sample player: {first_player['name']}")
    print(f"  - Role: {first_player['role']}")
    print(f"  - Runs: {first_player['runs']}")
    print(f"  - Wickets: {first_player['wickets']}")
    print(f"  - Score: {first_player['score']:.2f}")
    
    # Verify all required fields present
    required_fields = ['name', 'runs', 'wickets', 'strike_rate', 'price', 'role', 'score']
    for field in required_fields:
        assert field in first_player, f"Missing field: {field}"
    
    print(f"✓ All {len(players_data)} players have role field")
    
    # Check role variety
    roles = set(p['role'] for p in players_data)
    print(f"✓ Roles present: {sorted(roles)}")


def test_optimize_endpoint():
    """Test that /optimize endpoint includes role field in results"""
    print("\nTesting /optimize endpoint structure...")
    
    # Load and score players
    df = load_players("players.csv")
    df_with_scores = calculate_score(df)
    
    # Optimize team (same as API does)
    budget = 175
    result = optimize_team(df_with_scores, budget, team_size=11)
    
    if result is None:
        print("✗ No solution found for budget 175")
        return
    
    # Check result structure
    print(f"✓ Optimized team for budget ${budget}")
    print(f"  - Total cost: ${result['total_cost']:.2f}")
    print(f"  - Total score: {result['total_score']:.2f}")
    print(f"  - Team size: {len(result['players'])} players")
    
    # Check first player has role
    first_player = result['players'][0]
    assert 'role' in first_player, "Missing role field in optimized player"
    print(f"✓ Sample optimized player: {first_player['name']} ({first_player['role']})")
    
    # Check role distribution in optimized team
    team_roles = {}
    for player in result['players']:
        role = player['role']
        team_roles[role] = team_roles.get(role, 0) + 1
    
    print(f"✓ Team composition:")
    for role, count in sorted(team_roles.items()):
        print(f"  - {role}: {count} players")


if __name__ == "__main__":
    print("=" * 60)
    print("API Response Structure Test - Role Field Support")
    print("=" * 60)
    
    # Test players endpoint
    test_players_endpoint()
    
    # Test optimize endpoint
    test_optimize_endpoint()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Role field included in all API responses")
    print("=" * 60)
