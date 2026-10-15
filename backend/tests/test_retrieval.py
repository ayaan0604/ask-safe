from app.core.database import SessionLocal
from app.services.retrieval_service import retrieve_chunks, ROLE_ACCESS

QUESTIONS = [
    "What are the rules for employee leave?",
    "How should managers approve team budgets?",
    "What are the procedures for an internal investigation?",
    "What are the compensation bands?",
]

def main():
    with SessionLocal() as db:
        for role, allowed_levels in ROLE_ACCESS.items():
            print(f"\n{'=' * 55}")
            print(f"Testing role: {role}")
            print(f"Allowed access levels: {allowed_levels}")

            for question in QUESTIONS:
                results = retrieve_chunks(
                    db=db,
                    question=question,
                    user_role=role,
                    limit=5,
                )

                returned_levels = {
                    result["access_level"] for result in results
                }

                # Security assertion: no unauthorized access level
                # may appear in the retrieved results.
                assert returned_levels.issubset(set(allowed_levels)), (
                    f"ACCESS VIOLATION for {role}! "
                    f"Returned: {returned_levels}"
                )

                print(f"\nQuestion: {question}")
                print(f"Chunks returned: {len(results)}")
                print(f"Access levels returned: {returned_levels}")
                print("PASS: all returned chunks are authorized")

    print("\nAll retrieval boundary checks passed!")
if __name__ == "__main__":
    main()