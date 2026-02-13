from fastapi import APIRouter, HTTPException, Depends
from typing import List
import pandas as pd

from models.schemas import BudgetRequest, PlayerResponse, OptimizeResponse, OptimizationStrategy
from repositories.player_repository import get_data_source
from services.optimizer import optimize_team
from services.validator import validate_optimization_inputs, ValidationError
from services.player_service import get_scored_players
from repositories.cache import optimization_cache
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/")
async def root():
    """
    API root endpoint with health check.
    """
    # Simply check data source availability
    try:
        data_source = get_data_source()
        status = "online"
    except Exception:
        data_source = "unknown"
        status = "offline"
        
    return {
        "message": "Cricket Team Optimizer API",
        "version": "1.0.0", 
        "data_source": data_source,
        "status": status,
        "endpoints": ["/players", "/optimize"]
    }

@router.get("/players", response_model=List[PlayerResponse])
async def get_all_players():
    """
    Get all players with calculated scores.
    """
    try:
        # Get data from service (handles caching and scoring)
        df_scored = get_scored_players()
        
        # Convert to response models
        players = df_scored.to_dict('records')
        
        return players
        
    except Exception as e:
        logger.error(f"Error serving players: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading players: {str(e)}"
        )

@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_team_endpoint(request: BudgetRequest):
    """
    Optimize team selection based on budget and strategy.
    """
    logger.info(f"Optimization request: budget={request.budget}, team_size={request.team_size}, strategy={request.strategy}")
    
    try:
        # Get data
        df_scored = get_scored_players()
        
        # Check cache
        cache_key = optimization_cache.get_cache_key(
            budget=request.budget,
            team_size=request.team_size,
            strategy=request.strategy.value,
            df=df_scored
        )
        
        cached_result = optimization_cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached optimization result")
            return cached_result
            
        # Validate inputs
        validate_optimization_inputs(
            budget=request.budget,
            df=df_scored
        )
        
        # Run optimization
        result = optimize_team(
            df_scored,
            budget=request.budget,
            team_size=request.team_size,
            strategy=request.strategy
        )
        
        # Format response
        response = OptimizeResponse(
            players=result["players"],
            total_cost=result["total_cost"],
            total_score=result["total_score"]
        )
        
        # Save to cache
        optimization_cache.set(cache_key, response)
        
        return response
        
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.warning(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during optimization: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during optimization")
