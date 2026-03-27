from app.services.supabase_client import supabase
from app.core.config import SUPABASE_TABLE

def insert_processed_image_record(original_filename: str, upload_path: str, status: str = "uploaded"):
    payload = {
        "original_filename": original_filename,
        "upload_path": upload_path,
        "status": status,
        "detected_faces": 0,
        "matched_celebrities": []
    }

    response = supabase.table(SUPABASE_TABLE).insert(payload).execute()
    return response

def fetch_processed_images(limit: int = 10):
    response = supabase.table(SUPABASE_TABLE).select("*").limit(limit).execute()
    return response