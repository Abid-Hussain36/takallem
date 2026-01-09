from pydantic import BaseModel
from app.db.enums import Course


class ModuleResponse(BaseModel):
    id: int
    course: Course
    unit: str
    section: str
    title: str
    number: int
    resource_id: int

