from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import func
from app import db
from app.crud import course, user
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.user import User
from app.schemas import enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate
from app.crud.base import CRUDBase
from uuid import UUID


class CRUDEnrollment(CRUDBase[Enrollment, EnrollmentCreate, EnrollmentUpdate]):
    def enroll(
        self,
        db: Session,
        *,
        user_id: UUID,
        course_id: UUID,
    ) -> Enrollment:
        # 1. Check for any existing enrollment (Active or Inactive)
        enrollment = (
            db.query(Enrollment)
            .filter(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
            )
            .first()
        )

        # 2. Check course existence
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # 3. Validation checks
        if not course.is_active:
            raise HTTPException(status_code=400, detail="Course is inactive")

        if self.course_is_full(db, course_id):
            raise HTTPException(status_code=400, detail="Course is full")

        # 4. 🔁 REACTIVATION LOGIC
        if enrollment:
            if enrollment.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already enrolled in this course",
                )
            
            # Reactivate the existing record instead of creating a new one
            enrollment.is_active = True
            enrollment.completed = False  # Reset progress if needed
            db.commit()
            db.refresh(enrollment)
            return enrollment

        # 5. Create new enrollment if no record exists at all
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            is_active=True
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment
    
    def get_by_user(self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Enrollment]:
        return (
            db.query(Enrollment)
            .filter(Enrollment.user_id == user_id)
            .all()
        )
    
    def get_by_course_id(self, db: Session, *, course_id: UUID) -> list[Enrollment]:
        return db.query(self.model).filter(self.model.course_id == course_id).all()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> list[Enrollment]:
        return (
            db.query(Enrollment)
            .offset(skip)
            .limit(limit)
            .all()
    )


    def course_is_full(self, db: Session, course_id: UUID) -> bool:
        enrolled_count = (
            db.query(func.count(Enrollment.id))
            .filter(
                Enrollment.course_id == course_id,
                Enrollment.is_active == True  
            )
            .scalar()
        )

        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return True  

        return enrolled_count >= course.capacity
    
    def deregister(self, db: Session, *, enrollment_id: UUID, user: User) -> None:
        query = db.query(Enrollment).filter(Enrollment.id == enrollment_id)
    
        if user.role != "admin":
            query = query.filter(Enrollment.user_id == user.id)
        
        enrollment = query.first()

        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment record not found.")

        enrollment.is_active = False
        db.commit()

def get_active_enrollments_count(self, db: Session, course_id: UUID) -> int:
    return db.query(func.count(Enrollment.id))\
             .filter(Enrollment.course_id == course_id, Enrollment.is_active == True)\
             .scalar()

enrollment_crud = CRUDEnrollment(Enrollment)