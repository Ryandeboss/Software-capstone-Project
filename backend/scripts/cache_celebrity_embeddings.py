from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.services.celebrity_embedding_store import upsert_celebrity_embedding_records
from app.services.celebrity_loader import generate_reference_embedding_records


def main():
    records = generate_reference_embedding_records()
    saved_count = upsert_celebrity_embedding_records(records)
    print(f"Saved {saved_count} celebrity embedding row(s) to Supabase.")


if __name__ == "__main__":
    main()
