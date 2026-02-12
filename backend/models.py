from pydantic import BaseModel, Field
from typing import List, Optional


class Player(BaseModel):
    """Cricket player data model."""
    name: str
    runs: float
    wickets: float
    strike_rate: float
    price: float


class OptimizationConstraints(BaseModel):
    """Optimization constraints model."""
    budget: float = Field(default=100, gt=0)
    team_size: int = Field(default=11, ge=1, le=11)


class OptimizationRequest(BaseModel):
    """Request model for team optimization."""
    constraints: OptimizationConstraints
    excluded_players: Optional[List[str]] = None
    required_players: Optional[List[str]] = None


class OptimizedTeam(BaseModel):
    """Response model for optimized team."""
    players: List[Player]
    total_price: float
    total_runs: float
    total_wickets: float
    avg_strike_rate: float
    success: bool
    message: str
