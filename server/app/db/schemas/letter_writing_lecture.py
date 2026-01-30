from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.lecture.letter_writing_lecture_response import LetterWritingLectureResponse

if TYPE_CHECKING:
    from app.db.schemas.letter_writing_sequence import LetterWritingSequence


class LetterWritingLecture(Resource):
    __tablename__ = "letter_writing_lectures"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    letter: Mapped[str] = mapped_column(String)

    # Relationships
    letter_writing_sequences: Mapped[List["LetterWritingSequence"]] = relationship(
        back_populates="lecture",
        cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.LETTER_WRITING_LECTURE
    }

    def to_model(self) -> LetterWritingLectureResponse:
        return LetterWritingLectureResponse(
            id=self.id,
            resource_type=self.resource_type,
            letter=self.letter,
            content=self.content,
            letter_writing_sequences=[seq.to_model() for seq in self.letter_writing_sequences]
        )
