
import uuid
import psycopg2
from psycopg2.extras import execute_values, Json
from sentence_transformers import SentenceTransformer
from database.db import connect_db, close_db
from rag.embedding_model import get_embedding_doc, get_embedding_query

def upsert_data(data):
    """Ingests data in bulk, upserting new intents and deleting missing ones."""
    conn = connect_db()
    if not conn:
        return

    cur = conn.cursor()
    cur.execute("SET search_path TO gen_ai, public;")
    print("Database schema set to gen_ai, public.")
    
    try:
        # Get current vector_ids
        cur.execute("SELECT vector_id FROM intent;")
        existing_vector_ids = {str(row[0]) for row in cur.fetchall()}
        print(f"Existing vector IDs fetched: {len(existing_vector_ids)} found.")

        intent_rows = []
        parameter_rows = []
        response_rows = []
        new_vector_ids = set()

        # Prepare new rows
        for item in data:
            embedding = get_embedding_doc(item["description"])
            vector_id = str(uuid.uuid4())
            new_vector_ids.add(vector_id)

            # Intent row
            intent_rows.append((vector_id, item["intent"], 'NAVIGATION', item["description"], embedding))

            # Parameter rows
            required_params = set(item.get("required", []))
            for param_name, param_type in item["parameters"].items():
                metadata = {"type": param_type, "required": param_name in required_params}
                parameter_rows.append((vector_id, param_name, Json(metadata)))

            # Response rows
            for platform, value in item["responses"].items():
                response_rows.append((vector_id, platform, value))

        # Upsert intent_embedding
        execute_values(
            cur,
            """
            INSERT INTO intent_embedding (id, embedding)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding
            """,
            [(vid, emb) for vid, _, _, _, emb in intent_rows]
        )
        print("Bulk upsert for intent_embedding completed.")

        # Upsert intent
        execute_values(
            cur,
            """
            INSERT INTO intent (vector_id, intent_name, category, description)
            VALUES %s
            ON CONFLICT (intent_name) DO UPDATE
            SET vector_id = EXCLUDED.vector_id,
                category = EXCLUDED.category,
                description = EXCLUDED.description
            """,
            [(vid, name, cat, desc) for vid, name, cat, desc, _ in intent_rows]
        )
        print("Bulk upsert for intent table completed.")

        # Upsert parameters
        execute_values(
            cur,
            """
            INSERT INTO parameter (vector_id, parameter_name, metadata)
            VALUES %s
            ON CONFLICT (vector_id, parameter_name) DO UPDATE
            SET metadata = EXCLUDED.metadata
            """,
            parameter_rows
        )
        print("Bulk upsert for parameters completed.")

        # Upsert responses
        execute_values(
            cur,
            """
            INSERT INTO response (vector_id, platform, value)
            VALUES %s
            ON CONFLICT (value) DO UPDATE
            SET vector_id = EXCLUDED.vector_id,
                platform = EXCLUDED.platform
            """,
            response_rows
        )
        conn.commit()
        print("Bulk upsert for responses completed.")
    except Exception as e:
        conn.rollback()
        print("Error during ingestion:", e)
        print("Rolling back changes due to error.")
    finally:
        close_db(conn, cur)
