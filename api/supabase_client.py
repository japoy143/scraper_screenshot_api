import os
from dotenv import load_dotenv
from supabase import create_client, Client
from schema.type import Automations
from pathlib import Path
import mimetypes

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
client: Client = create_client(url, key)

# tables
automations_table = "automations"
templates_table = "templates"
# buckets
screenshot_buckets = "screenshots"


def get_automations():
    try:
        response = client.table(automations_table).select("*").execute()
        print(response)
        return response
    except Exception as exception:
        print(f"Error getting automations")
        return exception


def add_run_automation(automation: Automations):
    try:
        response = (
            client.table(automations_table)
            .insert(
                {
                    "automation_id": automation.automation_id,
                    "automations": [
                        automate.model_dump() for automate in automation.automations
                    ],
                    "count": automation.count,
                    "url": automation.url,
                }
            )
            .execute()
        )
        print(response)
        return response
    except Exception as exception:
        print(f"Error inserting automations")
        return exception


def update_action(automation_id, action_id, logs):
    try:
        response = (
            client.table(automations_table)
            .select("automations")
            .eq("automation_id", automation_id)
            .single()
            .execute()
        )

        actions = response.data["automations"]

        for action in actions:
            if action["id"] == str(action_id):
                action["is_done"] = True
                action["logs"] = logs
                break

        response = (
            client.table(automations_table)
            .update({"automations": actions})
            .eq("automation_id", automation_id)
            .execute()
        )
        print(response)
        return response

    except Exception as exception:
        print(f"Error updating action: {exception}")
        return exception


def delete_execution(automation_id):
    try:
        response = (
            client.table(automations_table)
            .delete()
            .eq("automation_id", automation_id)
            .execute()
        )
        return response
    except Exception as exception:
        print(f"Error deleting action: {exception}")
        return exception


# base url = https://vieqcasgkbxjockpxiti.supabase.co/storage/v1/object/public/screenshots/outputs/
# file storage
def upload_screenshot(file_path):
    path = Path(file_path)
    mime_type, _ = mimetypes.guess_type(path)
    storage_path = f"outputs/{path.name}"

    with open(path, "rb") as f:
        response = client.storage.from_("screenshots").upload(
            file=f,
            path=storage_path,
            file_options={
                "cache-control": "3600",
                "upsert": "false",
                "content-type": mime_type,
            },
        )
        print(response)
        url = client.storage.from_("screenshots").get_public_url(storage_path)
        return url


# save template automation
def save_template(user_id, automation_name, template_id, actions):
    try:
        response = (
            client.table(templates_table)
            .insert(
                {
                    "user_id": user_id,
                    "automation_name": automation_name,
                    "template_id": template_id,
                    "automations": [action.model_dump() for action in actions],
                }
            )
            .execute()
        )
        print(response)
        return response
    except Exception as exception:
        print(f"Error saving automation template")
        return exception


def get_template(id):
    try:
        response = client.table(templates_table).select("*").eq("user_id", id).execute()
        print(response)
        return response
    except Exception as exception:
        print(f"Error getting templates")
        return exception
