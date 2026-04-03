from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.db_service import insert_processed_image_record
from app.services.face_detection import detect_faces

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("")
async def upload_image(file: UploadFile = File(...)):
    try:
        original_name = file.filename or ""
        extension = Path(original_name).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only JPG, JPEG, PNG, and WEBP are allowed."
            )

        unique_filename = f"{uuid4().hex}{extension}"
        file_path = UPLOAD_DIR / unique_filename

        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        file_path.write_bytes(contents)

        face_boxes = detect_faces(str(file_path))
        faces_detected = len(face_boxes)

        db_result = insert_processed_image_record(
            original_filename=original_name,
            upload_path=str(file_path),
            status="uploaded",
            detected_faces=faces_detected,
        )

        return {
            "message": "Upload successful. File stored locally and metadata inserted into Supabase.",
            "filename": original_name,
            "local_path": str(file_path),
            "faces_detected": faces_detected,
            "face_boxes": face_boxes,
            "db_result": getattr(db_result, "data", None),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))