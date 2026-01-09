from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.problem_set.reading_comprehension_mcq_problem_set_response import ReadingComprehensionMCQProblemSetResponse


class ReadingComprehensionMCQProblemSet(Resource):
    __tablename__ = "reading_comprehension_mcq_problem_sets"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    text_id: Mapped[int] = mapped_column(ForeignKey("reading_comprehension_texts.id"))

    problem_count: Mapped[int] = mapped_column()

    # Relationships
    problems: Mapped[List["ReadingComprehensionMCQProblem"]] = relationship()
    text: Mapped["ReadingComprehensionText"] = relationship()

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.READING_COMPREHENSION_MCQ_PROBLEM_SET
    }

    def to_model(self) -> ReadingComprehensionMCQProblemSetResponse:
        return ReadingComprehensionMCQProblemSetResponse(
            id=self.id,
            resource_type=self.resource_type,
            text_id=self.text_id,
            problem_count=self.problem_count,
            problems=[p.to_model() for p in self.problems],
            text=self.text.to_model()
        )
