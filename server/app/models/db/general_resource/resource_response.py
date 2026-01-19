from pydantic import BaseModel, Field
from typing import Union
from app.db.enums import ResourceType


class ResourceResponse(BaseModel):
    id: int
    resource_type: ResourceType
