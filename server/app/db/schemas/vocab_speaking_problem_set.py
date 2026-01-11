from typing import List
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem_set.vocab_speaking_problem_set_response import VocabSpeakingProblemSetResponse
from app.db.enums import Gender


class VocabSpeakingProblemSet(Base):
    __tablename__ = "vocab_speaking_problem_sets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    collection_id: Mapped[int] = mapped_column(ForeignKey("vocab_speaking_problem_sets_collection.id", ondelete="CASCADE"))

    problem_count: Mapped[int] = mapped_column()
    gender: Mapped[Gender] = mapped_column(Enum(Gender))

    # Relationships
    problems: Mapped[List["VocabSpeakingProblem"]] = relationship()

    def to_model(self) -> VocabSpeakingProblemSetResponse:
        return VocabSpeakingProblemSetResponse(
            id=self.id,
            problem_count=self.problem_count,
            gender=self.gender,
            problems=[p.to_model() for p in self.problems]
        )
