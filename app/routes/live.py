from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio
from app.cache import get_cached_data

router = APIRouter()

@router.get("/live")
async def live_feed():
    async def event_generator():
        while True:
            data = get_cached_data()
            if data is not None:
                yield {"event": "update", "data": data}
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())
