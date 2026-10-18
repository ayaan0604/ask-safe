from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.documents import router as document_router
from app.api.query import router as query_router
from app.api.admin import router as admin_router

app = FastAPI(title= settings.app_name)

origins = settings.allowed_origins.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=['*'],
    allow_methods=['*']
)

app.include_router(auth_router)
app.include_router(document_router)
app.include_router(query_router)
app.include_router(admin_router)

@app.get('/health')
def health():
    return { "status" : "ok" }

