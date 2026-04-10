import logging
import cv2
import numpy as np
import face_recognition

logger = logging.getLogger(__name__)

def generate_embedding(image: np.ndarray, face_locations=None):
    try:
        if image is None:
            logger.warning("Cannot generate embedding because image is None")
            return None

        if len(image.shape) != 3 or image.shape[2] != 3:
            logger.warning("Cannot generate embedding for image with shape: %s", image.shape)
            return None

        if image.dtype != np.uint8:
            image = image.astype(np.uint8)

        # safer than image[:, :, ::-1]
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)

        if face_locations is None:
            face_locations = face_recognition.face_locations(rgb)
        else:
            logger.debug("Using provided face locations: %s", face_locations)

        if len(face_locations) == 0:
            logger.info("No face_recognition face locations found for image shape: %s", image.shape)
            return None

        logger.debug("face_recognition found %s face location(s)", len(face_locations))
        encodings = face_recognition.face_encodings(rgb, face_locations)

        if len(encodings) == 0:
            logger.warning("face_recognition found locations but produced no encodings")
            return None

        return encodings[0]

    except Exception:
        logger.exception("Failed to generate embedding")
        return None
