from pydantic import BaseModel, Field
from typing import List, Optional


class Player(BaseModel):
    """Player data model."""
    id: int
    name: str
    position: str
    salary: float
    projected_points: float
    team: str


class OptimizationConstraints(BaseModel):
    """Optimization constraints model."""
    salary_cap: float = Field(default=50000, gt=0)
    min_players: int = Field(default=5, ge=1)
    max_players: int = Field(default=11, ge=1)
    positions: Optional[dict[str, int]] = None  # e.g., {"QB": 1, "RB": 2}


class OptimizationRequest(BaseModel):
    """Request model for team optimization."""
    constraints: OptimizationConstraints
    excluded_players: Optional[List[int]] = None
    required_players: Optional[List[int]] = None


class OptimizedTeam(BaseModel):
    """Response model for optimized team."""
    players: List[Player]
    total_salary: float
    total_projected_points: float
    success: bool
    message: str
