from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
from models import Player, OptimizationRequest, OptimizedTeam
from data_loader import load_players
from optimizer import TeamOptimizer

# Initialize FastAPI app
app = FastAPI(
    title="Cricket Team Optimizer API",
    description="API for optimizing cricket team selection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
optimizer = TeamOptimizer()

# Global variable to store loaded data
_players_df: pd.DataFrame | None = None


def get_players_df() -> pd.DataFrame:
    """Get cached players dataframe."""
    global _players_df
    if _players_df is None:
        _players_df = load_players()
    return _players_df


def df_to_players(df: pd.DataFrame) -> List[Player]:
    """Convert DataFrame to list of Player models."""
    players = []
    for _, row in df.iterrows():
        player = Player(
            name=str(row["name"]),
            runs=float(row["runs"]),
            wickets=float(row["wickets"]),
            strike_rate=float(row["strike_rate"]),
            price=float(row["price"])
        )
        players.append(player)
    return players


@app.on_event("startup")
async def startup_event():
    """Load player data on startup."""
    try:
        get_players_df()
        print("Player data loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load player data: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Cricket Team Optimizer API",
        "version": "1.0.0",
        "endpoints": {
            "players": "/players",
            "optimize": "/optimize"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/players", response_model=List[Player])
async def get_all_players():
    """
    Get all players.
    
    Returns:
        List of players
    """
    try:
        df = get_players_df()
        players = df_to_players(df)
        return players
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading players: {str(e)}")


@app.get("/players/{player_name}", response_model=Player)
async def get_player(player_name: str):
    """
    Get a specific player by name.
    
    Args:
        player_name: Player name
    
    Returns:
        Player object
    """
    try:
        df = get_players_df()
        player_row = df[df["name"] == player_name]
        
        if player_row.empty:
            raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
        
        row = player_row.iloc[0]
        player = Player(
            name=str(row["name"]),
            runs=float(row["runs"]),
            wickets=float(row["wickets"]),
            strike_rate=float(row["strike_rate"]),
            price=float(row["price"])
        )
        return player
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving player: {str(e)}")


@app.post("/optimize", response_model=OptimizedTeam)
async def optimize_team(request: OptimizationRequest):
    """
    Optimize team selection based on constraints.
    
    Args:
        request: Optimization request with constraints and player preferences
    
    Returns:
        Optimized team with selected players and totals
    """
    try:
        # Get all available players
        df = get_players_df()
        available_players = df_to_players(df)
        
        if not available_players:
            raise HTTPException(status_code=500, detail="No player data available")
        
        # Convert lists to sets
        excluded_names = set(request.excluded_players) if request.excluded_players else set()
        required_names = set(request.required_players) if request.required_players else set()
        
        # Run optimization
        result = optimizer.optimize(
            available_players=available_players,
            constraints=request.constraints,
            excluded_player_names=excluded_names,
            required_player_names=required_names
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
