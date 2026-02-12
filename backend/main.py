from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/players", response_model=List[PlayerResponse])
async def get_all_players():
    """
    Get all players with calculated scores.
    
    Returns:
        List of all players with scores
    """
    try:
        # Load data
        df = load_players()
        
        # Calculate scores
        df_scored = calculate_score(df)
        
        # Convert to response models
        players = [
            PlayerResponse(
                name=str(row["name"]),
                runs=int(row["runs"]),
                wickets=int(row["wickets"]),
                strike_rate=float(row["strike_rate"]),
                price=float(row["price"]),
                score=float(row["score"])
            )
            for _, row in df_scored.iterrows()
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
        # Load data
        df = load_players()
        
        # Calculate score
        df_scored = calculate_score(df)
        
        # Optimize team
        result = optimize_team(
            df_scored,
            budget=request.budget,
            team_size=request.team_size
        )
        
        # Convert to response format
        selected_players = [
            PlayerResponse(
                name=p["name"],
                runs=int(p["runs"]),
                wickets=int(p["wickets"]),
                strike_rate=float(p["strike_rate"]),
                price=float(p["price"]),
                score=float(p["score"])
            )
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
