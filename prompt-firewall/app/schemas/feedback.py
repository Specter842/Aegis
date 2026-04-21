from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class FeedbackLabelEnum(str, Enum):
    true_positive = "true_positive"
    false_positive = "false_positive"
    false_negative = "false_negative"
    benign = "benign"
    needs_review = "needs_review"

class FeedbackCreate(BaseModel):
    trace_id: str
    label: FeedbackLabelEnum
    reviewer: Optional[str] = None
    reviewer_notes: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    trace_id: str
    request_fk: Optional[int]
    label: FeedbackLabelEnum
    reviewer: Optional[str]
    reviewer_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackMetrics(BaseModel):
    total_feedbacks: int
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int
    benign_count: int
    needs_review_count: int
