import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class MCQ(Base):
    __tablename__ = "mcqs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lecture_id = Column(String, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)           # ["A", "B", "C", "D"]
    correct_index = Column(Integer, nullable=False)  # 0–3
    explanation = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lecture = relationship("Lecture", back_populates="mcqs")
