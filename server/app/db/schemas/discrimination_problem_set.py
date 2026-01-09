from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.problem_set.discrimination_problem_set_response import DiscriminationProblemSetResponse


class DiscriminationProblemSet(Resource):
    __tablename__ = "discrimination_problem_sets"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    problem_count: Mapped[int] = mapped_column()

    # Relationships
    problems: Mapped[List["DiscriminationProblem"]] = relationship()

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.DISCRIMINATION_PROBLEM_SET
    }

    def to_model(self) -> DiscriminationProblemSetResponse:
        return DiscriminationProblemSetResponse(
            id=self.id,
            resource_type=self.resource_type,
            problem_count=self.problem_count,
            problems=[p.to_model() for p in self.problems]
        )
