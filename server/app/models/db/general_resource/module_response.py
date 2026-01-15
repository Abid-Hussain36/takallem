from pydantic import BaseModel
from app.db.enums import AvailableCourse
from app.models.db.general_resource.resource_response import PolymorphicResource


class ModuleResponse(BaseModel):
    id: int
    course: AvailableCourse
    unit: str
    section: str
    title: str
    number: int
    resource: PolymorphicResource  # Polymorphic resource - can be any Resource subtype

