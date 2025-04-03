import os
import psycopg2
import dotenv

dotenv.load_dotenv()

def get_connection():
    PG_HOST = os.getenv("PG_HOST")
    PG_DATABASE = os.getenv("PG_DB")
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_PORT = os.getenv("PG_PORT")

    conn = psycopg2.connect(
        host=PG_HOST,
        database=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
        port=PG_PORT,
        sslmode="require"
    )
    return conn
