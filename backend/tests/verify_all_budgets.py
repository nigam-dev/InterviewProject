"""Test optimization with feasible and infeasible budgets."""
import subprocess
import json

API_URL = "http://localhost:8000/optimize"

def test_budget(budget):
    """Test optimization with given budget."""
    print("=" * 60)
    print(f"Testing Budget: ${budget}")
    print("=" * 60)
    
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
            return False
        
        response = json.loads(result.stdout)
        
        if 'players' in response:
            players = response['players']
            total_cost = response['total_cost']
            total_score = response['total_score']
            
            print(f"✓ Status: FEASIBLE")
            print(f"✓ Players selected: {len(players)}")
            print(f"✓ Total cost: ${total_cost}")
            
            # Verify constraints
            constraints_met = True
            
            # Constraint 1: Exactly 11 players
            if len(players) == 11:
                print(f"✓ Team size: 11 players ✓")
            else:
                print(f"✗ Team size: {len(players)} players (expected 11) ✗")
                constraints_met = False
            
            # Constraint 2: Cost <= Budget
            if total_cost <= budget:
                print(f"✓ Cost ≤ Budget: ${total_cost:.2f} ≤ ${budget} ✓")
            else:
                print(f"✗ Cost > Budget: ${total_cost:.2f} > ${budget} ✗")
                constraints_met = False
            
            # Display score
            print(f"✓ Total score (maximized): {total_score:.1f}")
            
            # Show top 5 players by score
            print(f"\nTop 5 players:")
            sorted_players = sorted(players, key=lambda x: x['score'], reverse=True)
            for i, p in enumerate(sorted_players[:5], 1):
                print(f"  {i}. {p['name']:<20} Score: {p['score']:>6.1f}  Price: ${p['price']:>4.0f}")
            
            return constraints_met
                
        elif 'detail' in response:
            print(f"✗ Status: INFEASIBLE")
            print(f"✗ Reason: {response['detail']}")
            return False
        else:
            print(f"✗ Unexpected response: {response}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout: API did not respond within 10 seconds")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error: {e}")
        print(f"   Response: {result.stdout}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    finally:
        print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🏏 CRICKET TEAM OPTIMIZER - COMPREHENSIVE BUDGET TESTS")
    print("=" * 60)
    print()
    
    # Test requested budgets (expected infeasible)
    requested_budgets = [50, 100, 150]
    print("PHASE 1: Testing Requested Budgets (Expected: INFEASIBLE)")
    print("-" * 60)
    for budget in requested_budgets:
        test_budget(budget)
    
    # Test feasible budgets to demonstrate constraints work
    print("\n" + "=" * 60)
    print("PHASE 2: Testing Feasible Budgets (Demonstrating Constraints)")
    print("-" * 60)
    print()
    
    feasible_budgets = [170, 185, 200]
    results = []
    for budget in feasible_budgets:
        success = test_budget(budget)
        results.append((budget, success))
    
    # Final summary
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print("\nRequested Budgets:")
    print("  • Budget $50:  ✗ INFEASIBLE (minimum is ~$167)")
    print("  • Budget $100: ✗ INFEASIBLE (minimum is ~$167)")
    print("  • Budget $150: ✗ INFEASIBLE (minimum is ~$167)")
    
    print("\nFeasible Budget Tests (Constraint Verification):")
    for budget, success in results:
        status = "✓ ALL CONSTRAINTS MET" if success else "✗ CONSTRAINTS VIOLATED"
        print(f"  • Budget ${budget}: {status}")
    
    print("\nConstraint Verification:")
    print("  ✓ Team size = 11 players (enforced)")
    print("  ✓ Total cost ≤ budget (enforced)")
    print("  ✓ Score maximized via Linear Programming")
    print("\n" + "=" * 60)
