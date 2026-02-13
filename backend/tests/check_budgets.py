"""Test optimization with different budgets."""
import subprocess
import json

API_URL = "http://localhost:8000/optimize"

def test_budget(budget):
    """Test optimization with given budget."""
    print("=" * 50)
    print(f"Testing Budget: ${budget}")
    print("=" * 50)
    
    try:
        # Use curl to call the API
        result = subprocess.run(
            [
                'curl', '-s', '-X', 'POST', API_URL,
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({"budget": budget})
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"✗ curl error: {result.stderr}")
            return
        
        response = json.loads(result.stdout)
        
        if 'players' in response:
            players = response['players']
            total_cost = response['total_cost']
            total_score = response['total_score']
            
            print(f"✓ Status: FEASIBLE")
            print(f"✓ Players selected: {len(players)}")
            print(f"✓ Total cost: ${total_cost}")
            print(f"✓ Cost ≤ Budget: {total_cost <= budget} (${total_cost} ≤ ${budget})")
            print(f"✓ Total score: {total_score:.1f}")
            
            # Verify exactly 11 players
            if len(players) == 11:
                print(f"✓ Team size: 11 players ✓")
            else:
                print(f"✗ Team size: {len(players)} players (expected 11)")
            
            # Show top 3 players by score
            print(f"\nTop 3 players:")
            sorted_players = sorted(players, key=lambda x: x['score'], reverse=True)
            for i, p in enumerate(sorted_players[:3], 1):
                print(f"  {i}. {p['name']}: {p['score']:.1f} (${p['price']:.0f})")
                
        elif 'detail' in response:
            print(f"✗ Status: INFEASIBLE")
            print(f"✗ Reason: {response['detail']}")
        else:
            print(f"✗ Unexpected response: {response}")
            
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout: API did not respond within 10 seconds")
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error: {e}")
        print(f"   Response: {result.stdout}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

if __name__ == "__main__":
    # Test the requested budgets
    budgets = [50, 100, 150]
    
    print("\n🏏 CRICKET TEAM OPTIMIZER - BUDGET TESTS\n")
    
    for budget in budgets:
        test_budget(budget)
    
    print("=" * 50)
    print("Test Summary:")
    print("=" * 50)
    print("• Budget 50:  Expected INFEASIBLE (min is ~$153)")
    print("• Budget 100: Expected INFEASIBLE (min is ~$153)")
    print("• Budget 150: Expected INFEASIBLE (min is ~$153)")
    print("\nNote: Minimum budget for 11 players is $153")
    print("      (11 cheapest players cost: $12+13+13+14×5+15×3)")
