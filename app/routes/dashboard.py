# app/routes/dashboard.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services import data_service

router = APIRouter()

# Configure the templates directory (base folder is app/templates)
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        # Asynchronously fetch all required data from the backend API
        data = await data_service.fetch_all_data()
        aggregates = data_service.process_data(data)
    except Exception as e:
        # You may add logging here as needed
        raise HTTPException(status_code=500, detail="Error processing data")
    
    # Render the index page (located in templates/pages) that extends base.html
    return templates.TemplateResponse("pages/index.html", {"request": request, "aggregates": aggregates})
