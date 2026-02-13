from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logger import get_logger
from core.database import init_database
from api.routes import router as api_router

logger = get_logger(__name__)

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
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost",
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# Include API routes
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("Starting Cricket Team Optimizer API...")
    if init_database():
        logger.info("✓ Database initialized")
    else:
        logger.warning("⚠ Database unavailable, continuing with CSV fallback")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
