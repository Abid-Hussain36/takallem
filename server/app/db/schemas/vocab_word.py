from sqlalchemy import ForeignKey, Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.enums import AvailableCourse
from app.models.db.vocab.vocab_word_response import VocabWordResponse


class VocabWord(Base):
    __tablename__ = "vocab_words"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)  # PK

    lecture_id: Mapped[int] = mapped_column(ForeignKey("vocab_lectures.id"))  # FK for Vocab Lecture

    number: Mapped[int] = mapped_column(Integer)
    word: Mapped[str] = mapped_column(String)
    meaning: Mapped[str] = mapped_column(String)
    course: Mapped[AvailableCourse] = mapped_column(Enum(AvailableCourse))
    language: Mapped[str] = mapped_column(String)
    dialect: Mapped[str | None] = mapped_column(String)
    vocab_audio: Mapped[str] = mapped_column(String)

    # Relationships
    lecture: Mapped["VocabLecture"] = relationship(back_populates="vocab_words")

    def to_model(self) -> VocabWordResponse:
        return VocabWordResponse(
            id=self.id,
            lecture_id=self.lecture_id,
            number=self.number,
            word=self.word,
            meaning=self.meaning,
            course=self.course,
            language=self.language,
            dialect=self.dialect,
            vocab_audio=self.vocab_audio
        )
