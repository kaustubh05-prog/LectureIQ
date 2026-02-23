import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lecture_id = Column(String, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_text = Column(String, nullable=False)
    segments = Column(JSON, nullable=False)  # [{start, end, text}]
    language = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lecture = relationship("Lecture", back_populates="transcript")
