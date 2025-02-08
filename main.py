# app/main.py
from fastapi import FastAPI
from app.routes import router
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import dotenv

# Load .env only for local development
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development":
    dotenv.load_dotenv()

app = FastAPI(
    title="DataHub Analysis Dashboard",
    # docs_url="/docs",
    # redoc_url="/redoc"
)

# Mount the static files directory so they are accessible at /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include the dashboard routes (more routers can be added as your app scales)
app.include_router(router)

if __name__ == "__main__":
   # Set host and port based on environment
    host = "0.0.0.0" if ENVIRONMENT == "production" else "127.0.0.1"
    port = int(os.environ.get("PORT", 8001))  # Use Heroku's $PORT or default for local

    uvicorn.run("main:app", reload=(ENVIRONMENT == "development"), host=host, port=port)
