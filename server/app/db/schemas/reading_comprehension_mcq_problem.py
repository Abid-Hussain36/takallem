from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem.reading_comprehension_mcq_problem_response import ReadingComprehensionMCQProblemResponse


class ReadingComprehensionMCQProblem(Base):
    __tablename__ = "reading_comprehension_mcq_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("reading_comprehension_mcq_problem_sets.id", ondelete="CASCADE"))

    question: Mapped[str] = mapped_column(String)
    question_audio: Mapped[str] = mapped_column(String)
    correct_answer: Mapped[str] = mapped_column(String)
    answer_choices: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])

    # Relationships
    problem_set: Mapped["ReadingComprehensionMCQProblemSet"] = relationship(back_populates="problems")

    def to_model(self) -> ReadingComprehensionMCQProblemResponse:
        return ReadingComprehensionMCQProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            question=self.question,
            question_audio=self.question_audio,
            correct_answer=self.correct_answer,
            answer_choices=self.answer_choices
        )
