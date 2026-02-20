import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lecture_id = Column(String, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    answers = Column(JSON, nullable=False)   # [0, 2, 1, ...]
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="quiz_attempts")
    lecture = relationship("Lecture", back_populates="quiz_attempts")
