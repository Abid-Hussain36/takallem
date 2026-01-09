from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.lecture.letter_speaking_lecture_response import LetterSpeakingLectureResponse


class LetterSpeakingLecture(Resource):
    __tablename__ = "letter_speaking_lectures"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    letter: Mapped[str] = mapped_column(String)
    content: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    letter_audio: Mapped[str] = mapped_column(String)
    word_audios: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.LETTER_SPEAKING_LECTURE
    }

    def to_model(self) -> LetterSpeakingLectureResponse:
        return LetterSpeakingLectureResponse(
            id=self.id,
            resource_type=self.resource_type,
            letter=self.letter,
            content=self.content,
            letter_audio=self.letter_audio,
            word_audios=self.word_audios
        )
