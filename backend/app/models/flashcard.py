import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lecture_id = Column(String, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lecture = relationship("Lecture", back_populates="flashcards")
