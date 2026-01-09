from sqlalchemy import ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.db.enums import AvailableCourse
from app.models.db.vocab.vocab_word_response import VocabWordResponse


class VocabWord(Base):
    __tablename__ = "vocab_words"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)  # PK

    lecture_id: Mapped[int] = mapped_column(ForeignKey("vocab_lectures.id"))  # FK for Vocab Lecture

    word: Mapped[str] = mapped_column(String)
    meaning: Mapped[str] = mapped_column(String)
    course: Mapped[AvailableCourse] = mapped_column(Enum(AvailableCourse))
    language: Mapped[str] = mapped_column(String)
    dialect: Mapped[str | None] = mapped_column(String)
    vocab_audio: Mapped[str] = mapped_column(String)

    def to_model(self) -> VocabWordResponse:
        return VocabWordResponse(
            id=self.id,
            lecture_id=self.lecture_id,
            word=self.word,
            meaning=self.meaning,
            course=self.course,
            language=self.language,
            dialect=self.dialect,
            vocab_audio=self.vocab_audio
        )
