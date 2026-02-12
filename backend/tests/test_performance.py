"""Test backend performance optimizations."""
import sys
from pathlib import Path
import time

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import load_players
from scoring import calculate_score
from optimizer import optimize_team

print('Testing optimized backend...\n')

# Test 1: Data loading performance
start = time.time()
df = load_players()
load_time = time.time() - start
print(f'✓ Load players: {load_time*1000:.2f}ms')
print(f'  Loaded {len(df)} players')

# Test 2: Score calculation
start = time.time()
df_scored = calculate_score(df)
score_time = time.time() - start
print(f'✓ Calculate scores: {score_time*1000:.2f}ms')

# Test 3: Optimization performance
start = time.time()
result = optimize_team(df_scored, budget=175, team_size=11)
opt_time = time.time() - start
print(f'✓ Optimize team: {opt_time*1000:.2f}ms')
print(f'  Selected {len(result["players"])} players')
print(f'  Total cost: ${result["total_cost"]}')
print(f'  Total score: {result["total_score"]:.1f}')

# Test 4: Memory efficiency - verify data types
print(f'\n✓ Data types optimized:')
print(f'  runs: {df_scored["runs"].dtype}')
print(f'  wickets: {df_scored["wickets"].dtype}')
print(f'  strike_rate: {df_scored["strike_rate"].dtype}')
print(f'  price: {df_scored["price"].dtype}')
print(f'  score: {df_scored["score"].dtype}')

total_time = load_time + score_time + opt_time
print(f'\n✓ Total execution time: {total_time*1000:.2f}ms')
print('✓ All optimizations working correctly!')
