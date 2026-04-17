import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.core.config import BASE_DIR

FEEDBACK_DIR = BASE_DIR / "data" / "feedback"
FEEDBACK_PATH = FEEDBACK_DIR / "match_feedback.jsonl"

_feedback_lock = Lock()


def record_match_feedback(payload: dict) -> dict:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

    record = {
        "feedback_id": uuid4().hex,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }

    with _feedback_lock:
        with FEEDBACK_PATH.open("a", encoding="utf-8") as feedback_file:
            feedback_file.write(json.dumps(record) + "\n")

    return record
