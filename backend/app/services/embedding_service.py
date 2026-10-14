from google import genai
from google.genai import types 

from app.core.config import settings

client = genai.Client(api_key= settings.gemini_api_key)

EMBEDDING_MODEL = 'gemini-embedding-001'
EMBEDDING_DIMENSIONS = 768


def embed_texts(
        texts: list[str],
        task_type: str
)-> list[list[float]]:

    #generate embeddings for a batch of texts

    if not texts:
        return []

    response = client.models.embed_content(
        model = EMBEDDING_MODEL,
        contents = texts,
        config= types.EmbedContentConfig(
            task_type = task_type,
            output_dimensionality= EMBEDDING_DIMENSIONS
        )
    )

    if response.embeddings is None:
        raise RuntimeError("Gemini returned no embeddings")

    vectors = [
        embedding.values for embedding in response.embeddings
    ]

    if any(
        vector is None or len(vector)!= EMBEDDING_DIMENSIONS
        for vector in vectors
    ):
        raise RuntimeError("Invalid embedding dimensions returned by gemini")

    return vectors