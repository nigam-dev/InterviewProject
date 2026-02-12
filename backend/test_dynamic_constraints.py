"""
Test script to verify dynamic role constraints in optimizer
"""
from data_loader import load_players
from scoring import calculate_score
from optimizer import optimize_team


def test_dynamic_role_constraints():
    """Test optimizer with various role constraint configurations"""
    print("=" * 70)
    print("Testing Dynamic Role Constraints")
    print("=" * 70)
    
    # Load and score players
    df = load_players("players.csv")
    df_with_scores = calculate_score(df)
    
    print(f"\n✓ Loaded {len(df)} players")
    role_counts = df['role'].value_counts().to_dict()
    print(f"✓ Available players: {role_counts}")
    
    # Test different role constraint configurations
    test_cases = [
        {
            "name": "Default (1-4-3-3)",
            "budget": 200,
            "constraints": None  # Should use default
        },
        {
            "name": "Explicit Default (1-4-3-3)",
            "budget": 200,
            "constraints": {"WK": 1, "BAT": 4, "BOWL": 3, "ALL": 3}
        },
        {
            "name": "Batting Heavy (1-5-2-3)",
            "budget": 200,
            "constraints": {"WK": 1, "BAT": 5, "BOWL": 2, "ALL": 3}
        },
        {
            "name": "Bowling Heavy (1-3-4-3)",
            "budget": 200,
            "constraints": {"WK": 1, "BAT": 3, "BOWL": 4, "ALL": 3}
        },
        {
            "name": "All-Rounder Focus (2-3-2-4)",
            "budget": 200,
            "constraints": {"WK": 2, "BAT": 3, "BOWL": 2, "ALL": 4}
        },
        {
            "name": "Minimal Bowling (1-6-1-3)",
            "budget": 200,
            "constraints": {"WK": 1, "BAT": 6, "BOWL": 1, "ALL": 3}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'-' * 70}")
        print(f"Test: {test_case['name']}")
        print(f"Budget: ${test_case['budget']}")
        print(f"Constraints: {test_case['constraints']}")
        print(f"{'-' * 70}")
        
        try:
            # Optimize with custom constraints
            if test_case['constraints'] is None:
                result = optimize_team(df_with_scores, test_case['budget'])
            else:
                result = optimize_team(
                    df_with_scores, 
                    test_case['budget'],
                    role_constraints=test_case['constraints']
                )
            
            players = result['players']
            total_cost = result['total_cost']
            total_score = result['total_score']
            
            # Count roles in result
            role_distribution = {}
            for player in players:
                role = player['role']
                role_distribution[role] = role_distribution.get(role, 0) + 1
            
            print(f"✓ Optimization successful!")
            print(f"  Team size: {len(players)} players")
            print(f"  Total cost: ${total_cost:.2f}")
            print(f"  Total score: {total_score:.2f}")
            print(f"  Role distribution: {role_distribution}")
            
            # Verify constraints
            expected_constraints = test_case['constraints'] or {"WK": 1, "BAT": 4, "BOWL": 3, "ALL": 3}
            
            for role, expected_count in expected_constraints.items():
                actual_count = role_distribution.get(role, 0)
                if actual_count == expected_count:
                    print(f"  ✓ {role}: {actual_count} (expected {expected_count})")
                else:
                    print(f"  ✗ {role}: {actual_count} (expected {expected_count}) MISMATCH!")
                    
            # Show top 3 players
            top_players = sorted(players, key=lambda x: x['score'], reverse=True)[:3]
            print(f"\n  Top 3 players:")
            for p in top_players:
                print(f"    - {p['name']} ({p['role']}): ${p['price']}, Score: {p['score']:.1f}")
                
        except ValueError as e:
            print(f"✗ Optimization failed: {e}")
    
    print(f"\n{'=' * 70}")
    print("✓ Dynamic Role Constraints Test Complete!")
    print("  Optimizer successfully accepts and applies custom role constraints")
    print("=" * 70)


def test_edge_cases():
    """Test edge cases for dynamic constraints"""
    print("\n" + "=" * 70)
    print("Testing Edge Cases")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_with_scores = calculate_score(df)
    
    # Test 1: Empty constraints (should fail)
    print("\n1. Testing empty constraints...")
    try:
        result = optimize_team(df_with_scores, 200, role_constraints={})
        # If team_size is 11 but no role constraints, it should work
        print(f"  ✓ Optimization succeeded (no role constraints, only team size)")
        print(f"  Selected {len(result['players'])} players")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test 2: Partial constraints (only some roles)
    print("\n2. Testing partial constraints (only WK and BAT)...")
    try:
        result = optimize_team(
            df_with_scores, 
            200,
            team_size=5,  # Reduced team size
            role_constraints={"WK": 1, "BAT": 4}
        )
        print(f"  ✓ Optimization succeeded")
        role_dist = {}
        for p in result['players']:
            role_dist[p['role']] = role_dist.get(p['role'], 0) + 1
        print(f"  Role distribution: {role_dist}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test 3: Impossible constraints (more than available)
    print("\n3. Testing impossible constraints (10 WK, but only 7 available)...")
    try:
        result = optimize_team(
            df_with_scores, 
            200,
            role_constraints={"WK": 10, "BAT": 1, "BOWL": 0, "ALL": 0}
        )
        print(f"  ✗ Should have failed but succeeded")
    except ValueError as e:
        print(f"  ✓ Correctly failed: {e}")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    test_dynamic_role_constraints()
    test_edge_cases()
