
import os

import pg8000
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Create and return a PostgreSQL connection."""

    return pg8000.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
