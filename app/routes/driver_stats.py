from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.data_service import fetch_all_data, process_driver_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/drivers", response_class=HTMLResponse)
async def driver_stats(request: Request):
    data = await fetch_all_data()
    stats = process_driver_data(data)
    return templates.TemplateResponse("pages/driver_stats.html", {"request": request, "stats": stats})
