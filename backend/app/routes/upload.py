from pathlib import Path
from uuid import uuid4
import logging

import cv2
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.db_service import insert_processed_image_record
from app.services.face_detection import detect_faces

from app.services.face_embedding import generate_embedding
from app.services.celebrity_loader import load_celebrity_embeddings
from app.services.recognition import recognize_face


router = APIRouter(prefix="/upload", tags=["upload"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("")
async def upload_image(file: UploadFile = File(...)):
    try:
        logger.info("Upload request received for file: %s", file.filename)
        celebrity_db = load_celebrity_embeddings()
        celebrity_count = len(celebrity_db)
        reference_embedding_count = sum(len(embeddings) for embeddings in celebrity_db.values())
        logger.info(
            "Celebrity database ready: %s celebrities, %s embeddings",
            celebrity_count,
            reference_embedding_count,
        )

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
        logger.info("Saved uploaded file to %s (%s bytes)", file_path, len(contents))

        face_boxes = detect_faces(str(file_path))
        faces_detected = len(face_boxes)
        logger.info("Detected %s face(s) in uploaded image", faces_detected)

        db_result = insert_processed_image_record(
            original_filename=original_name,
            upload_path=str(file_path),
            status="uploaded",
            detected_faces=faces_detected,
        )
        logger.info("Inserted processed image metadata into Supabase")

        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError(f"Could not read uploaded image for embedding: {file_path}")

        results = []

        for index, box in enumerate(face_boxes, start=1):
            x = box["x"]
            y = box["y"]
            width = box["width"]
            height = box["height"]
            known_face_location = [(y, x + width, y + height, x)]

            logger.info(
                "Generating embedding for uploaded face %s using detected box %s",
                index,
                box,
            )
            embedding = generate_embedding(image, known_face_location)

            if embedding is None:
                logger.warning("Uploaded face %s did not produce an embedding", index)
                results.append({"name": "unknown"})
                continue

            name, distance = recognize_face(embedding, celebrity_db)
            logger.info("Uploaded face %s recognition result: name=%s distance=%s", index, name, distance)

            results.append({
                "name": name,
                "distance": float(distance) if distance is not None else None
            })

        logger.info("Upload processing complete for %s: %s", original_name, results)
        return {
            "message": "Upload successful. File stored locally and metadata inserted into Supabase.",
            "filename": original_name,
            "local_path": str(file_path),
            "faces_detected": faces_detected,
            "face_boxes": face_boxes,
            "db_result": getattr(db_result, "data", None),
            "recognized_faces": results
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Upload processing failed")
        raise HTTPException(status_code=500, detail=str(exc))
    

