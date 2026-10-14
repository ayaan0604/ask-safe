from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import DocumentChunk, Document
from app.services.embedding_service import embed_texts

ROLE_ACCESS = {
    'employee' : ['employee'],
    'manager' : ['employee', 'manager'],
    'hr' : ['employee', 'manager', 'hr']
}

def retrieve_chunks(
        db: Session,
        question: str,
        user_role: str,
        limit: int = 5,
)-> list[dict]:

    question = question.strip()

    if not question:
        raise ValueError('Question is empty')

    if user_role not in ROLE_ACCESS:
        raise ValueError("Inavlid user role")

    if not 1<=limit <= 20:
        raise ValueError("Limit must be between 1 and 20")


    query_embedding = embed_texts([question], "RETRIEVAL_QUERY")[0]

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label('cosine_distance')

    #filter authorized documents only

    stmt = (
        select(
            Document.id.label("document_id"),
            Document.filename,
            Document.access_level,
            DocumentChunk.chunk_index,
            DocumentChunk.page_number,
            DocumentChunk.content,
            distance,
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
        .where(
            Document.access_level.in_(ROLE_ACCESS[user_role])

        )
        .order_by(distance)
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    results = []

    for row in rows:
        cosine_distance = float(row.cosine_distance)

        results.append(
            {
                'document_id' : row.document_id,
                'filename' : row.filename,
                "access_level" : row.access_level,
                'chunk_index' : row.chunk_index,
                'page_number' : row.page_number,
                'content' : row.content,
                'cosine_distance' : cosine_distance,
                'similarity' : 1.0 - cosine_distance
            }
        )

    return results