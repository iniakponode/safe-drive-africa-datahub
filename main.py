# app/main.py
import asyncio
import os
try:
    import dotenv
except ImportError:  # pragma: no cover - optional dependency
    dotenv = None
from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.routers.ubpk_metrics import router as ubpk_router
from app.routers.analysis_pages import router as analysis_router
from app.cache import refresh_cache_periodically

# Load environment variables (for local development)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development" and dotenv:
    dotenv.load_dotenv()

app = FastAPI(
    title="DataHub Analysis Dashboard"
)

# Mount static files (if any)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include all routes
app.include_router(router)
app.include_router(ubpk_router, prefix="/metrics/behavior", tags=["UBPK"])
app.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])

@app.on_event("startup")
async def startup_event():
    # Start background cache refresh task.
    asyncio.create_task(refresh_cache_periodically())

if __name__ == "__main__":
    # Set host and port based on environment.
    host = "0.0.0.0" if ENVIRONMENT == "production" else "127.0.0.1"
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", reload=(ENVIRONMENT == "development"), host=host, port=port)
