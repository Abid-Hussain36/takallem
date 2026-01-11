from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem_set.vocab_listening_problem_set_response import VocabListeningProblemSetResponse


class VocabListeningProblemSet(Base):
    __tablename__ = "vocab_listening_problem_sets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    collection_id: Mapped[int] = mapped_column(ForeignKey("vocab_listening_problem_sets_collection.id", ondelete="CASCADE"))

    set_number: Mapped[int] = mapped_column()
    problem_count: Mapped[int] = mapped_column()

    # Relationships
    problems: Mapped[List["VocabListeningProblem"]] = relationship()

    def to_model(self) -> VocabListeningProblemSetResponse:
        return VocabListeningProblemSetResponse(
            id=self.id,
            set_number=self.set_number,
            problem_count=self.problem_count,
            problems=[p.to_model() for p in self.problems]
        )
