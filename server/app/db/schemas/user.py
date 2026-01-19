from typing import List
from sqlalchemy import String, ARRAY, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.user.user_response import UserResponse
from app.db.enums import AvailableCourse, Gender, AvailableDialect


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)  # PK

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    gender: Mapped[Gender] = mapped_column(Enum(Gender))
    current_course: Mapped[AvailableCourse | None] = mapped_column(Enum(AvailableCourse))
    current_dialect: Mapped[AvailableDialect | None] = mapped_column(Enum(AvailableDialect))
    languages_learning: Mapped[List[str]] = mapped_column(ARRAY(String), default=[]) # The list of languages the user is currently learning
    languages_learned: Mapped[List[str]] = mapped_column(ARRAY(String), default=[]) # The list of languages the user has successfully learned on the app
    courses_completed: Mapped[List[str]] = mapped_column(ARRAY(String), default=[]) # The list of courses the user has completed
    
    # Relationships
    # Relationships basically help you access the objects we have in our relations
    # When user is deleted, all progress objects deleted too and orphans
    course_progresses: Mapped[List["UserCourseProgress"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )  # List of courses user is taking and progress in them

    # Response Conversion
    def to_model(self) -> UserResponse:
        return UserResponse(
            id=self.id,
            email=self.email,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            gender=self.gender,
            current_course=self.current_course,
            current_dialect=self.current_dialect,
            languages_learning=self.languages_learning,
            languages_learned=self.languages_learned,
            courses_completed=self.courses_completed,
            course_progresses=[course_progress.to_model() for course_progress in self.course_progresses]
        )
