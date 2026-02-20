import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ProcessingStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    duration = Column(Integer, nullable=True)  # seconds
    status = Column(Enum(ProcessingStatus), nullable=False, default=ProcessingStatus.UPLOADING)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="lectures")
    transcript = relationship(
        "Transcript", back_populates="lecture",
        uselist=False, cascade="all, delete-orphan"
    )
    note = relationship(
        "Note", back_populates="lecture",
        uselist=False, cascade="all, delete-orphan"
    )
    flashcards = relationship(
        "Flashcard", back_populates="lecture",
        cascade="all, delete-orphan", order_by="Flashcard.order"
    )
    mcqs = relationship(
        "MCQ", back_populates="lecture",
        cascade="all, delete-orphan", order_by="MCQ.order"
    )
    resources = relationship(
        "Resource", back_populates="lecture",
        cascade="all, delete-orphan"
    )
    quiz_attempts = relationship("QuizAttempt", back_populates="lecture")
