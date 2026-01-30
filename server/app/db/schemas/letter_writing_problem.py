from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem.letter_writing_problem_response import LetterWritingProblemResponse

if TYPE_CHECKING:
    from app.db.schemas.letter_writing_problem_set import LetterWritingProblemSet
    from app.db.schemas.letter_writing_sequence import LetterWritingSequence


class LetterWritingProblem(Base):
    __tablename__ = "letter_writing_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("letter_writing_problem_sets.id", ondelete="CASCADE"))

    letter: Mapped[str] = mapped_column(String)
    position: Mapped[str] = mapped_column(String)
    reference_writing: Mapped[str] = mapped_column(String)

    # Relationships
    problem_set: Mapped["LetterWritingProblemSet"] = relationship(back_populates="problems")
    writing_sequence: Mapped["LetterWritingSequence"] = relationship(
        back_populates="problem",
        cascade="all, delete-orphan",
        uselist=False
    )

    def to_model(self) -> LetterWritingProblemResponse:
        return LetterWritingProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            letter=self.letter,
            position=self.position,
            reference_writing=self.reference_writing,
            writing_sequence=self.writing_sequence.to_model()
        )
