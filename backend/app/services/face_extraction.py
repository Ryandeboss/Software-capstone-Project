import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)

def extract_faces(image_path: str, face_boxes: list[dict]) -> list[np.ndarray]:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image for face extraction: {image_path}")

    faces = []

    for index, box in enumerate(face_boxes, start=1):
        x, y, w, h = box["x"], box["y"], box["width"], box["height"]

        face = image[y:y+h, x:x+w]
        if face.size == 0:
            logger.warning("Skipping empty crop for face %s with box %s", index, box)
            continue

        # Normalize size (important)
        face = cv2.resize(face, (160, 160))

        faces.append(face)

    logger.info("Extracted %s cropped face(s) from %s box(es)", len(faces), len(face_boxes))
    return faces
