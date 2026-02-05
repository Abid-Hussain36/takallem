from typing import List
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.schemas.resource import Resource
from app.db.enums import AvailableDialect, ResourceType
from app.models.db.problem_set.vocab_speaking_problem_sets_response import VocabSpeakingProblemSetsResponse


class VocabSpeakingProblemSets(Resource):
    __tablename__ = "vocab_speaking_problem_sets_collection"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    # Relationship
    problem_sets: Mapped[List["VocabSpeakingProblemSet"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.VOCAB_SPEAKING_PROBLEM_SETS
    }

    def to_model(self) -> VocabSpeakingProblemSetsResponse:
        return VocabSpeakingProblemSetsResponse(
            id=self.id,
            resource_type=self.resource_type,
            problem_sets=[ps.to_model() for ps in self.problem_sets]
        )
