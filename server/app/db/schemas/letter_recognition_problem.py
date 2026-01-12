from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.models.db.problem.letter_recognition_problem_response import LetterRecognitionProblemResponse


class LetterRecognitionProblem(Base):
    __tablename__ = "letter_recognition_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("letter_recognition_problem_sets.id", ondelete="CASCADE"))

    word: Mapped[str] = mapped_column(String)
    answer_choices: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    correct_answer: Mapped[str] = mapped_column(String)

    def to_model(self) -> LetterRecognitionProblemResponse:
        return LetterRecognitionProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            word=self.word,
            answer_choices=self.answer_choices,
            correct_answer=self.correct_answer
        )
