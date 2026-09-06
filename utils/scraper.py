from playwright.async_api import async_playwright
from .helper import render_actions
from time import time
from api.supabase_client import update_action

user_actions = ["click", "fill", "check", "hover"]

scraper_actions = [
    {
        "action": "get_by_role",
        "role": "",
        "name": "",
        "secondary_action": "",
        "input": "",
    },
    {
        "action": "locator",
        "role": "",
        "name": "",
        "secondary_action": "",
        "input": "",
    },
    {
        "action": "screenshot",
        "role": "",
        "name": "",
        "secondary_action": "",
        "input": "",
    },
    {
        "action": "new_page",
        "role": "",
        "name": "",
        "secondary_action": "",
        "input": "",
    },
]


async def run_actions(url, actions, automation_id):
    async with async_playwright() as p:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        browser = await p.chromium.launch(channel="chrome")
        page = await browser.new_page()
        await page.goto(url)

        results = []

        for action in actions:
            result = await render_actions(
                page=page, user_action=action.model_dump(), automation_id=automation_id
            )
            results.append(result)
            update_action(automation_id=automation_id, action_id=action.id, logs=result)
            print(action.id)
        await browser.close()

        return results
