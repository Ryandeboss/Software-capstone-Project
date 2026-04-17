import json
import logging
from threading import Lock

from app.core.config import BASE_DIR

logger = logging.getLogger(__name__)

STATE_DIR = BASE_DIR / "data" / "app_state"
SETTINGS_PATH = STATE_DIR / "recognition_settings.json"

DEFAULT_RECOGNITION_THRESHOLD = 0.6
MIN_RECOGNITION_THRESHOLD = 0.3
MAX_RECOGNITION_THRESHOLD = 1.0

_settings_lock = Lock()


def _ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_threshold(threshold: float) -> float:
    numeric_threshold = float(threshold)
    if numeric_threshold < MIN_RECOGNITION_THRESHOLD or numeric_threshold > MAX_RECOGNITION_THRESHOLD:
        raise ValueError(
            f"Threshold must be between {MIN_RECOGNITION_THRESHOLD} and {MAX_RECOGNITION_THRESHOLD}."
        )
    return round(numeric_threshold, 3)


def _default_settings() -> dict[str, float]:
    return {
        "recognition_threshold": DEFAULT_RECOGNITION_THRESHOLD,
    }


def get_recognition_settings() -> dict[str, float]:
    with _settings_lock:
        _ensure_state_dir()

        if not SETTINGS_PATH.exists():
            defaults = _default_settings()
            SETTINGS_PATH.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
            return {
                **defaults,
                "min_threshold": MIN_RECOGNITION_THRESHOLD,
                "max_threshold": MAX_RECOGNITION_THRESHOLD,
                "default_threshold": DEFAULT_RECOGNITION_THRESHOLD,
            }

        try:
            stored_settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Recognition settings file is invalid JSON. Resetting to defaults.")
            stored_settings = _default_settings()
            SETTINGS_PATH.write_text(json.dumps(stored_settings, indent=2), encoding="utf-8")

        threshold = stored_settings.get("recognition_threshold", DEFAULT_RECOGNITION_THRESHOLD)

        try:
            normalized_threshold = _normalize_threshold(threshold)
        except (TypeError, ValueError):
            logger.warning("Recognition threshold value is invalid. Resetting to default.")
            normalized_threshold = DEFAULT_RECOGNITION_THRESHOLD
            stored_settings["recognition_threshold"] = normalized_threshold
            SETTINGS_PATH.write_text(json.dumps(stored_settings, indent=2), encoding="utf-8")

        if normalized_threshold != threshold:
            stored_settings["recognition_threshold"] = normalized_threshold
            SETTINGS_PATH.write_text(json.dumps(stored_settings, indent=2), encoding="utf-8")

        return {
            "recognition_threshold": normalized_threshold,
            "min_threshold": MIN_RECOGNITION_THRESHOLD,
            "max_threshold": MAX_RECOGNITION_THRESHOLD,
            "default_threshold": DEFAULT_RECOGNITION_THRESHOLD,
        }


def update_recognition_threshold(threshold: float) -> dict[str, float]:
    normalized_threshold = _normalize_threshold(threshold)

    with _settings_lock:
        _ensure_state_dir()
        payload = {"recognition_threshold": normalized_threshold}
        SETTINGS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    logger.info("Updated recognition threshold to %.3f", normalized_threshold)
    return {
        "recognition_threshold": normalized_threshold,
        "min_threshold": MIN_RECOGNITION_THRESHOLD,
        "max_threshold": MAX_RECOGNITION_THRESHOLD,
        "default_threshold": DEFAULT_RECOGNITION_THRESHOLD,
    }
