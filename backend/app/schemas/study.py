from pydantic import BaseModel, Field, field_validator
from typing import List


class QuizSubmitRequest(BaseModel):
    answers: List[int] = Field(min_length=1)

    @field_validator("answers", mode="before")
    @classmethod
    def validate_answer_range(cls, v):
        for ans in v:
            if not isinstance(ans, int) or not (0 <= ans <= 3):
                raise ValueError("Each answer must be an integer between 0 and 3")
        return v


class QuizResultDetail(BaseModel):
    question_index: int
    your_answer: int
    correct_answer: int
    is_correct: bool
    explanation: str


class QuizResultResponse(BaseModel):
    score: int
    total: int
    percentage: float
    details: List[QuizResultDetail]
