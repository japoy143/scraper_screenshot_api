from utils.scraper import run_actions
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import (
    Limiter,
    _rate_limit_exceeded_handler,
)  # rate limit ref: https://shiladityamajumder.medium.com/using-slowapi-in-fastapi-mastering-rate-limiting-like-a-pro-19044cb6062b
from slowapi.errors import RateLimitExceeded
from schema.type import (
    ScrapeRequest,
    Automations,
    AutomationTemplate,
    DeleteScreenshotsRequest,
)
from api.supabase_client import (
    add_run_automation,
    delete_execution,
    save_template,
    get_template,
    delete_screenshots,
    get_all_screenshot_expired_and_delete,
)
from events.manager import subscribe, unsubscribe
import asyncio
import json

web_link = "https://rainierlesondatoii.vercel.app/"


# rate limiting
limiter = Limiter(key_func=lambda request: request.client.host)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://scrapeflow-9nm8.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Error Handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/scrape/actions")
@limiter.limit("10/minute")  # means 3 request per minute
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

        result = await run_actions(url, actions, automation_id)
        return {"success": True, "result": result}
    except Exception as exception:
        delete_execution(automation_id=automation_id)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(exception)}
        )


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


# can only save 5 per minute minimizing database usage
# disable this when scaled
@app.post("/templates/save")
@limiter.limit("5/minute")
def template_save(request: Request, payload: AutomationTemplate):

    try:
        user_id = payload.user_id
        automation_name = payload.automation_name
        template_id = payload.template_id
        actions = payload.actions
        res = save_template(
            user_id=user_id,
            automation_name=automation_name,
            template_id=template_id,
            actions=actions,
        )
        print(res)
        return {"success": True, "result": res}
    except Exception as exception:
        print(exception)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(exception)}
        )


@app.get("/templates/{user_id}")
@limiter.limit("10/minute")
def get_user_templates(request: Request, user_id: str):
    try:
        res = get_template(user_id)
        return {"success": True, "result": res}

    except Exception as exception:
        print(exception)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(exception)}
        )


@app.post("/screenshot/remove")
@limiter.limit("3/minute")
def delete_all_screenshots(request: Request, data: DeleteScreenshotsRequest):
    try:
        res = delete_screenshots(data.files)
        print(res)
        return {"success": True, "result": res}
    except Exception as exception:
        print(exception)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(exception)}
        )


@app.post("/screenshot/remove/expired")
@limiter.limit("1/minute")
def delete_expire_screenshots(request: Request):
    try:
        res = get_all_screenshot_expired_and_delete()
        print(res)
        return res
    except Exception as exception:
        print(exception)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(exception)}
        )
