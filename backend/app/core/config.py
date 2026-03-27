import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "project-images")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "processed_images")

if not SUPABASE_URL:
    raise ValueError("Missing SUPABASE_URL in backend/.env")

if not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_KEY in backend/.env")