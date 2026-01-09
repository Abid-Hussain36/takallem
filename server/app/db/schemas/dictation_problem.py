from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.models.db.problem.dictation_problem_response import DictationProblemResponse


class DictationProblem(Base):
    __tablename__ = "dictation_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("dictation_problem_sets.id", ondelete="CASCADE"))

    word: Mapped[str] = mapped_column(String)
    word_audio: Mapped[str] = mapped_column(String)

    def to_model(self) -> DictationProblemResponse:
        return DictationProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            word=self.word,
            word_audio=self.word_audio
        )
