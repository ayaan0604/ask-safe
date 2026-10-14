from sqlalchemy import text

from app.core.database import Base, engine
from app.models.entities import User, Document, DocumentChunk

def initialize_database():
    with engine.begin() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    initialize_database()
