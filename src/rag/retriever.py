from collections import defaultdict
from psycopg.rows import dict_row
from database.db import get_pool
from rag.embedding_model import get_embedding_query
from database.db import db_logger
import time

def embedding_to_pgvector_str(embedding: list[float]) -> str:
    """Convert list of floats to a PostgreSQL vector string."""
    return "[" + ",".join(map(str, embedding)) + "]"

def format_intents_plain_text(rows):
    """Formats intent data into plain text."""
    intents = defaultdict(lambda: {
        "intent_name": None,
        "description": None,
        "platforms": {}
    })

    for row in rows:
        intent_id = row['embedding_id']
        intents[intent_id]["intent_name"] = row["intent_name"]
        intents[intent_id]["description"] = row["description"]
        platform = row["platform"]
        value = row["value"]
        if platform and value:
            intents[intent_id]["platforms"][platform] = value

    lines = []
    for intent_id, intent_data in intents.items():
        lines.append(f"Intent: {intent_data['intent_name']}")
        lines.append(f"Description: {intent_data['description']}")
        for platform, value in intent_data["platforms"].items():
            lines.append(f"  - {platform}: {value}")
        lines.append("")
    return "\n".join(lines)

def get_top_k_documents(query_embedding: list[float], k: int = 3):
    """Fetch top-K matching intents + responses from Postgres in a single query."""
    total_start = time.time()

    # Convert embedding
    start_time = time.time()
    pgvector_str = embedding_to_pgvector_str(query_embedding)
    db_logger.debug(
        f"Converted embedding to pgvector string in {(time.time() - start_time) * 1000:.2f} ms"
    )

    conn_start = time.time()
    pool = get_pool()
    with pool.connection() as conn:
        db_logger.debug(
            f"Checked out connection in {(time.time() - conn_start) * 1000:.2f} ms"
        )

        with conn.cursor(row_factory=dict_row) as cursor:
            try:
                start_time = time.time()
                cursor.execute(
                    """
                    WITH top_intents AS (
                        SELECT ie.id AS embedding_id
                        FROM intent_embedding ie
                        ORDER BY ie.embedding <=> %s::vector
                        LIMIT %s
                    )
                    SELECT 
                        i.vector_id AS embedding_id,
                        i.intent_name,
                        i.description,
                        r.platform,
                        r.value
                    FROM top_intents ti
                    JOIN intent i ON i.vector_id = ti.embedding_id
                    LEFT JOIN response r ON i.vector_id = r.vector_id;
                    """,
                    (pgvector_str, k),
                )
                results = cursor.fetchall()
                db_logger.debug(
                    f"Fetched top {k} intents (with responses) in {(time.time() - start_time) * 1000:.2f} ms"
                )

            except Exception as e:
                db_logger.error("Error fetching top documents:", exc_info=e)
                return []

    db_logger.info(
        f"Total time of retrieval : {(time.time() - total_start) * 1000:.2f} ms"
    )
    return results


if __name__ == "__main__":
    query_embedding = get_embedding_query("please navigate to worker event details")
    top_documents = get_top_k_documents(query_embedding, 3)
    print(format_intents_plain_text(top_documents))
