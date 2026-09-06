import os
from dotenv import load_dotenv
from supabase import create_client, Client
from schema.type import Automations

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
client: Client = create_client(url, key)


def get_automations():
    try:
        response = client.table("automations").select("*").execute()
        print(response)
        return response
    except Exception as exception:
        print(f"Error getting automations")
        return exception


def add_run_automation(automation: Automations):
    try:
        response = (
            client.table("automations")
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
            client.table("automations")
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
            client.table("automations")
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
            client.table("automations")
            .delete()
            .eq("automation_id", automation_id)
            .execute()
        )
        return response
    except Exception as exception:
        print(f"Error deleting action: {exception}")
        return exception
