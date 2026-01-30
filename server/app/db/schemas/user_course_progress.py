from typing import Dict
from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.enums import AvailableCourse, AvailableDialect, AvailableLanguage
from app.models.db.user.user_course_progress_response import UserCourseProgressResponse


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)  # PK

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )  # FK, Many Side
    
    course_name: Mapped[AvailableCourse] = mapped_column(Enum(AvailableCourse))
    language: Mapped[AvailableLanguage] = mapped_column(Enum(AvailableLanguage))
    dialect: Mapped[AvailableDialect | None] = mapped_column(Enum(AvailableDialect))
    default_dialect: Mapped[AvailableDialect | None] = mapped_column(Enum(AvailableDialect))
    total_modules: Mapped[int] = mapped_column()
    curr_module: Mapped[int] = mapped_column(default=1)
    covered_words: Mapped[Dict[str, int]] = mapped_column(JSONB, default={})
    problem_counter: Mapped[int] = mapped_column(default=0)
    current_vocab_problem_set: Mapped[int] = mapped_column(default=1)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="course_progresses")  # Lets you access the user object

    # Makes sure this table has unique rows across these fields
    __table_args__ = (
        UniqueConstraint("user_id", "course_name", name="uq_user_course_dialect"),
        Index("idx_user_course_dialect", "user_id", "course_name")
    )

    def to_model(self) -> UserCourseProgressResponse:
        return UserCourseProgressResponse(
            id=self.id,
            course_name=self.course_name,
            language=self.language,
            dialect=self.dialect,
            default_dialect=self.default_dialect,
            total_modules=self.total_modules,
            curr_module=self.curr_module,
            covered_words=self.covered_words,
            problem_counter=self.problem_counter,
            current_vocab_problem_set=self.current_vocab_problem_set
        )
