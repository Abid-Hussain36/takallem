from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.problem_set.vocab_listening_problem_set_response import VocabListeningProblemSetResponse


class VocabListeningProblemSet(Resource):
    __tablename__ = "vocab_listening_problem_sets"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    set_number: Mapped[int] = mapped_column()
    set_limit: Mapped[int] = mapped_column()
    problem_count: Mapped[int] = mapped_column()

    # Relationships
    problems: Mapped[List["VocabListeningProblem"]] = relationship()

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.VOCAB_LISTENING_PROBLEM_SET
    }

    def to_model(self) -> VocabListeningProblemSetResponse:
        return VocabListeningProblemSetResponse(
            id=self.id,
            resource_type=self.resource_type,
            set_number=self.set_number,
            set_limit=self.set_limit,
            problem_count=self.problem_count,
            problems=[p.to_model() for p in self.problems]
        )
