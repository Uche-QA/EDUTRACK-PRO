from typing import Any, Dict
from sqlalchemy.orm import Session


from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, Dict[str, Any]]):
    

    def get_by_email(self, db: Session, *, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate):
        existing = self.get_by_email(db, email=obj_in.email)
        if existing:
            raise ValueError("email_exists")

        db_obj = User(
            name=obj_in.name,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role,
    )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Dict[str, Any],
    ) -> User:
      
        for field, value in obj_in.items():
            if field == "password":
                setattr(db_obj, "hashed_password", get_password_hash(value))
            else:
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(
        self,
        db: Session,
        *,
        user: User,
        is_active: bool,
    ) -> User:
        
        user.is_active = is_active
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


crud_user = CRUDUser(User)

