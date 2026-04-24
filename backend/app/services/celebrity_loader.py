from pathlib import Path
import logging
import cv2
from app.services.face_embedding import generate_embedding
from app.services.celebrity_embedding_store import fetch_cached_celebrity_embeddings

BASE_DIR = Path(__file__).resolve().parents[2]
REFERENCE_DIR = BASE_DIR / "data" / "reference"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
logger = logging.getLogger(__name__)


def generate_reference_embedding_records():
    records = []

    logger.info("Generating celebrity reference embeddings from %s", REFERENCE_DIR)

    if not REFERENCE_DIR.exists():
        logger.warning("Reference directory does not exist: %s", REFERENCE_DIR)
        return records

    for celeb_path in REFERENCE_DIR.iterdir():
        if not celeb_path.is_dir():
            continue

        images_seen = 0
        embeddings_seen = 0

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
                embeddings_seen += 1
                records.append(
                    {
                        "celebrity_name": celeb_path.name,
                        "source_image": str(img_path.relative_to(REFERENCE_DIR)),
                        "embedding": face_embedding,
                    }
                )
            else:
                logger.warning("No face embedding generated for reference image: %s", img_path)

        logger.info(
            "Reference folder '%s': %s/%s images produced embeddings",
            celeb_path.name,
            embeddings_seen,
            images_seen,
        )

    logger.info("Generated %s total celebrity reference embedding record(s)", len(records))
    return records


def _records_to_celebrity_db(records):
    celebrity_db = {}

    for record in records:
        celebrity_db.setdefault(record["celebrity_name"], []).append(record["embedding"])

    return celebrity_db


def load_celebrity_embeddings():
    try:
        celebrity_db = fetch_cached_celebrity_embeddings()
    except Exception:
        logger.exception("Could not fetch cached celebrity embeddings from Supabase")
        celebrity_db = {}

    if celebrity_db:
        return celebrity_db

    logger.warning(
        "No cached celebrity embeddings found in Supabase; generating from reference images as a fallback"
    )
    celebrity_db = _records_to_celebrity_db(generate_reference_embedding_records())

    total_embeddings = sum(len(embeddings) for embeddings in celebrity_db.values())
    logger.info(
        "Loaded %s reference embeddings across %s celebrities",
        total_embeddings,
        len(celebrity_db),
    )

    return celebrity_db
