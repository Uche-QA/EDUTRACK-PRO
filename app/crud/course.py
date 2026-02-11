from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_active(self, db: Session) -> list[Course]:
        return (
            db.query(Course)
            .filter(Course.is_active == True)
            .all()
        )
    
    def get_active_paginated(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Course]:
        return (
            db.query(Course)
            .filter(Course.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_code(self, db: Session, code: str):
        return db.query(Course).filter(Course.code == code).first()


crud_course = CRUDCourse(Course)




