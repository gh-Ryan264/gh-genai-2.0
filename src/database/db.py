import psycopg2
from dotenv import load_dotenv
import os
from psycopg_pool import AsyncConnectionPool
from psycopg_pool import ConnectionPool

load_dotenv()

# Database connection setup
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("DATABASE_NAME"),
            user=os.environ.get("DATABASE_USER"),
            password=os.environ.get("DATABASE_PASSWORD"),
            host=os.environ.get("DATABASE_HOST"),
        )
        print("Database connection established.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def close_db(conn, cur):
    """Close cursor and connection."""
    if cur:
        cur.close()
    if conn:
        conn.close()
        print("Database connection closed.")

pool = ConnectionPool(os.environ.get("DATABASE_URL"), min_size=1, max_size=5)

def get_pool():
    """Return the global connection pool."""
    return pool

if __name__ == "__main__":

    conn = connect_db()
    close_db(conn)