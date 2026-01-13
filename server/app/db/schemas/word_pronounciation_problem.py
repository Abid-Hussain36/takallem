from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem.word_pronounciation_problem_response import WordPronounciationProblemResponse


class WordPronounciationProblem(Base):
    __tablename__ = "word_pronounciation_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("word_pronounciation_problem_sets.id", ondelete="CASCADE"))

    question: Mapped[str] = mapped_column(String)
    word: Mapped[str] = mapped_column(String)
    word_audio: Mapped[str] = mapped_column(String)

    # Relationships
    problem_set: Mapped["WordPronounciationProblemSet"] = relationship(back_populates="problems")

    def to_model(self) -> WordPronounciationProblemResponse:
        return WordPronounciationProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            question=self.question,
            word=self.word,
            word_audio=self.word_audio
        )
