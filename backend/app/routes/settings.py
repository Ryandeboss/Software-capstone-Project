from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.settings_service import get_recognition_settings, update_recognition_threshold

router = APIRouter(prefix="/settings", tags=["settings"])


class ThresholdUpdateRequest(BaseModel):
    threshold: float


@router.get("")
def read_settings():
    return get_recognition_settings()


@router.put("/recognition-threshold")
def update_threshold(payload: ThresholdUpdateRequest):
    try:
        return update_recognition_threshold(payload.threshold)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
