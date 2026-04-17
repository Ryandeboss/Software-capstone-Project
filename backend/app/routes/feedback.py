from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.feedback_service import record_match_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class MatchFeedbackRequest(BaseModel):
    upload_id: str
    match_id: str
    face_index: int
    action: Literal["confirm", "reject"]
    predicted_name: str
    source_filename: str
    local_path: str
    distance: float | None = None
    threshold_used: float | None = None


@router.post("/matches")
def create_match_feedback(payload: MatchFeedbackRequest):
    return {
        "message": "Feedback recorded.",
        "feedback": record_match_feedback(payload.model_dump()),
    }
