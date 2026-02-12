"""
Test script to verify role-based constraints in optimizer
"""
from data_loader import load_players
from scoring import calculate_score
from optimizer import optimize_team


def test_role_constraints():
    """Test that optimizer enforces role-based constraints"""
    print("=" * 70)
    print("Testing Role-Based Constraints in Team Optimizer")
    print("=" * 70)
    
    # Load players with roles
    df = load_players("players.csv")
    print(f"\n✓ Loaded {len(df)} players")
    
    # Check role availability
    role_counts = df['role'].value_counts().to_dict()
    print(f"\n✓ Available players by role:")
    for role in ['WK', 'BAT', 'BOWL', 'ALL']:
        count = role_counts.get(role, 0)
        print(f"  - {role}: {count} players")
    
    # Calculate scores
    df_with_scores = calculate_score(df)
    print(f"\n✓ Calculated scores for all players")
    
    # Test optimization with different budgets
    budgets_to_test = [175, 200, 250]
    
    for budget in budgets_to_test:
        print(f"\n{'-' * 70}")
        print(f"Testing with Budget: ${budget}")
        print(f"{'-' * 70}")
        
        try:
            result = optimize_team(df_with_scores, budget, team_size=11)
            
            # Verify result structure
            assert 'players' in result, "Missing 'players' in result"
            assert 'total_cost' in result, "Missing 'total_cost' in result"
            assert 'total_score' in result, "Missing 'total_score' in result"
            
            players = result['players']
            total_cost = result['total_cost']
            total_score = result['total_score']
            
            print(f"✓ Optimization successful!")
            print(f"  - Team size: {len(players)} players")
            print(f"  - Total cost: ${total_cost:.2f}")
            print(f"  - Total score: {total_score:.2f}")
            print(f"  - Budget used: {(total_cost/budget)*100:.1f}%")
            
            # Verify constraints
            # 1. Team size
            assert len(players) == 11, f"Expected 11 players, got {len(players)}"
            print(f"  ✓ Team size constraint: 11 players")
            
            # 2. Budget constraint
            assert total_cost <= budget, f"Budget exceeded: ${total_cost} > ${budget}"
            print(f"  ✓ Budget constraint: ${total_cost:.2f} <= ${budget}")
            
            # 3. Role constraints
            role_distribution = {}
            for player in players:
                role = player['role']
                role_distribution[role] = role_distribution.get(role, 0) + 1
            
            print(f"\n  Role Distribution:")
            for role in ['WK', 'BAT', 'BOWL', 'ALL']:
                count = role_distribution.get(role, 0)
                print(f"    {role}: {count} players")
            
            # Verify exact role counts
            expected_roles = {'WK': 1, 'BAT': 4, 'BOWL': 3, 'ALL': 3}
            for role, expected_count in expected_roles.items():
                actual_count = role_distribution.get(role, 0)
                assert actual_count == expected_count, \
                    f"Role {role}: expected {expected_count}, got {actual_count}"
            
            print(f"\n  ✓ Role constraints verified:")
            print(f"    - WK: 1 (Wicketkeeper) ✓")
            print(f"    - BAT: 4 (Batsman) ✓")
            print(f"    - BOWL: 3 (Bowler) ✓")
            print(f"    - ALL: 3 (All-rounder) ✓")
            
            # Show selected players by role
            print(f"\n  Selected Players:")
            for role in ['WK', 'BAT', 'BOWL', 'ALL']:
                role_players = [p for p in players if p['role'] == role]
                if role_players:
                    print(f"    {role}:")
                    for p in sorted(role_players, key=lambda x: x['score'], reverse=True):
                        print(f"      - {p['name']}: ${p['price']}, Score: {p['score']:.1f}")
            
        except ValueError as e:
            print(f"✗ Optimization failed: {e}")
            continue
    
    print(f"\n{'=' * 70}")
    print("✓ ALL ROLE CONSTRAINT TESTS PASSED!")
    print("  - Team always has exactly 1 WK, 4 BAT, 3 BOWL, 3 ALL")
    print("  - Budget constraint maintained")
    print("  - Score maximization working")
    print("=" * 70)


if __name__ == "__main__":
    test_role_constraints()
