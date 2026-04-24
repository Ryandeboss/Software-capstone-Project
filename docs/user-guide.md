# User Guide

This guide explains how to use the Celebrity Face Recognition Photo Organizer as a local development app.

## Start the App

Start the backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Start the frontend in another terminal:

```powershell
cd frontend
npm run dev
```

Open the frontend URL shown by Vite, usually:

```text
http://localhost:5173
```

## Upload Images

1. Use the upload panel to choose one or more images.
2. Supported formats are JPG, JPEG, PNG, and WEBP.
3. Click **Upload Images**.
4. Wait for the upload and recognition process to complete.

For each uploaded image, the app shows:

- The original image preview.
- The number of detected faces.
- Face boxes over the preview.
- The best celebrity match for each detected face.
- The match distance and threshold used.

## Understand Match Results

Each detected face is compared to cached celebrity embeddings in Supabase.

- A lower distance means the uploaded face is closer to that celebrity reference embedding.
- If the best distance is below the current threshold, the app returns the celebrity name.
- If the best distance is above the threshold, the app returns `unknown`.

The default threshold is `0.6`.

## Adjust Recognition Settings

Use the recognition settings panel to adjust the match threshold.

- Lower values are stricter and reduce false positives.
- Higher values are looser and may return more matches.
- The allowed range is `0.30` to `1.00`.
- Click **Save Threshold** to apply the value to future uploads.
- Click **Use Default** to load the default value, then save it if you want it applied.

## Submit Feedback

After a face is recognized, use the feedback controls to confirm or reject the result.

Feedback records are stored locally in:

```text
backend/data/feedback/match_feedback.jsonl
```

Each record includes the upload ID, match ID, face index, predicted name, distance, threshold, and action.

## Troubleshooting

If uploads are slow, make sure the celebrity embedding cache has been populated:

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\cache_celebrity_embeddings.py
```

If settings do not load, verify the backend is running at:

```text
http://127.0.0.1:8000
```

If no faces are found, try a clearer image with a front-facing face.

If many results are `unknown`, raise the threshold slightly.

If incorrect celebrities are accepted too often, lower the threshold.
