from supabase import create_client

from app.core.config import settings


supabase_client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)

BUCKET_NAME = settings.supabase_bucket_name

def upload_pdf(storage_path: str, pdf_bytes: bytes):
    return supabase_client.storage.from_(BUCKET_NAME).upload(
        path = storage_path,
        file = pdf_bytes,
        file_options={
            "content-type": "application/pdf",
            "upsert": "false",
        }
    )

def download_pdf(storage_path: str)-> bytes:
    
    return supabase_client.storage.from_(BUCKET_NAME).download(storage_path)
   

def delete_pdf(storage_path: str):
    return supabase_client.storage.from_(BUCKET_NAME).remove(storage_path)