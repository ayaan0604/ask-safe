from pathlib import Path
from typing import Annotated, Literal
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status, Response

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import delete, func, select


from app.api.deps import require_hr_admin, get_current_user
from app.core.database import get_db
from app.models.entities import User, Document, DocumentChunk
from app.schemas.documents import DocumentUploadResponse
from app.services.text_chunker import chunk_pages
from app.services.pdf_extractor import extract_pages
from app.services.embedding_service import embed_texts
from app.services.storage import upload_pdf, delete_pdf, download_pdf



router = APIRouter(prefix= "/api/documents", tags= ['Documents'])

MAX_FILE_SIZE = 10 * 1024 * 1024

EMBEDDING_BATCH_SIZE = 50


@router.post('/upload', response_model=DocumentUploadResponse, status_code= status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    access_level: Annotated[
        Literal['employee', 'manager', 'hr'],
        Form()
    ],
    current_user : Annotated[User, Depends(require_hr_admin)],
    db: Annotated[Session, Depends(get_db)]
):
    #file name validation
    
    filename = Path(file.filename or "").name

    if not filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail= 'Please upload a pdf file.'
        )

    #read 10MB atmost (+1 byte)

    pdf_bytes = bytearray()

    try:
        while len(pdf_bytes)<=MAX_FILE_SIZE:
            remaining = MAX_FILE_SIZE+1 - len(pdf_bytes)
            if remaining <= 0:
                break

            data = await file.read(min(1024*1024, remaining))

            if not data:
                break

            pdf_bytes.extend(data)

    finally:
        await file.close()

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail = "PDF is Empty")

    if len(pdf_bytes)> MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail= "File size must be 10MB or smaller"
        )

    #check pdf siganture before further processing
    if not bytes(pdf_bytes).startswith(b"%PDF-"):
        raise HTTPException(
            status_code= 400,
            detail= 'Uploaded File is not a valid pdf'
        )

    #extract text and page numbers
    try:
        pages = extract_pages(bytes(pdf_bytes))

    except ValueError as e:
        raise HTTPException(status_code=400, detail= str(e)) from e


    #split into chunks
    chunks = chunk_pages(pages)

    
    #generate embeddings
    try:
        vectors = []

        for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
            batch = chunks[start : start+EMBEDDING_BATCH_SIZE]

            batch_vectors = embed_texts(
                texts = [chunk['content'] for chunk in batch],
                task_type= 'RETRIEVAL_DOCUMENT'
            )

            vectors.extend(batch_vectors)

        if len(vectors) != len(chunks):
            raise RuntimeError("Embedding Count Mismatched")

    except Exception as e:
        raise HTTPException(
            status_code = 502,
            detail= 'Could not generate document embeddings.'
        ) from e 

    #upload the pdf to bucket
    storage_path = f'documents/{uuid4().hex}.pdf'

    try:
        upload_pdf(storage_path, bytes(pdf_bytes))
    except Exception as e:
        print("Couldn't upload document: ", e)
        raise HTTPException(
            status_code=502,
            detail= "Couldn't store the original document."
        ) from e

    document = Document(
        filename = filename,
        access_level = access_level,
        status = 'ready',
        uploaded_by = current_user.id,
        storage_path = storage_path
    )

    try:
        db.add(document)
        db.flush()

        db.add_all([
            DocumentChunk(
                document_id = document.id,
                chunk_index = chunk['chunk_index'],
                page_number = chunk['page_number'],
                content = chunk['content'],
                embedding = vector 
            )

            for chunk, vector in zip(chunks, vectors)
        ])

        db.commit()
        db.refresh(document)

    except SQLAlchemyError as e:
        db.rollback()

        delete_pdf(storage_path)

        raise HTTPException(
            status_code= 500,
            detail = 'Could not save the document'
        ) from e

    return DocumentUploadResponse(
        id = document.id,
        filename= document.filename,
        access_level = document.access_level,
        status = document.status,
        chunk_count = len(chunks)
    )


@router.delete('/{document_id}')
def delete_document(
    document_id: int,
    current_user: Annotated[User, Depends(require_hr_admin)],
    db: Annotated[Session, Depends(get_db)]
):

    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code= 404,
            detail= 'document not found'
        )

    try:
        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document_id
            )
        )
        db.delete(document)
        db.commit()

        if document.storage_path:
            try:
                delete_pdf(document.storage_path)
            except Exception as e:
                print("Bucket document Cleanup failed: ", e)



    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail= 'could not delete document'
        ) from e

    return {
        'message' : 'Document deleted successfully',
        'document_id' : document_id
    }


class DocumentListResponse(BaseModel):
    id: int
    filename: str
    access_level: str 
    status: str 
    uploaded_by: int
    created_at: datetime
    chunk_count : int 

@router.get("", response_model=list[DocumentListResponse])
def list_documents(
    current_user : Annotated[User, Depends(get_current_user)],
    db : Annotated[Session, Depends(get_db)]
):
    stmt = (
        select(
            Document.id,
            Document.filename,
            Document.access_level,
            Document.status,
            Document.uploaded_by,
            Document.created_at,
            func.count(DocumentChunk.id).label("chunk_count"),
        )
        .outerjoin(
            DocumentChunk,
            DocumentChunk.document_id == Document.id
        )
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
    )

    rows = db.execute(stmt).all()

    access_levels = {
        'employee' : {'employee'},
        'manager' : {'employee', 'manager'},
        'hr_admin' : {'employee', 'manager', 'hr'},
    }

    user_role = current_user.role
    allowed_roles = access_levels.get(user_role, set())

    return [
        DocumentListResponse(
            id=row.id,
            filename=row.filename,
            access_level=row.access_level,
            status=row.status,
            uploaded_by=row.uploaded_by,
            created_at=row.created_at,
            chunk_count=row.chunk_count,
        )
        for row in rows if row.access_level in allowed_roles 
    ]

@router.get('/{document_id}/download')
def download_document(
    document_id : int,
    current_user : Annotated[User, Depends(get_current_user)],
    db : Annotated[Session, Depends(get_db)]
):

    document = db.get(Document, document_id)

    if document is None:
        print("not in db", id)
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if not document.storage_path:
        print("not on supabase")
        raise HTTPException(
            status_code=404,
            detail="Original PDF is not available",
        )

    allowed_levels = {
        'employee' : {'employee'},
        'manager' : {'employee', 'manager'},
        'hr_admin' : {'employee', 'manager', 'hr'},
    }

    user_role = current_user.role
    permitted_levels = allowed_levels.get(user_role, set())

    if document.access_level not in permitted_levels:
        print("not permitted")
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )


    try:
        pdf_bytes = download_pdf(document.storage_path)
    except Exception as e:
        print("Failed to fetch document from bucket ")
        raise HTTPException(
            status_code=502,
            detail="Could not download the document",
        ) from e

    return Response(
        content= pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f'attachment; filename="{document.filename}"'
        }
    )
