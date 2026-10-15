from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from typing import Annotated

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.entities import User 
from app.schemas.query import QueryRequest, QueryResponse
from app.services.retrieval_service import retrieve_chunks
from app.services.generation_service import generate_answer


router = APIRouter(prefix = "/api", tags = ["Query"])

@router.post('/query', response_model = QueryResponse)
def query_documents(
    request: QueryRequest,
    current_user : Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):

    chunks = retrieve_chunks(
        db= db,
        question= request.question,
        user_role = current_user.role,
        limit = request.limit
    )

    try:
        answer = generate_answer(
            question= request.question,
            chunks= chunks
        )
    except Exception as e:
        print(e)
        
        raise HTTPException(
            status_code= status.HTTP_502_BAD_GATEWAY,
            detail= "The answer generation service is temporarily unavailable"
        ) from e

    return {
        'question' : request.question,
        'answer' : answer,
        'sources': [
            {
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "similarity": chunk["similarity"],

            }
            for chunk in chunks
        ]
    }