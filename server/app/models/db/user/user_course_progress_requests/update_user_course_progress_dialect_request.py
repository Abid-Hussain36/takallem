from pydantic import BaseModel
from app.db.enums import AvailableCourse, AvailableDialect


class UpdateUserCourseProgressDialectRequest(BaseModel):
    id: int
    dialect: AvailableDialect