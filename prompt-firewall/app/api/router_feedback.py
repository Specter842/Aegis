from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackMetrics
from app.db.repositories.feedback_repo import FeedbackRepo

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(feedback_in: FeedbackCreate, db: AsyncSession = Depends(get_db)):
    repo = FeedbackRepo(db)
    feedback = await repo.create_feedback(
        trace_id=feedback_in.trace_id,
        label=feedback_in.label.value,
        reviewer=feedback_in.reviewer,
        reviewer_notes=feedback_in.reviewer_notes
    )
    if not feedback:
        raise HTTPException(status_code=404, detail="Could not associate feedback with trace ID.")
    return feedback

@router.get("/metrics", response_model=FeedbackMetrics)
async def get_feedback_metrics(db: AsyncSession = Depends(get_db)):
    repo = FeedbackRepo(db)
    metrics = await repo.get_metrics()
    return metrics

@router.get("/{trace_id}", response_model=FeedbackResponse)
async def get_feedback(trace_id: str, db: AsyncSession = Depends(get_db)):
    repo = FeedbackRepo(db)
    feedback = await repo.get_feedback_by_trace_id(trace_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.get("/", response_model=FeedbackResponse)
async def get_feedback_by_query(trace_id: str = Query(..., description="Trace ID of the request"), db: AsyncSession = Depends(get_db)):
    repo = FeedbackRepo(db)
    feedback = await repo.get_feedback_by_trace_id(trace_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback
