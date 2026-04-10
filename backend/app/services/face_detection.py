from pathlib import Path
import logging
import cv2

logger = logging.getLogger(__name__)

def detect_faces(image_path: str) -> list[dict]:
    image_file = Path(image_path)

    if not image_file.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(str(image_file))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    logger.info("Detecting faces in %s with image shape %s", image_file, image.shape)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )

    results = []
    for (x, y, w, h) in faces:
        results.append({
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h),
        })

    logger.info("OpenCV Haar cascade detected %s face(s): %s", len(results), results)
    return results
