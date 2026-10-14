from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


from app.api.deps import require_hr_admin
from app.core.database import get_db
from app.models.entities import User, Document, DocumentChunk
from app.schemas.documents import DocumentUploadResponse
from app.services.text_chunker import chunk_pages
from app.services.pdf_extractor import extract_pages
from app.services.embedding_service import embed_texts



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

    document = Document(
        filename = filename,
        access_level = access_level,
        status = 'ready',
        uploaded_by = current_user.id
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
