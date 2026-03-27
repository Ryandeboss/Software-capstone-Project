from pathlib import Path
from app.services.db_service import insert_processed_image_record, fetch_processed_images
from app.services.storage_service import upload_file_to_bucket
from app.core.config import SUPABASE_BUCKET

def main():
    print("=== SUPABASE TEST START ===")

    # Test DB insert
    db_insert = insert_processed_image_record(
        original_filename="test_upload.txt",
        upload_path="backend/test_upload.txt",
        status="uploaded"
    )
    print("DB insert response:")
    print(getattr(db_insert, "data", db_insert))

    # Test DB fetch
    db_fetch = fetch_processed_images(limit=5)
    print("DB fetch response:")
    print(getattr(db_fetch, "data", db_fetch))

    # Test Storage upload
    local_file = Path("test_upload.txt")
    remote_file = "tests/test_upload.txt"
    storage_result = upload_file_to_bucket(str(local_file), remote_file)

    print("Storage upload response:")
    print(storage_result)
    print(f"Uploaded to bucket: {SUPABASE_BUCKET}/{remote_file}")

    print("=== SUPABASE TEST COMPLETE ===")

if __name__ == "__main__":
    main()