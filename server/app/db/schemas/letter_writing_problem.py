from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.models.db.problem.letter_writing_problem_response import LetterWritingProblemResponse


class LetterWritingProblem(Base):
    __tablename__ = "letter_writing_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("letter_writing_problem_sets.id", ondelete="CASCADE"))

    word: Mapped[str] = mapped_column(String)
    position: Mapped[str] = mapped_column(String)
    reference_writing: Mapped[str] = mapped_column(String)
    writing_sequence: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])

    def to_model(self) -> LetterWritingProblemResponse:
        return LetterWritingProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            word=self.word,
            position=self.position,
            reference_writing=self.reference_writing,
            writing_sequence=self.writing_sequence
        )
