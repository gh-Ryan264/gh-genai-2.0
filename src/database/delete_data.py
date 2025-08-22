from database.db import connect_db, close_db
from database.db import db_logger
def bulk_delete_intents(intent_names: list[str]):
    """
    Deletes multiple intents and their associated parameters, responses, and embeddings
    by intent names, without relying on foreign key cascade.
    """
    db_logger.info(f"Starting bulk deletion for intents: {intent_names}")
    if not intent_names:
        print("No intent names provided for deletion.")
        db_logger.warning("No intent names provided for deletion.")
        return
    
    conn = None
    cur = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        db_logger.info("Database connection and cursor established for deletion.")
        cur.execute("SET search_path TO gen_ai, public;")

        # Get all vector_ids for the given intent names
        db_logger.debug(f"Fetching vector_ids for intents: {intent_names}")
        cur.execute(
            """
            SELECT vector_id FROM intent 
            WHERE intent_name = ANY(%s);
            """,
            (intent_names,)
        )
        vector_ids = [row[0] for row in cur.fetchall()]
        db_logger.debug(f"Found vector_ids: {vector_ids}")

        if not vector_ids:
            print("No matching intents found.")
            db_logger.warning("No matching intents found for the provided names.")
            return

        # Delete dependent rows first
        cur.execute(
            """
            DELETE FROM parameter 
            WHERE vector_id = ANY(%s::uuid[]);
            """,
            (vector_ids,)
        )
        db_logger.debug(f"Deleted parameters for vector_ids: {vector_ids}")
        cur.execute(
            """
            DELETE FROM response 
            WHERE vector_id = ANY(%s::uuid[]);
            """,
            (vector_ids,)
        )
        db_logger.debug(f"Deleted responses for vector_ids: {vector_ids}")

        # Delete intents
        cur.execute(
            """
            DELETE FROM intent 
            WHERE intent_name = ANY(%s);
            """,
            (intent_names,)
        )
        db_logger.debug(f"Deleted intents: {intent_names}")

        # Delete related embeddings
        cur.execute(
            """
            DELETE FROM intent_embedding 
            WHERE id = ANY(%s::uuid[]);
            """,
            (vector_ids,)
        )
        db_logger.debug(f"Deleted intent_embeddings for vector_ids: {vector_ids}")

        conn.commit()
        print(f"Deleted {len(intent_names)} intents and their related data successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
        db_logger.error("Rolling back changes due to error.")
        print("Rolling back changes due to error.")
        db_logger.error(f"Error in bulk deletion: {e}")
        print(f"Error in bulk deletion: {e}")

    finally:
        close_db(conn, cur)
