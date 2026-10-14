def chunk_pages(
        pages : list[dict],
        chunk_size: int = 1000,
        overlap : int = 150
) -> list[dict]:

    #splits extracted page texts into overalpping chunks

    if chunk_size<= 0:
        raise ValueError("Chunk size must be a positive integer")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be postive and less than chunk size:", chunk_size )

    chunks = []
    chunk_idx = 0
    step = chunk_size - overlap

    for page in pages:
        text = page['text']
        page_number = page['page_number']

        for start in range(0, len(text), step):
            content = text[start: start+chunk_size].strip()

            if not content:
                continue

            chunks.append({
                'chunk_index': chunk_idx,
                'page_number' : page_number,
                'content' : content
            })

            chunk_idx += 1

    return chunks


