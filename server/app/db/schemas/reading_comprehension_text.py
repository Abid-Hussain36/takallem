from typing import List
from sqlalchemy import String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem_set.reading_comprehension_text_response import ReadingComprehensionTextResponse


class ReadingComprehensionText(Base):
    __tablename__ = "reading_comprehension_texts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    text_title: Mapped[str] = mapped_column(String)
    text: Mapped[List[str]] = mapped_column(ARRAY(String))

    # Relationships
    mcq_problem_sets: Mapped[List["ReadingComprehensionMCQProblemSet"]] = relationship(back_populates="text")
    writing_problem_sets: Mapped[List["ReadingComprehensionWritingProblemSet"]] = relationship(back_populates="text")

    def to_model(self) -> ReadingComprehensionTextResponse:
        return ReadingComprehensionTextResponse(
            id=self.id,
            text_title=self.text_title,
            text=self.text
        )
