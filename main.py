from utils.scraper import run_actions
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from slowapi import (
    Limiter,
    _rate_limit_exceeded_handler,
)  # rate limit ref: https://shiladityamajumder.medium.com/using-slowapi-in-fastapi-mastering-rate-limiting-like-a-pro-19044cb6062b
from slowapi.errors import RateLimitExceeded
from schema.type import ScrapeRequest, Automations
from api.supabase_client import add_run_automation, delete_execution
from events.manager import subscribe, unsubscribe
import asyncio
import json

web_link = "https://rainierlesondatoii.vercel.app/"


# rate limiting
limiter = Limiter(key_func=lambda request: request.client.host)


app = FastAPI()

# Register Error Handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/scrape/actions")
@limiter.limit("3/minute")  # means 3 request per minute
async def scrape(request: Request, payload: ScrapeRequest):
    # values
    actions = payload.actions
    url = payload.url
    automation_id = payload.automation_id
    count = 0
    # formatted values
    automation = Automations(
        automation_id=automation_id,
        count=count,
        automations=actions,
        url=url,
    )
    # add to db
    add_run_automation(automation=automation)
    try:

        results = await run_actions(url, actions, automation_id)
        return {"results": results}
    except Exception as exception:
        delete_execution(automation_id=automation_id)
        return exception


@app.get("/events/{subscriber_id}")
async def events(request: Request, subscriber_id: str):
    queue = subscribe(subscriber_id)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"  # comment line, keeps connection open
        except asyncio.CancelledError:
            pass
        finally:
            unsubscribe(subscriber_id)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
