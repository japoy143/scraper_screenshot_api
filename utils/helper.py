import re
from pathlib import Path
import uuid
from playwright.async_api import Page, Locator
from events.manager import publish

user_actions = ["click", "fill", "check", "hover"]


async def render_secondary_actions(locator: Locator, secondary_action: str, input_data):
    match secondary_action:
        case "click":
            return await locator.click()
        case "fill":
            return await locator.fill(input_data)
        case "check":
            return await locator.check()
        case "hover":
            return await locator.hover()
        case None:
            return None
        case _:
            raise ValueError(f"Unknown secondary_action: {secondary_action}")


async def render_actions(page: Page, user_action: dict, automation_id: str):
    action_id = user_action["id"]
    action = user_action["action"]
    role = user_action.get("role")
    name = user_action.get("name")
    secondary_action = user_action.get("secondary_action")
    input_data = user_action.get("input")

    match action:
        case "get_by_role":
            current_action = page.get_by_role(
                role=role, name=re.compile(name, re.IGNORECASE)
            )
            await render_secondary_actions(current_action, secondary_action, input_data)
            await publish(
                subscriber_id=automation_id,
                event={"id": action_id, "logs": str(current_action)},
            )
            print(current_action)
            return str(current_action)

        case "get_by_label":
            current_action = page.get_by_label(name)
            await render_secondary_actions(current_action, secondary_action, input_data)
            await publish(
                subscriber_id=automation_id,
                event={"id": action_id, "logs": str(current_action)},
            )
            print(current_action)
            return str(current_action)

        case "locator":
            current_action = page.locator(name)
            await render_secondary_actions(current_action, secondary_action, input_data)
            await publish(
                subscriber_id=automation_id,
                event={"id": action_id, "logs": str(current_action)},
            )
            print(current_action)
            return str(current_action)

        case "screenshot":
            screenshot_id = str(uuid.uuid4())
            path = Path(f"outputs/screenshots/screenshot_{screenshot_id}.png")
            path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=path)
            print(path)
            return str(path)

        case "new_page":
            new_page = await page.context.new_page()
            return new_page

        case _:
            raise ValueError(f"Unknown action: {action}")
