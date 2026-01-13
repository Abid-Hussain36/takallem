from typing import List
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.lecture.letter_writing_sequence_response import LetterWritingSequenceResponse


class LetterWritingSequence(Base):
    __tablename__ = "letter_writing_sequences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True) # PK
    
    lecture_id: Mapped[int] = mapped_column(ForeignKey("letter_writing_lectures.id", ondelete="CASCADE"), nullable=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("letter_writing_problems.id", ondelete="CASCADE"), nullable=True)

    position: Mapped[str] = mapped_column(String)
    sequence_images: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])

    # Relationships
    lecture: Mapped["LetterWritingLecture"] = relationship(back_populates="letter_writing_sequences")
    problem: Mapped["LetterWritingProblem"] = relationship(back_populates="writing_sequence")

    def to_model(self) -> LetterWritingSequenceResponse:
        return LetterWritingSequenceResponse(
            id=self.id,
            lecture_id=self.lecture_id,
            problem_id=self.problem_id,
            position=self.position,
            sequence_images=self.sequence_images
        )