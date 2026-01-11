from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.general_resource.dialect_response import DialectResponse


class DialectSelectionResponse(BaseModel):
    id: int
    resource_type: ResourceType
    dialects: List[DialectResponse]

