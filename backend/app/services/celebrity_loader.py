from pathlib import Path
import logging
import cv2
from app.services.face_embedding import generate_embedding

BASE_DIR = Path(__file__).resolve().parents[2]
REFERENCE_DIR = BASE_DIR / "data" / "reference"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
logger = logging.getLogger(__name__)

def load_celebrity_embeddings():
    celebrity_db = {}

    logger.info("Loading celebrity reference embeddings from %s", REFERENCE_DIR)

    if not REFERENCE_DIR.exists():
        logger.warning("Reference directory does not exist: %s", REFERENCE_DIR)
        return celebrity_db

    for celeb_path in REFERENCE_DIR.iterdir():
        if not celeb_path.is_dir():
            continue

        embeddings = []
        images_seen = 0

        for img_path in celeb_path.iterdir():
            if img_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue

            images_seen += 1
            image = cv2.imread(str(img_path))
            if image is None:
                logger.warning("Could not read reference image: %s", img_path)
                continue

            face_embedding = generate_embedding(image)

            if face_embedding is not None:
                embeddings.append(face_embedding)
            else:
                logger.warning("No face embedding generated for reference image: %s", img_path)

        if embeddings:
            celebrity_db[celeb_path.name] = embeddings

        logger.info(
            "Reference folder '%s': %s/%s images produced embeddings",
            celeb_path.name,
            len(embeddings),
            images_seen,
        )

    total_embeddings = sum(len(embeddings) for embeddings in celebrity_db.values())
    logger.info(
        "Loaded %s reference embeddings across %s celebrities",
        total_embeddings,
        len(celebrity_db),
    )

    return celebrity_db
