from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem_set.vocab_reading_problem_set_response import VocabReadingProblemSetResponse


class VocabReadingProblemSet(Base):
    __tablename__ = "vocab_reading_problem_sets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True) # PK

    collection_id: Mapped[int] = mapped_column(ForeignKey("vocab_reading_problem_sets_collection.id", ondelete="CASCADE"))

    set_number: Mapped[int] = mapped_column()
    problem_count: Mapped[int] = mapped_column()

    # Relationships
    collection: Mapped["VocabReadingProblemSets"] = relationship(back_populates="problem_sets")
    problems: Mapped[List["VocabReadingProblem"]] = relationship(
        back_populates="problem_set",
        cascade="all, delete-orphan"
    )

    def to_model(self) -> VocabReadingProblemSetResponse:
        return VocabReadingProblemSetResponse(
            id=self.id,
            set_number=self.set_number,
            problem_count=self.problem_count,
            problems=[p.to_model() for p in self.problems]
        )
