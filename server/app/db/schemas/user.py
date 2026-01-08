from sqlalchemy import Column, Integer, String, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True) # PK

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    languages_learning = Column(ARRAY(String), default=[], nullable=False) # The list of languages the user is currently learning
    
    # Relationships
    course_progresses = relationship("UserCourseProgress", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', languages={self.languages_learning})>"
