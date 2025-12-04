import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    """
    Create a new PostgreSQL connection using environment variables.

    Required env vars:
        DB_HOST
        DB_PORT (default: 5432)
        DB_NAME
        DB_USER
        DB_PASSWORD
    """
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT", "5432"))
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not all([host, name, user, password]):
        raise RuntimeError(
            "Database configuration is incomplete. "
            "Ensure DB_HOST, DB_NAME, DB_USER, and DB_PASSWORD are set."
        )

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=name,
        user=user,
        password=password,
        cursor_factory=RealDictCursor,
    )

