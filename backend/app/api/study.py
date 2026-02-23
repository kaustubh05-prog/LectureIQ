import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lecture import Lecture, ProcessingStatus
from app.models.mcq import MCQ
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.schemas.study import QuizResultDetail, QuizResultResponse, QuizSubmitRequest
from app.utils.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{lecture_id}/quiz/submit", response_model=QuizResultResponse)
def submit_quiz(
    lecture_id: str,
    request: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lecture = (
        db.query(Lecture)
        .filter(Lecture.id == lecture_id, Lecture.user_id == current_user.id)
        .first()
    )
    if not lecture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecture not found.")

    if lecture.status != ProcessingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lecture is still processing. Please wait for it to complete.",
        )

    mcqs = (
        db.query(MCQ)
        .filter(MCQ.lecture_id == lecture_id)
        .order_by(MCQ.order)
        .all()
    )
    if not mcqs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions found for this lecture.",
        )

    if len(request.answers) != len(mcqs):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected {len(mcqs)} answers, received {len(request.answers)}.",
        )

    # ── Grade ───────────────────────────────────────────────────────────
    correct = 0
    details = []
    for i, (mcq, answer) in enumerate(zip(mcqs, request.answers)):
        is_correct = answer == mcq.correct_index
        if is_correct:
            correct += 1
        details.append(QuizResultDetail(
            question_index=i,
            your_answer=answer,
            correct_answer=mcq.correct_index,
            is_correct=is_correct,
            explanation=mcq.explanation,
        ))

    percentage = round((correct / len(mcqs)) * 100, 1)

    # ── Persist attempt ─────────────────────────────────────────────────
    db.add(QuizAttempt(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        lecture_id=lecture_id,
        score=correct,
        total=len(mcqs),
        answers=request.answers,
        attempted_at=datetime.utcnow(),
    ))
    db.commit()

    logger.info(
        "Quiz submitted: user=%s lecture=%s score=%d/%d (%.1f%%)",
        current_user.id, lecture_id, correct, len(mcqs), percentage,
    )

    return QuizResultResponse(
        score=correct,
        total=len(mcqs),
        percentage=percentage,
        details=details,
    )
