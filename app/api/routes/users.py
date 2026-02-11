from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_active_user, require_role
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdateMe, UserUpdateAdmin, UserRead, UserStatusUpdate
from app.crud.user import crud_user

from app.core.security import get_password_hash

router = APIRouter()

@router.post("/", response_model=UserRead)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
):
    existing_user = crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    user = crud_user.create(db, obj_in=user_in)
    return user

@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
):
    return current_user

@router.get("/", response_model=list[UserRead])
def list_users(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    _: User = Depends(require_role("admin")),
):
    limit = min(limit, 100)  
    return crud_user.get_multi(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/me", response_model=UserRead)
def update_me(
    user_in: UserUpdateMe,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return crud_user.update(
        db,
        db_obj=current_user,
        obj_in=user_in.model_dump(exclude_unset=True),
    )

@router.patch("/{user_id}", response_model=UserRead)
def admin_update_user(
    user_id: UUID,
    user_in: UserUpdateAdmin,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.email:
        existing_user = crud_user.get_by_email(db, email=user_in.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists."
            )

    return crud_user.update(
        db,
        db_obj=user,
        obj_in=user_in.model_dump(exclude_unset=True),
    )


@router.patch("/{user_id}/status", response_model=UserRead, status_code=status.HTTP_200_OK,)
def update_user_status(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    status_in: UserStatusUpdate,
    _: dict = Depends(require_role("admin")),
):
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud_user.update_status(
        db,
        user=user,
        is_active=status_in.is_active,
    )
