import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lecture_id = Column(String, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, unique=True)
    content = Column(Text, nullable=False)       # Markdown
    key_concepts = Column(JSON, default=list)    # ["concept1", ...]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lecture = relationship("Lecture", back_populates="note")
