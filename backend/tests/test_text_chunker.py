
from app.services.text_chunker import chunk_pages


def test_chunks_preserve_page_numbers_and_overlap():
    pages = [
        {
            "page_number": 4,
            "text": "A" * 1200,
        }
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=1000,
        overlap=150,
    )

    assert len(chunks) == 2
    assert chunks[0]["page_number"] == 4
    assert chunks[1]["page_number"] == 4
    assert chunks[0]["content"][-150:] == chunks[1]["content"][:150]
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_index"] == 1
