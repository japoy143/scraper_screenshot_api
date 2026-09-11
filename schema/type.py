from pydantic import BaseModel
from typing import List


class Actions(BaseModel):
    id: str
    action: str
    role: str
    name: str
    secondary_action: str
    input: str
    is_done: bool
    logs: str


class Automations(BaseModel):
    automation_id: str
    automations: List[Actions]
    count: int
    url: str


class ScrapeRequest(BaseModel):
    automation_id: str
    url: str
    actions: List[Actions]


class AutomationTemplate(BaseModel):
    user_id: str
    automation_name: str
    template_id: str
    actions: List[Actions]


class DeleteScreenshotsRequest(BaseModel):
    files: list[str]
