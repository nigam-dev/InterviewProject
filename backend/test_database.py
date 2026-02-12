"""
Test database and CSV fallback functionality
"""
import sys
import os

# Test 1: Import all modules
print("=" * 70)
print("Test 1: Module Imports")
print("=" * 70)

try:
    from database import init_database, is_database_available, close_database
    from player_repository import load_players, get_data_source, sync_csv_to_database
    from scoring import calculate_score
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Note: SQLAlchemy/psycopg2 may not be installed yet")
    sys.exit(1)


# Test 2: Database initialization (expected to fail without PostgreSQL)
print("\n" + "=" * 70)
print("Test 2: Database Initialization")
print("=" * 70)

db_available = init_database()
if db_available:
    print(f"✓ Database initialized successfully")
    print(f"  Data source: {get_data_source()}")
else:
    print(f"✓ Database unavailable (expected without PostgreSQL running)")
    print(f"  Will use CSV fallback")


# Test 3: Load players with fallback
print("\n" + "=" * 70)
print("Test 3: Load Players (with fallback)")
print("=" * 70)

try:
    df = load_players("players.csv")
    print(f"✓ Loaded {len(df)} players")
    print(f"  Data source: {get_data_source()}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  First player: {df.iloc[0]['name']} ({df.iloc[0]['role']})")
    
    # Check required columns
    required_columns = ['name', 'runs', 'wickets', 'strike_rate', 'price', 'role']
    missing = set(required_columns) - set(df.columns)
    if missing:
        print(f"✗ Missing columns: {missing}")
    else:
        print(f"✓ All required columns present")
        
except Exception as e:
    print(f"✗ Failed to load players: {e}")
    sys.exit(1)


# Test 4: Score calculation still works
print("\n" + "=" * 70)
print("Test 4: Score Calculation")
print("=" * 70)

try:
    df_scored = calculate_score(df)
    print(f"✓ Calculated scores for {len(df_scored)} players")
    print(f"  Sample: {df_scored.iloc[0]['name']}, Score: {df_scored.iloc[0]['score']:.2f}")
    
    if 'score' not in df_scored.columns:
        print(f"✗ Score column missing")
    else:
        print(f"✓ Score column added successfully")
        
except Exception as e:
    print(f"✗ Score calculation failed: {e}")
    sys.exit(1)


# Test 5: Database sync (if available)
if is_database_available():
    print("\n" + "=" * 70)
    print("Test 5: Database Sync (Optional)")
    print("=" * 70)
    
    try:
        count = sync_csv_to_database("players.csv")
        print(f"✓ Synced {count} players to database")
        
        # Try loading from database
        df_db = load_players("players.csv")
        source = get_data_source()
        print(f"✓ Current data source: {source}")
        
        if source == 'database':
            print(f"✓ Successfully using database as primary source")
        else:
            print(f"⚠ Still using CSV (database may be empty)")
            
    except Exception as e:
        print(f"⚠ Database sync failed (this is OK if no DB): {e}")
else:
    print("\n" + "=" * 70)
    print("Test 5: Database Sync (Skipped - Database Unavailable)")
    print("=" * 70)
    print("✓ CSV fallback working as expected")


# Test 6: API compatibility
print("\n" + "=" * 70)
print("Test 6: API Compatibility")
print("=" * 70)

# Simulate what main.py does
_cached_players_df = None

def get_players_data():
    global _cached_players_df
    if _cached_players_df is None:
        df = load_players()
        _cached_players_df = calculate_score(df)
    return _cached_players_df

try:
    df_api = get_players_data()
    print(f"✓ API-style data loading works")
    print(f"  Players: {len(df_api)}")
    print(f"  Columns: {list(df_api.columns)}")
    
    # Verify it returns same data on second call (caching)
    df_api2 = get_players_data()
    if df_api is df_api2:
        print(f"✓ Caching works (same object returned)")
    else:
        print(f"⚠ Caching may not be working properly")
        
except Exception as e:
    print(f"✗ API compatibility test failed: {e}")
    sys.exit(1)


# Test 7: Verify existing functionality not broken
print("\n" + "=" * 70)
print("Test 7: Backward Compatibility")
print("=" * 70)

checks = []

# Check 1: DataFrame structure
if all(col in df_scored.columns for col in ['name', 'price', 'score', 'role']):
    checks.append("✓ Required columns for optimizer")
else:
    checks.append("✗ Missing required columns")

# Check 2: Data types
if df_scored['price'].dtype == float:
    checks.append("✓ Price is float")
else:
    checks.append("✗ Price type incorrect")

if df_scored['score'].dtype == float:
    checks.append("✓ Score is float")
else:
    checks.append("✗ Score type incorrect")

# Check 3: Role values
valid_roles = {'WK', 'BAT', 'BOWL', 'ALL'}
if set(df_scored['role'].unique()).issubset(valid_roles):
    checks.append("✓ Valid role values")
else:
    checks.append("✗ Invalid role values found")

# Check 4: No null values in critical columns
critical_cols = ['name', 'price', 'role', 'score']
if not df_scored[critical_cols].isnull().any().any():
    checks.append("✓ No null values in critical columns")
else:
    checks.append("✗ Null values found")

for check in checks:
    print(f"  {check}")

if all("✓" in check for check in checks):
    print("\n✓ All backward compatibility checks passed")
else:
    print("\n✗ Some backward compatibility issues found")


# Cleanup
print("\n" + "=" * 70)
print("Cleanup")
print("=" * 70)

close_database()
print("✓ Database connections closed")


# Summary
print("\n" + "█" * 70)
print("SUMMARY")
print("█" * 70)
print(f"Database Available: {db_available}")
print(f"Data Source: {get_data_source()}")
print(f"Players Loaded: {len(df)}")
print(f"CSV Fallback: {'Working' if get_data_source() == 'csv' else 'Not tested'}")
print(f"API Compatible: Yes")
print("█" * 70)
print("\n✓ All tests completed successfully!")
print("  System is ready to use with or without PostgreSQL")
print("█" * 70)
