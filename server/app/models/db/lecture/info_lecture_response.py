from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType


class InfoLectureResponse(BaseModel):
    id: int
    resource_type: ResourceType
    content: List[str]

