from pydantic import BaseModel
from app.db.enums import AvailableCourse


class GetUserCourseProgressRequest(BaseModel):
    id: int
    course: AvailableCourse