from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.problem_set.vocab_reading_problem_sets_response import VocabReadingProblemSetsResponse


class VocabReadingProblemSets(Resource):
    __tablename__ = "vocab_reading_problem_sets_collection"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    set_limit: Mapped[int] = mapped_column()

    # Relationship
    problem_sets: Mapped[List["VocabReadingProblemSet"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.VOCAB_READING_PROBLEM_SETS
    }

    def to_model(self) -> VocabReadingProblemSetsResponse:
        return VocabReadingProblemSetsResponse(
            id=self.id,
            resource_type=self.resource_type,
            set_limit=self.set_limit,
            problem_sets=[ps.to_model() for ps in self.problem_sets]
        )