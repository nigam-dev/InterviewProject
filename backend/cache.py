import pandas as pd
from typing import Dict, Any, Optional

class OptimizationCache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def _generate_dataset_hash(self, df: pd.DataFrame) -> str:
        """Generate a stable hash for the player dataset."""
        # Using hash_pandas_object for efficient hashing of DataFrame content
        # sum() combines the series of hashes into a single value
        return str(pd.util.hash_pandas_object(df).sum())

    def get_cache_key(self, budget: int, team_size: int, df: pd.DataFrame) -> str:
        """Generate a unique cache key based on inputs."""
        dataset_hash = self._generate_dataset_hash(df)
        # Create a unique string key combining budget, team size and dataset hash
        return f"opt:{budget}:{team_size}:{dataset_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Store a value in the cache."""
        self._cache[key] = value

    def clear(self) -> None:
        """Clear the entire cache."""
        self._cache.clear()

# Global cache instance
optimization_cache = OptimizationCache()
