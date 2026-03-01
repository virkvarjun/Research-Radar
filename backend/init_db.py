"""Create all database tables. Run once after starting Postgres.

Usage:
    cd backend
    python init_db.py
"""

from sqlalchemy import create_engine, text

from app.config import settings
from app.db import Base

# Import all models so Base.metadata knows about them
from app.models import (  # noqa: F401
    User, Paper, PaperChunk, Thread, Event,
    Digest, DigestPaper, Institution, UserInstitution, SavedPaper,
)


def main():
    sync_url = settings.database_url_sync
    print(f"Connecting to: {sync_url}")
    engine = create_engine(sync_url)

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
        print("✓ pgvector extension enabled")

    Base.metadata.create_all(engine)
    print("✓ All tables created")
    engine.dispose()


if __name__ == "__main__":
    main()
