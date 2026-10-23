from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import select 
from sqlalchemy.orm import Session


from app.api.deps import require_hr_admin
from app.core.database import get_db
from app.models.entities import User


router = APIRouter(prefix = "/api/admin", tags=["Admin"])

class PendingUserResponse(BaseModel):
    id : int
    email: EmailStr
    role : str 
    account_status : str

    model_config = ConfigDict(from_attributes=True)

class UserApprovalResponse(BaseModel):
    id: int 
    email : EmailStr
    role: str 
    account_status : str 
    message: str 

@router.get("/pending-users", response_model = list[PendingUserResponse])
def get_pending_users(
    current_user : Annotated[User, Depends(require_hr_admin)],
    db : Annotated[Session, Depends(get_db)]

):
    
    stmt = (
        select(User)
        .where(User.account_status == 'pending')
        .order_by(User.id)
    )

    return db.scalars(statement = stmt).all()

def update_pending_user(
        user_id : int,
        new_status: str,
        message: str,
        db: Session,
)-> UserApprovalResponse:
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.account_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user does not have a pending registration.",
        )

    user.account_status = new_status
    db.commit()
    db.refresh(user)

    return UserApprovalResponse(
        id = user.id,
        email = user.email,
        role = user.role,
        account_status= user.account_status,
        message = message
    )

@router.post("/users/{user_id}/approve")
def approve_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_hr_admin)],
    db: Annotated[Session, Depends(get_db)]
):
    return update_pending_user(
        user_id= user_id,
        new_status='active',
        message= "User approved successfully",
        db = db
    )


@router.post("/users/{user_id}/reject")
def reject_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_hr_admin)],
    db: Annotated[Session, Depends(get_db)]
):
    return update_pending_user(
        user_id= user_id,
        new_status='rejected',
        message= "User registeration rejected",
        db = db
    )


