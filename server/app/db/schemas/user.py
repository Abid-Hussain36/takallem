from typing import List
from sqlalchemy import String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.db.user.user_response import UserResponse


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)  # PK

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    languages_learning: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])  # The list of languages the user is currently learning
    
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
            languages_learning=self.languages_learning,
            course_progresses=[course_progress.to_model() for course_progress in self.course_progresses]
        )
