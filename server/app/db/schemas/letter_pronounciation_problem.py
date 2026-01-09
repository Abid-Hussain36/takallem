from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.problem.letter_pronounciation_problem_response import LetterPronounciationProblemResponse


class LetterPronounciationProblem(Resource):
    __tablename__ = "letter_pronounciation_problems"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    problem_count: Mapped[int] = mapped_column()
    question: Mapped[str] = mapped_column(String)
    letter: Mapped[str] = mapped_column(String)
    letter_audio: Mapped[str] = mapped_column(String)

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.LETTER_PRONOUNCIATION_PROBLEM
    }

    def to_model(self) -> LetterPronounciationProblemResponse:
        return LetterPronounciationProblemResponse(
            id=self.id,
            resource_type=self.resource_type,
            problem_count=self.problem_count,
            question=self.question,
            letter=self.letter,
            letter_audio=self.letter_audio
        )
