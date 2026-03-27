from pathlib import Path
from app.services.supabase_client import supabase
from app.core.config import SUPABASE_BUCKET

def upload_file_to_bucket(local_file_path: str, remote_path: str):
    file_path = Path(local_file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {local_file_path}")

    with open(file_path, "rb") as f:
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=remote_path,
            file=f,
            file_options={"content-type": "text/plain", "upsert": "true"}
        )

    return response