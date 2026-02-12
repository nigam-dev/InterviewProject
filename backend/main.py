from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import Player, OptimizationRequest, OptimizedTeam
from data_loader import DataLoader
from optimizer import TeamOptimizer

# Initialize FastAPI app
app = FastAPI(
    title="Sports Team Optimizer API",
    description="API for optimizing sports team selection",
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
data_loader = DataLoader()
optimizer = TeamOptimizer()


@app.on_event("startup")
async def startup_event():
    """Load player data on startup."""
    try:
        data_loader.load_data()
        print("Player data loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load player data: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Sports Team Optimizer API",
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
async def get_players(position: str | None = None, max_salary: float | None = None):
    """
    Get all players or filter by position and/or max salary.
    
    Args:
        position: Filter by position (optional)
        max_salary: Filter by maximum salary (optional)
    
    Returns:
        List of players
    """
    try:
        if position or max_salary:
            players = data_loader.filter_players(position=position, max_salary=max_salary)
        else:
            players = data_loader.get_all_players()
        
        return players
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading players: {str(e)}")


@app.get("/players/{player_id}", response_model=Player)
async def get_player(player_id: int):
    """
    Get a specific player by ID.
    
    Args:
        player_id: Player ID
    
    Returns:
        Player object
    """
    try:
        player = data_loader.get_player_by_id(player_id)
        
        if player is None:
            raise HTTPException(status_code=404, detail=f"Player with ID {player_id} not found")
        
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
        available_players = data_loader.get_all_players()
        
        if not available_players:
            raise HTTPException(status_code=500, detail="No player data available")
        
        # Convert lists to sets
        excluded_ids = set(request.excluded_players) if request.excluded_players else set()
        required_ids = set(request.required_players) if request.required_players else set()
        
        # Run optimization
        result = optimizer.optimize(
            available_players=available_players,
            constraints=request.constraints,
            excluded_player_ids=excluded_ids,
            required_player_ids=required_ids
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
