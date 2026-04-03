from pathlib import Path
import os
from dotenv import load_dotenv

# This file lives at: backend/app/core/config.py
# So backend/.env is: parents[2] / ".env"
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "project-images")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "processed_images")

if not SUPABASE_URL:
    raise ValueError(f"Missing SUPABASE_URL in {ENV_PATH}")

if not SUPABASE_KEY:
    raise ValueError(f"Missing SUPABASE_KEY in {ENV_PATH}")