from sqlalchemy import Column, ForeignKey, Index, Integer, String, DateTime, Boolean, ARRAY, UniqueConstraint, null
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True) # PK

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    ) # FK, Many Side
    
    course_name = Column(String, nullable=False)
    dialect = Column(String, nullable=True)
    curr_lesson = Column(Integer, default=1, nullable=False)
    seen_problems = Column(ARRAY(Integer), default=[], nullable=False)
    covered_words = Column(ARRAY(String), default=[], nullable=False)
    coverage_count = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="course_progresses")

    # Makes sure this table has unique rows across these fields
    __table_args__ = (
        UniqueConstraint("user_id", "course_name", "dialect", name="uq_user_course_dialect"),
    )

    def __repr__(self):
        return f"<UserCourseProgress(user_id={self.user_id}, course_id='{self.course_name}', lesson={self.curr_lesson})>"