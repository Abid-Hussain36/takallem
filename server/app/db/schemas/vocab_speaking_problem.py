from typing import List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.schemas.vocab_speaking_problem_word import vocab_speaking_problem_word
from app.models.db.problem.vocab_speaking_problem_response import VocabSpeakingProblemResponse


class VocabSpeakingProblem(Base):
    __tablename__ = "vocab_speaking_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("vocab_speaking_problem_sets.id", ondelete="CASCADE"))

    question: Mapped[str] = mapped_column(String)
    
    # Relationships
    vocab_words: Mapped[List["VocabWord"]] = relationship(
        secondary=vocab_speaking_problem_word
    )

    def to_model(self) -> VocabSpeakingProblemResponse:
        return VocabSpeakingProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            question=self.question,
            vocab_words=[vw.to_model() for vw in self.vocab_words]
        )
