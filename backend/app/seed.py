from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.entities import User

DEMO_USERS = [
    {
        "email": "employee@demo.com",
        "password": "EmployeeDemo123!",
        "role": "employee",
    },
    {
        "email": "manager@demo.com",
        "password": "ManagerDemo123!",
        "role": "manager",
    },
    {
        "email": "hr@demo.com",
        "password": "HrAdminDemo123!",
        "role": "hr_admin",
    },
]


def seed_users():
    with SessionLocal() as db:
        for account in DEMO_USERS:
            existing_user = db.scalar(
                select(User).where(
                    User.email == account['email']
                )
            )

            if existing_user:
                print(f"User already exists: {account['email']}")

            user = User(
                email = account["email"],
                password_hash = hash_password(account['password']),
                role = account['role']
            )

            db.add(user)

        db.commit()
        print("Demo users seeded successfully")


if __name__ == "__main__":
    seed_users()