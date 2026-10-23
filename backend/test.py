from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

print("Testing Gemini model...")

for chunk in client.models.generate_content_stream(
    model="gemini-3.5-flash",
    contents="Reply with the words: Streaming works.",
):
    print("Received:", repr(chunk.text), flush=True)

print("Test complete.")