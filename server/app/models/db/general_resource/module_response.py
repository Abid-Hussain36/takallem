from pydantic import BaseModel
from app.db.enums import AvailableCourse, AvailableDialect


class ModuleResponse(BaseModel):
    id: int
    course: AvailableCourse
    dialect: AvailableDialect | None
    unit: str
    section: str
    title: str
    number: int
    resource_id: int

