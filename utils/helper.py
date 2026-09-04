from playwright.sync_api import Page, Locator
from pathlib import Path
import uuid

user_actions = ["click", "fill", "check", "hover"]


def render_actions(page: Page, user_action):
    action = user_action["action"]
    role = user_action["role"]
    name = user_action["name"]
    secondary_action = user_action["secondary_action"]
    input = user_action["input"]

    screenshot_id = str(uuid.uuid1())
    path = Path(f"outputs/screenshots/screenshot_{screenshot_id}.png")

    match action:
        case "get_by_role":
            current_action = page.get_by_role(role=role, name=name)
            render_secondary_actions(current_action, secondary_action, input)
            print(current_action)
        case "locator":
            current_action = page.locator(name=name)
            render_secondary_actions(current_action, secondary_action, input)
            print(current_action)
        case "screenshot":
            current_action = page.screenshot(path=path)
            print(current_action)
        case "new_page":
            current_action = page.new_page()


def render_secondary_actions(locator: Locator, secondary_action, input_data):
    match secondary_action:
        case "click":
            return locator.click()
        case "fill":
            return locator.fill(input_data)
        case "check":
            return locator.check()
        case "hover":
            return locator.hover()
