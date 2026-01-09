from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.problem_set.reading_comprehension_text_response import ReadingComprehensionTextResponse


class ReadingComprehensionText(Resource):
    __tablename__ = "reading_comprehension_texts"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    text_title: Mapped[str] = mapped_column(String)
    text: Mapped[List[str]] = mapped_column(ARRAY(String))

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.READING_COMPREHENSION_TEXT
    }

    def to_model(self) -> ReadingComprehensionTextResponse:
        return ReadingComprehensionTextResponse(
            id=self.id,
            resource_type=self.resource_type,
            text_title=self.text_title,
            text=self.text
        )
