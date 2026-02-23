from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class LectureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: str
    progress: int
    duration: Optional[int] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class LectureStatusResponse(BaseModel):
    id: str
    status: str
    progress: int
    error_message: Optional[str] = None


class FlashcardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question: str
    answer: str
    order: int


class MCQResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question: str
    options: List[str]
    correct_index: int
    explanation: str
    order: int


class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    title: str
    url: str
    thumbnail_url: Optional[str] = None
    topic: Optional[str] = None


class TranscriptData(BaseModel):
    full_text: str
    segments: List[dict]
    language: Optional[str] = None


class LectureDetailResponse(BaseModel):
    id: str
    title: str
    status: str
    progress: int
    duration: Optional[int] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    transcript: Optional[TranscriptData] = None
    notes: Optional[str] = None           # Markdown
    key_concepts: List[str] = []
    flashcards: List[FlashcardResponse] = []
    mcqs: List[MCQResponse] = []
    resources: List[ResourceResponse] = []
