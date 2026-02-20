import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lecture_id = Column(String, ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False)    # "youtube" | "documentation" | "practice"
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lecture = relationship("Lecture", back_populates="resources")
