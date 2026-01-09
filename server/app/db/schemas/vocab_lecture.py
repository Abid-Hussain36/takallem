from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.lecture.vocab_lecture_response import VocabLectureResponse


class VocabLecture(Resource):
    __tablename__ = "vocab_lectures"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    vocab_words: Mapped[List["VocabWord"]] = relationship()  # List of vocab words covered

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.VOCAB_LECTURE
    }

    def to_model(self) -> VocabLectureResponse:
        return VocabLectureResponse(
            id=self.id,
            resource_type=self.resource_type,
            vocab_words=[vw.to_model() for vw in self.vocab_words]
        )
