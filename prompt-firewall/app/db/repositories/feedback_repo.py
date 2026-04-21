from __future__ import annotations
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.db.models import FeedbackModel, ScanRequestModel

class FeedbackRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_feedback(self, trace_id: str, label: str, reviewer: Optional[str] = None, reviewer_notes: Optional[str] = None) -> FeedbackModel:
        # Resolve request_fk
        stmt = select(ScanRequestModel).where(ScanRequestModel.trace_id == trace_id)
        result = await self.session.execute(stmt)
        req = result.scalar_one_or_none()
        request_fk = req.id if req else None

        feedback = FeedbackModel(
            trace_id=trace_id,
            request_fk=request_fk,
            label=label,
            reviewer=reviewer,
            reviewer_notes=reviewer_notes
        )
        self.session.add(feedback)
        await self.session.flush()
        return feedback

    async def get_feedback_by_trace_id(self, trace_id: str) -> Optional[FeedbackModel]:
        stmt = select(FeedbackModel).where(FeedbackModel.trace_id == trace_id).order_by(desc(FeedbackModel.created_at))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_metrics(self) -> dict:
        stmt = select(FeedbackModel.label, func.count(FeedbackModel.id)).group_by(FeedbackModel.label)
        result = await self.session.execute(stmt)
        counts = dict(result.all())
        
        return {
            "total_feedbacks": sum(counts.values()),
            "true_positive_count": counts.get("true_positive", 0),
            "false_positive_count": counts.get("false_positive", 0),
            "false_negative_count": counts.get("false_negative", 0),
            "benign_count": counts.get("benign", 0),
            "needs_review_count": counts.get("needs_review", 0)
        }
