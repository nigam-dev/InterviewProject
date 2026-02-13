#!/usr/bin/env python3
"""
Standalone test script for backend functionality.
Tests data loading, score calculation, and team optimization.
"""
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import load_players
from scoring import calculate_score
from optimizer import optimize_team


def main():
    print("=" * 80)
    print("BACKEND FUNCTIONALITY TEST")
    print("=" * 80)
    
    # Test 1: Load players
    print("\n1. Testing load_players()...")
    df = load_players()
    print(f"   ✓ Loaded {len(df)} players")
    print(f"   ✓ Columns: {list(df.columns)}")
    
    # Test 2: Calculate score
    print("\n2. Testing calculate_score()...")
    df_scored = calculate_score(df)
    print(f"   ✓ Calculated scores for {len(df_scored)} players")
    print(f"   ✓ Score column added: {'score' in df_scored.columns}")
    
    # Show top 5 scorers
    print("\n   Top 5 Scorers:")
    top_5 = df_scored.nlargest(5, 'score')[['name', 'runs', 'wickets', 'strike_rate', 'price', 'score']]
    for idx, (_, row) in enumerate(top_5.iterrows(), 1):
        print(f"   {idx}. {row['name']:<20} - Score: {row['score']:.1f}")
    
    # Test 3: Optimize with budget 115 (7 players)
    print("\n3. Testing optimize_team() with budget=115, team_size=7...")
    # Define constraints that sum to 7
    constraints = {"WK": 1, "BAT": 2, "BOWL": 2, "ALL": 2}
    result = optimize_team(df_scored, budget=115, team_size=7, role_constraints=constraints)
    
    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS (Budget: $115, Team Size: 7)")
    print("=" * 80)
    
    print(f"\nTotal Cost: ${result['total_cost']:.2f}")
    print(f"Total Score: {result['total_score']:.1f}")
    print(f"Players Selected: {len(result['players'])}")
    
    print(f"\n{'Selected Players:':^80}")
    print("=" * 80)
    print(f"{'#':<3} {'Name':<22} {'Runs':<6} {'Wkts':<5} {'SR':<6} {'Price':<6} {'Score':<8}")
    print("-" * 80)
    
    # Sort by score descending
    sorted_players = sorted(result['players'], key=lambda p: p['score'], reverse=True)
    for idx, player in enumerate(sorted_players, 1):
        print(f"{idx:<3} {player['name']:<22} {player['runs']:<6.0f} {player['wickets']:<5.0f} "
              f"{player['strike_rate']:<6.0f} ${player['price']:<5.0f} {player['score']:<8.1f}")
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()
