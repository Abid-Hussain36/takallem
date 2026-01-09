from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem.vocab_listening_problem_response import VocabListeningProblemResponse


class VocabListeningProblem(Base):
    __tablename__ = "vocab_listening_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("vocab_listening_problem_sets.id", ondelete="CASCADE"))

    vocab_word_id: Mapped[int] = mapped_column(ForeignKey("vocab_words.id"))
    answer_choices: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])

    # Relationships
    vocab_word: Mapped["VocabWord"] = relationship()

    def to_model(self) -> VocabListeningProblemResponse:
        return VocabListeningProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            vocab_word_id=self.vocab_word_id,
            answer_choices=self.answer_choices,
            vocab_word=self.vocab_word.to_model()
        )
