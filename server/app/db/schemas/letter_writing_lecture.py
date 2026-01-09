from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.lecture.letter_writing_lecture_response import LetterWritingLectureResponse


class LetterWritingLecture(Resource):
    __tablename__ = "letter_writing_lectures"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    letter: Mapped[str] = mapped_column(String)
    content: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    letter_writing_sequence: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.LETTER_WRITING_LECTURE
    }

    def to_model(self) -> LetterWritingLectureResponse:
        return LetterWritingLectureResponse(
            id=self.id,
            resource_type=self.resource_type,
            letter=self.letter,
            content=self.content,
            letter_writing_sequence=self.letter_writing_sequence
        )
