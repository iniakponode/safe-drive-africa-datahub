# app/routes/dashboard.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.data_service import fetch_all_data, process_data
from app.services import data_service

router = APIRouter()

# Configure the templates directory (base folder is app/templates)
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # 1) Fetch the nested data
    driver_details_list = await fetch_all_data()
    # 2) Process it to get aggregates
    aggregates = process_data(driver_details_list)
    # 3) Render template
    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "aggregates": aggregates
        }
    )
