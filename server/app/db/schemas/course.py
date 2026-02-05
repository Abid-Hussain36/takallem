from typing import TYPE_CHECKING
from sqlalchemy import ARRAY, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_collection, mapped_column, relationship
from app.db.database import Base
from app.db.enums import AvailableCourse, AvailableDialect
from app.models.db.general_resource.course_response import CourseResponse

if TYPE_CHECKING:
    from app.db.schemas.language import LanguageSchema


class CourseSchema(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True) # PK

    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id", ondelete="CASCADE")) # FK

    course_name: Mapped[AvailableCourse] = mapped_column(Enum(AvailableCourse))
    total_modules: Mapped[int] = mapped_column()
    ref_modules: Mapped[int] = mapped_column(ARRAY(Integer), default=[], server_default='{}')
    image: Mapped[str] = mapped_column(String)
    text_color: Mapped[str] = mapped_column(String)
    default_dialect: Mapped[AvailableDialect | None] = mapped_column(Enum(AvailableDialect)) # Fetch a dummy list of modules until the user picks a dialect

    # Relationships
    language: Mapped["LanguageSchema"] = relationship("LanguageSchema", back_populates="courses")

    def to_model(self) -> CourseResponse:
        return CourseResponse(
            id=self.id,
            course_name=self.course_name,
            total_modules=self.total_modules,
            ref_modules=self.ref_modules,
            image=self.image,
            text_color=self.text_color,
            default_dialect=self.default_dialect,
            language=self.language.language
        )