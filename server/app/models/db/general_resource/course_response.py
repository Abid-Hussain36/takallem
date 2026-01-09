from pydantic import BaseModel
from app.db.enums import AvailableCourse


class CourseResponse(BaseModel):
    id: int
    course_name: AvailableCourse
    image: str
    text_color: str