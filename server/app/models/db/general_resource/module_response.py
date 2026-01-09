from pydantic import BaseModel
from app.db.enums import AvailableCourse


class ModuleResponse(BaseModel):
    id: int
    course: AvailableCourse
    unit: str
    section: str
    title: str
    number: int
    resource_id: int

