from typing import List
from sqlalchemy import Enum, ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.enums import AvailableLanguage
from app.models.db.general_resource.language_response import LanguageResponse


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True) # PK

    language: Mapped[AvailableLanguage] = mapped_column(Enum(AvailableLanguage))
    image: Mapped[str] = mapped_column(String)
    text_color: Mapped[str] = mapped_column(String)

    # Relatonships
    dialects: Mapped[List["Dialect"]] = relationship(
        back_populates="language",
        cascade="all, delete-orphan"
    )
    courses: Mapped[List["Course"]] = relationship(
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
