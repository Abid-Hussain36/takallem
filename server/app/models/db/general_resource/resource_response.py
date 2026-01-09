from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.general_resource.module_response import ModuleResponse


class ResourceResponse(BaseModel):
    id: int
    resource_type: ResourceType
    module: List[ModuleResponse]

