from pydantic import BaseModel, ConfigDict, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    limit : int = Field(default = 5, ge=1, le=10)


class SourceResponse(BaseModel):
    document_id : int 
    filename: str
    page_number : int | None 
    chunk_index : int 
    similarity : float 

class QueryResponse(BaseModel):
    question: str 
    answer : str 
    sources: list[SourceResponse]

    model_config = ConfigDict(from_attributes= True)

