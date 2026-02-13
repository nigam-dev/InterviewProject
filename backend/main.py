from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import pandas as pd
from models import BudgetRequest, PlayerResponse, OptimizeResponse
from player_repository import load_players, get_data_source
from database import init_database, close_database
from scoring import calculate_score
from optimizer import optimize_team
from validator import validate_optimization_inputs, ValidationError
from cache import optimization_cache
from logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database connection
    logger.info("Initializing database connection...")
    db_available = init_database()
    if db_available:
        logger.info("✓ Database initialized successfully")
    else:
        logger.warning("⚠ Database unavailable, using CSV fallback")
    
    yield
    
    # Shutdown: Close database connections
    logger.info("Closing database connections...")
    close_database()


# Initialize FastAPI app
app = FastAPI(
    title="Cricket Team Optimizer API",
    description="API for optimizing cricket team selection",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite dev server fallback
        "http://localhost:3000",  # Alternative dev port
        "http://localhost",       # Docker frontend
        "http://localhost:80",    # Docker frontend explicit
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# Cache: Load and score players once at startup
_cached_players_df: pd.DataFrame = None



def get_players_data() -> pd.DataFrame:
    """Get cached player data, loading if necessary."""
    global _cached_players_df
    if _cached_players_df is None:
        df = load_players()
        _cached_players_df = calculate_score(df)
    return _cached_players_df


@app.get("/")
async def root():
    """
    API root endpoint with health check.
    
    Returns:
        API info and data source status
    """
    data_source = get_data_source()
    return {
        "message": "Cricket Team Optimizer API",
        "version": "1.0.0",
        "data_source": data_source,
        "endpoints": ["/players", "/optimize"]
    }


@app.get("/players", response_model=List[PlayerResponse])
async def get_all_players():
    """
    Get all players with calculated scores.
    
    Returns:
        List of all players with scores
    """
    logger.info("Fetching all players")
    try:
        # Get cached data
        df_scored = get_players_data()
        
        # Convert to response models (fast: to_dict('records') vs iterrows)
        players = [
            PlayerResponse(**record)
            for record in df_scored.to_dict('records')
        ]
        
        logger.info(f"Successfully retrieved {len(players)} players")
        return players
        
    except Exception as e:
        logger.error(f"Error loading players: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading players: {str(e)}"
        )


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_team_endpoint(request: BudgetRequest):
    """
    Optimize team selection based on budget.
    
    Args:
        request: Budget request with budget (and optional team_size)
    
    Returns:
        Optimized team with selected players and totals
    """
    logger.info(f"Optimization request: budget={request.budget}, team_size={request.team_size}")
    try:
        # Get cached data
        df_scored = get_players_data()
        
        # Check cache explicitly
        cache_key = optimization_cache.get_cache_key(
            budget=request.budget,
            team_size=request.team_size,
            strategy=str(request.strategy),
            df=df_scored
        )
        cached_result = optimization_cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached optimization result")
            return cached_result
        
        # Validate inputs before optimization
        validate_optimization_inputs(
            budget=request.budget,
            df=df_scored
        )
        
        # Optimize team
        result = optimize_team(
            df_scored,
            budget=request.budget,
            team_size=request.team_size,
            strategy=request.strategy
        )
        
        # Convert to response format (fast: dict unpacking)
        selected_players = [
            PlayerResponse(**p)
            for p in result["players"]
        ]
        
        response = OptimizeResponse(
            players=selected_players,
            total_cost=result["total_cost"],
            total_score=result["total_score"]
        )
        
        # Store in cache
        optimization_cache.set(cache_key, response)
        
        logger.info(f"Optimization successful: cost={result['total_cost']}, score={result['total_score']}")
        return response
        
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        # Handle validation errors with 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.warning(f"Optimization logic error: {str(e)}")
        # Handle optimization errors with 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected optimization error: {str(e)}", exc_info=True)
        # Handle unexpected errors with 500 Internal Server Error
        raise HTTPException(
            status_code=500,
            detail=f"Optimization error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
