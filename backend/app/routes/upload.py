from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.db_service import insert_processed_image_record

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        contents = await file.read()
        file_path.write_bytes(contents)

        db_result = insert_processed_image_record(
            original_filename=file.filename,
            upload_path=str(file_path),
            status="uploaded"
        )

        return {
            "message": "Upload saved locally and metadata inserted into Supabase.",
            "filename": file.filename,
            "local_path": str(file_path),
            "db_result": getattr(db_result, "data", None)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))