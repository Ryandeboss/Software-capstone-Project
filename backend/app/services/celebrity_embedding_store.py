import logging
from typing import Iterable

import numpy as np

from app.core.config import SUPABASE_CELEBRITY_EMBEDDINGS_TABLE
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)


def _embedding_to_list(embedding) -> list[float]:
    return np.asarray(embedding, dtype=float).tolist()


def _row_to_embedding(row: dict) -> np.ndarray | None:
    embedding = row.get("embedding")
    if not embedding:
        return None

    try:
        return np.asarray(embedding, dtype=float)
    except (TypeError, ValueError):
        logger.warning("Skipping invalid cached embedding row: %s", row)
        return None


def fetch_cached_celebrity_embeddings() -> dict[str, list[np.ndarray]]:
    response = (
        supabase.table(SUPABASE_CELEBRITY_EMBEDDINGS_TABLE)
        .select("celebrity_name,embedding,source_image")
        .execute()
    )
    rows = getattr(response, "data", None) or []
    celebrity_db: dict[str, list[np.ndarray]] = {}

    for row in rows:
        celebrity_name = row.get("celebrity_name")
        embedding = _row_to_embedding(row)

        if not celebrity_name or embedding is None:
            continue

        celebrity_db.setdefault(celebrity_name, []).append(embedding)

    total_embeddings = sum(len(embeddings) for embeddings in celebrity_db.values())
    logger.info(
        "Fetched %s cached celebrity embedding(s) across %s celebrity folder(s) from Supabase",
        total_embeddings,
        len(celebrity_db),
    )
    return celebrity_db


def upsert_celebrity_embedding_records(records: Iterable[dict]) -> int:
    payload = []

    for record in records:
        payload.append(
            {
                "celebrity_name": record["celebrity_name"],
                "source_image": record["source_image"],
                "embedding": _embedding_to_list(record["embedding"]),
            }
        )

    if not payload:
        logger.warning("No celebrity embeddings were available to upsert")
        return 0

    response = (
        supabase.table(SUPABASE_CELEBRITY_EMBEDDINGS_TABLE)
        .upsert(payload, on_conflict="celebrity_name,source_image")
        .execute()
    )
    saved_rows = getattr(response, "data", None) or payload
    logger.info(
        "Upserted %s celebrity embedding row(s) into Supabase table '%s'",
        len(saved_rows),
        SUPABASE_CELEBRITY_EMBEDDINGS_TABLE,
    )
    return len(saved_rows)
