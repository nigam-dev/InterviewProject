from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class OptimizationStrategy(str, Enum):
    """Strategy for team optimization."""
    MAX_SCORE = "MAX_SCORE"
    MAX_SCORE_PER_COST = "MAX_SCORE_PER_COST"


class BudgetRequest(BaseModel):
    """Request model for optimization."""
    budget: int = Field(gt=0, description="Total budget available")
    team_size: int = Field(default=11, ge=1, le=11, description="Number of players to select")
    strategy: OptimizationStrategy = Field(
        default=OptimizationStrategy.MAX_SCORE,
        description="Optimization strategy to use"
    )


class PlayerResponse(BaseModel):
    """Response model for player data."""
    name: str
    runs: int
    wickets: int
    strike_rate: float
    price: float
    role: str
    score: float


class OptimizeResponse(BaseModel):
    """Response model for optimized team."""
    players: List[PlayerResponse]
    total_cost: float
    total_score: float
