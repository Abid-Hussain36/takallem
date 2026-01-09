from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.models.db.problem.discrimination_problem_response import DiscriminationProblemResponse


class DiscriminationProblem(Base):
    __tablename__ = "discrimination_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("discrimination_problem_sets.id", ondelete="CASCADE"))

    word_audio: Mapped[str] = mapped_column(String)
    incorrect_word_audio: Mapped[str] = mapped_column(String)
    answer_choices: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    correct_answer: Mapped[str] = mapped_column(String)

    def to_model(self) -> DiscriminationProblemResponse:
        return DiscriminationProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            word_audio=self.word_audio,
            incorrect_word_audio=self.incorrect_word_audio,
            answer_choices=self.answer_choices,
            correct_answer=self.correct_answer
        )
