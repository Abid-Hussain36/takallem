from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.lecture.info_lecture_response import InfoLectureResponse


class InfoLecture(Resource):
    __tablename__ = "info_lectures"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    content: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.INFO_LECTURE
    }

    def to_model(self) -> InfoLectureResponse:
        return InfoLectureResponse(
            id=self.id,
            resource_type=self.resource_type,
            content=self.content
        )
