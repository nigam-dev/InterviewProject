from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
from models import BudgetRequest, PlayerResponse, OptimizeResponse
from data_loader import load_players
from scoring import calculate_score
from optimizer import optimize_team

# Initialize FastAPI app
app = FastAPI(
    title="Cricket Team Optimizer API",
    description="API for optimizing cricket team selection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
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


@app.get("/players", response_model=List[PlayerResponse])
async def get_all_players():
    """
    Get all players with calculated scores.
    
    Returns:
        List of all players with scores
    """
    try:
        # Get cached data
        df_scored = get_players_data()
        
        # Convert to response models (fast: to_dict('records') vs iterrows)
        players = [
            PlayerResponse(**record)
            for record in df_scored.to_dict('records')
        ]
        
        return players
        
    except Exception as e:
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
    try:
        # Get cached data
        df_scored = get_players_data()
        
        # Optimize team
        result = optimize_team(
            df_scored,
            budget=request.budget,
            team_size=request.team_size
        )
        
        # Convert to response format (fast: dict unpacking)
        selected_players = [
            PlayerResponse(**p)
            for p in result["players"]
        ]
        
        return OptimizeResponse(
            players=selected_players,
            total_cost=result["total_cost"],
            total_score=result["total_score"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
