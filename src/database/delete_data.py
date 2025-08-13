from database.db import connect_db, close_db

def bulk_delete_intents(intent_names: list[str]):
    """
    Deletes multiple intents and their associated parameters, responses, and embeddings
    by intent names, without relying on foreign key cascade.
    """
    if not intent_names:
        print("No intent names provided for deletion.")
        return
    
    conn = None
    cur = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SET search_path TO gen_ai, public;")

        # Get all vector_ids for the given intent names
        cur.execute(
            """
            SELECT vector_id FROM intent 
            WHERE intent_name = ANY(%s);
            """,
            (intent_names,)
        )
        vector_ids = [row[0] for row in cur.fetchall()]

        if not vector_ids:
            print("No matching intents found.")
            return

        # Delete dependent rows first
        cur.execute(
            """
            DELETE FROM parameter 
            WHERE vector_id = ANY(%s::uuid[]);
            """,
            (vector_ids,)
        )
        cur.execute(
            """
            DELETE FROM response 
            WHERE vector_id = ANY(%s::uuid[]);
            """,
            (vector_ids,)
        )

        # Delete intents
        cur.execute(
            """
            DELETE FROM intent 
            WHERE intent_name = ANY(%s);
            """,
            (intent_names,)
        )

        # Delete related embeddings
        cur.execute(
            """
            DELETE FROM intent_embedding 
            WHERE id = ANY(%s::uuid[]);
            """,
            (vector_ids,)
        )

        conn.commit()
        print(f"Deleted {len(intent_names)} intents and their related data successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Rolling back changes due to error.")
        print(f"Error in bulk deletion: {e}")

    finally:
        close_db(conn, cur)
