from typing import List, TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.enums import AvailableLanguage
from app.models.db.general_resource.language_response import LanguageResponse

if TYPE_CHECKING:
    from app.db.schemas.dialect import DialectSchema
    from app.db.schemas.course import CourseSchema


class LanguageSchema(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True) # PK

    language: Mapped[AvailableLanguage] = mapped_column(Enum(AvailableLanguage))
    image: Mapped[str] = mapped_column(String)
    text_color: Mapped[str] = mapped_column(String)

    # Relatonships
    dialects: Mapped[List["DialectSchema"]] = relationship(
        "DialectSchema",
        back_populates="language",
        cascade="all, delete-orphan"
    )
    courses: Mapped[List["CourseSchema"]] = relationship(
        "CourseSchema",
        back_populates="language",
        cascade="all, delete-orphan"
    )

    def to_model(self) -> LanguageResponse:
        return LanguageResponse(
            id=self.id,
            language=self.language,
            image=self.image,
            text_color=self.text_color,
            dialects=[dialect.to_model() for dialect in self.dialects],
            courses=[course.to_model() for course in self.courses]
        )
