from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType


class ReadingComprehensionTextResponse(BaseModel):
    id: int
    resource_type: ResourceType
    text_title: str
    text: List[str]

