import logging
import numpy as np

logger = logging.getLogger(__name__)

def _format_name(name):
    if not name:
        return "unknown"
    return name.replace("_", " ").title()

def compare_embeddings(face_embedding, celebrity_db):
    best_match = None
    best_distance = float("inf")
    comparisons = 0

    for celeb_name, embeddings in celebrity_db.items():
        for celeb_embedding in embeddings:
            distance = np.linalg.norm(face_embedding - celeb_embedding)
            comparisons += 1

            if distance < best_distance:
                best_distance = distance
                best_match = celeb_name

    logger.info(
        "Compared uploaded face against %s reference embedding(s); best_match=%s best_distance=%s",
        comparisons,
        best_match,
        best_distance,
    )
    return best_match, best_distance

def recognize_face(face_embedding, celebrity_db, threshold=0.6):
    if not celebrity_db:
        logger.warning("Recognition guess for uploaded face: unknown (celebrity database is empty)")
        return "unknown", None

    name, distance = compare_embeddings(face_embedding, celebrity_db)
    display_name = _format_name(name)

    if distance < threshold:
        logger.info(
            "Recognition guess for uploaded face: %s (distance %.4f, threshold %.4f)",
            display_name,
            distance,
            threshold,
        )
        return name, distance
    else:
        logger.info(
            "Recognition guess for uploaded face: %s, but returning unknown because distance %.4f is above threshold %.4f",
            display_name,
            distance,
            threshold,
        )
        return "unknown", distance
