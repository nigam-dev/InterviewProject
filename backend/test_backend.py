"""Test script to verify backend functionality."""
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import DataLoader
from optimizer import TeamOptimizer
from models import OptimizationConstraints


def test_data_loader():
    """Test data loading functionality."""
    print("Testing DataLoader...")
    loader = DataLoader()
    
    # Test loading data
    data = loader.load_data()
    print(f"✓ Loaded {len(data)} players from CSV")
    
    # Test getting all players
    players = loader.get_all_players()
    print(f"✓ Retrieved {len(players)} player objects")
    
    # Test getting specific player
    player = loader.get_player_by_id(1)
    if player:
        print(f"✓ Retrieved player: {player.name} ({player.position})")
    
    # Test filtering
    qbs = loader.filter_players(position="QB")
    print(f"✓ Found {len(qbs)} quarterbacks")
    
    return players


def test_optimizer(players):
    """Test optimization functionality."""
    print("\nTesting TeamOptimizer...")
    optimizer = TeamOptimizer()
    
    # Test basic optimization
    constraints = OptimizationConstraints(
        salary_cap=50000,
        min_players=5,
        max_players=9
    )
    
    result = optimizer.optimize(
        available_players=players,
        constraints=constraints
    )
    
    if result.success:
        print(f"✓ Optimization successful!")
        print(f"  - Selected {len(result.players)} players")
        print(f"  - Total salary: ${result.total_salary:,.2f}")
        print(f"  - Total points: {result.total_projected_points:.2f}")
        print(f"  - Players: {', '.join([p.name for p in result.players])}")
    else:
        print(f"✗ Optimization failed: {result.message}")
        return False
    
    # Test with position constraints
    print("\nTesting with position constraints...")
    constraints_with_positions = OptimizationConstraints(
        salary_cap=50000,
        min_players=8,
        max_players=8,
        positions={"QB": 1, "RB": 2, "WR": 3, "TE": 2}
    )
    
    result2 = optimizer.optimize(
        available_players=players,
        constraints=constraints_with_positions
    )
    
    if result2.success:
        print(f"✓ Position-constrained optimization successful!")
        print(f"  - Selected {len(result2.players)} players")
        print(f"  - Total salary: ${result2.total_salary:,.2f}")
        print(f"  - Total points: {result2.total_projected_points:.2f}")
        
        # Show position breakdown
        positions = {}
        for p in result2.players:
            positions[p.position] = positions.get(p.position, 0) + 1
        print(f"  - Position breakdown: {positions}")
    else:
        print(f"✗ Position optimization failed: {result2.message}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("BACKEND FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        # Test data loading
        players = test_data_loader()
        
        # Test optimizer
        test_optimizer(players)
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - Backend is working correctly!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
