from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.db.enums import AvailableCourse
from app.models.db.general_resource.course_response import CourseResponse


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True) # PK

    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id", ondelete="CASCADE")) # FK

    course_name: Mapped[AvailableCourse] = mapped_column(Enum(AvailableCourse))
    image: Mapped[str] = mapped_column(String)
    text_color: Mapped[str] = mapped_column(String)

    def to_model(self) -> CourseResponse:
        return CourseResponse(
            id=self.id,
            course_name=self.course_name,
            image=self.image,
            text_color=self.text_color
        )