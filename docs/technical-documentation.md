# Technical Documentation

This document describes the current implementation of the Celebrity Face Recognition Photo Organizer.

## System Overview

The app has three main pieces:

- React frontend for image upload, threshold settings, result review, and feedback.
- FastAPI backend for image processing, recognition, settings, feedback, and Supabase access.
- Supabase database for upload metadata and cached celebrity reference embeddings.

## Recognition Flow

When a user uploads an image:

1. `backend/app/routes/upload.py` receives the uploaded file.
2. The file is saved under `backend/data/uploads/`.
3. `detect_faces()` finds face boxes with OpenCV Haar cascades.
4. Upload metadata is inserted into the configured `processed_images` Supabase table.
5. The backend reads cached celebrity embeddings from Supabase through `load_celebrity_embeddings()`.
6. For each detected uploaded face, `generate_embedding()` creates one embedding.
7. `recognize_face()` compares the uploaded embedding against cached celebrity embeddings.
8. The API returns face boxes, recognized names, distances, threshold values, and feedback metadata.

The important performance improvement is step 5: celebrity reference embeddings are fetched from Supabase instead of being regenerated from every reference image on every upload.

## Cached Celebrity Embeddings

The cache table is created by:

```text
backend/database/create_celebrity_embeddings.sql
```

Default table name:

```text
celebrity_embeddings
```

Columns:

- `id`: row UUID
- `celebrity_name`: celebrity folder/name key
- `source_image`: source reference image path relative to `backend/data/reference/`
- `embedding`: JSON array containing the face embedding
- `created_at`: creation timestamp
- `updated_at`: update timestamp

The unique key on `(celebrity_name, source_image)` prevents duplicate cache rows for the same reference image.

## Cache Population Script

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\cache_celebrity_embeddings.py
```

The script:

1. Scans `backend/data/reference/`.
2. Generates embeddings for readable image files.
3. Skips unsupported files and images without usable face encodings.
4. Upserts records into the celebrity embeddings table.

Run this script again whenever celebrity reference images are added, removed, or replaced.

## Fallback Behavior

`load_celebrity_embeddings()` first tries Supabase.

If cached embeddings are available, it returns them immediately.

If the cache is empty or Supabase is unavailable, it falls back to generating embeddings from `backend/data/reference/`. This keeps the app functional, but the upload request will be slower.

## Backend Services

- `face_detection.py`: detects faces in uploaded images.
- `face_embedding.py`: converts images/faces into `face_recognition` embeddings.
- `celebrity_loader.py`: loads cached embeddings or generates fallback reference embeddings.
- `celebrity_embedding_store.py`: fetches and upserts cached embeddings in Supabase.
- `recognition.py`: compares embeddings and applies the recognition threshold.
- `settings_service.py`: stores and validates local recognition threshold settings.
- `feedback_service.py`: writes local match feedback records.
- `db_service.py`: inserts and fetches processed image records.

## API Endpoints

Base URL:

```text
http://127.0.0.1:8000
```

Endpoints:

- `GET /health`: backend health check.
- `POST /upload`: upload one image and receive face recognition results.
- `GET /settings`: read recognition threshold settings.
- `PUT /settings/recognition-threshold`: update the threshold.
- `POST /feedback/matches`: record match feedback.

## Environment Variables

Configured in `backend/.env`:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_BUCKET=project-images
SUPABASE_TABLE=processed_images
SUPABASE_CELEBRITY_EMBEDDINGS_TABLE=celebrity_embeddings
```

`SUPABASE_CELEBRITY_EMBEDDINGS_TABLE` is optional if the table is named `celebrity_embeddings`.

## Local Runtime Data

Generated local data includes:

- `backend/data/uploads/`: uploaded image files.
- `backend/data/feedback/match_feedback.jsonl`: feedback entries.
- `backend/data/app_state/recognition_settings.json`: threshold settings.

Review these files before committing because they often contain local test data.

## Validation Checklist

After changing recognition logic:

1. Run Python compile checks:

```powershell
python -m compileall backend\app backend\scripts
```

2. Confirm the cache table exists in Supabase.
3. Run the cache script.
4. Start the backend.
5. Upload a test image from the frontend.
6. Confirm logs show cached embeddings being fetched from Supabase.
