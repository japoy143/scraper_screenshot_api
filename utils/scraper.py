from playwright.sync_api import sync_playwright
from .helper import render_actions

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


def run_actions(url, actions):
    with sync_playwright() as p:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page()
        page.goto(url)

        results = []

        for action in actions:
            result = render_actions(page=page, user_action=action)
            results.append(result)

        browser.close()

        return results
