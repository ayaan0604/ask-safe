from app.core.database import SessionLocal
from app.services.retrieval_service import retrieve_chunks



def main():
    question = "How does the leave policy work?"

    with SessionLocal() as db:
        results = retrieve_chunks(
            db = db,
            question= question,
            user_role='employee',
            limit= 5
        )

    print(f"retrieved {len(results)} chunks")

    for result in results:
        print("-" * 60)
        print("Document:", result["filename"])
        print("Page:", result["page_number"])
        print("Chunk:", result["chunk_index"])
        print("Distance:", round(result["cosine_distance"], 4))
        print("Similarity:", round(result["similarity"], 4))
        print("Content:", result["content"][:300])

if __name__ == "__main__":
    main()