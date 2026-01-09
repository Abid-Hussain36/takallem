from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.models.db.problem.letter_joining_problem_response import LetterJoiningProblemResponse


class LetterJoiningProblem(Base):
    __tablename__ = "letter_joining_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("letter_joining_problem_sets.id", ondelete="CASCADE"))

    word: Mapped[str] = mapped_column(String)
    letter_list: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])

    def to_model(self) -> LetterJoiningProblemResponse:
        return LetterJoiningProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            word=self.word,
            letter_list=self.letter_list
        )
