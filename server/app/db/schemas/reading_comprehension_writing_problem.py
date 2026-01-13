from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.problem.reading_comprehension_writing_problem_response import ReadingComprehensionWritingProblemResponse


class ReadingComprehensionWritingProblem(Base):
    __tablename__ = "reading_comprehension_writing_problems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    problem_set_id: Mapped[int] = mapped_column(ForeignKey("reading_comprehension_writing_problem_sets.id", ondelete="CASCADE"))

    question_audio: Mapped[str] = mapped_column(String)

    # Relationships
    problem_set: Mapped["ReadingComprehensionWritingProblemSet"] = relationship(back_populates="problems")

    def to_model(self) -> ReadingComprehensionWritingProblemResponse:
        return ReadingComprehensionWritingProblemResponse(
            id=self.id,
            problem_set_id=self.problem_set_id,
            question_audio=self.question_audio
        )
