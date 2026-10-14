from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    access_level : str
    status: str
    chunk_count: int


    model_config = ConfigDict(from_attributes=True)

    