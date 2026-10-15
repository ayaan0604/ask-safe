from fastapi import FastAPI
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.documents import router as document_router
from app.api.query import router as query_router

app = FastAPI(title= settings.app_name)

app.include_router(auth_router)
app.include_router(document_router)
app.include_router(query_router)

@app.get('/health')
def health():
    return { "status" : "ok" }

