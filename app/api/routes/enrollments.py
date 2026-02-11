from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app import crud
from app.api.deps import get_db, get_current_active_user, require_role
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentRead, EnrollmentCreateAdmin



from app.crud.enrollment import enrollment_crud as crud_enrollment
from app.crud.course import crud_course
from app.crud.user import crud_user
from app.api import deps


router = APIRouter()


@router.post("/", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    *,
    db: Session = Depends(get_db),
    enrollment_in: EnrollmentCreate,
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll in courses",
        )

    return crud_enrollment.enroll(
        db=db,
        user_id=current_user.id,
        course_id=enrollment_in.course_id,
    )


@router.post("/admin", response_model=EnrollmentRead)
def enroll_user_as_admin(
    *,
    db: Session = Depends(get_db),
    enrollment_in: EnrollmentCreateAdmin,
    _: User = Depends(require_role("admin")),
):
    return crud_enrollment.enroll(
        db=db,
        user_id=enrollment_in.user_id,
        course_id=enrollment_in.course_id,
    )

@router.get("/me", response_model=list[EnrollmentRead])
def my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "student":
        raise HTTPException(
            status_code=403,
            detail="Only students can view their enrollments",
        )

    return crud_enrollment.get_by_user(
        db,
        user_id=current_user.id,
    )


@router.get("/user/{user_id}", response_model=list[EnrollmentRead])
def enrollments_by_user_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.require_role("admin")) # Only Admins can look up others
):
    # 1. Fetch the user first to check their role
    target_user = crud_user.get(db, id=user_id)
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 2. Check if they are actually a student
    if target_user.role != "student":
        raise HTTPException(
            status_code=400, 
            detail=f"This user is an Admin. Only students have enrollments."
        )

    # 3. If they are a student, proceed to get enrollments
    return crud_enrollment.get_by_user(db, user_id=user_id)

@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentRead,
)
def get_enrollment_by_id(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    enrollment = crud_enrollment.get(db, enrollment_id)

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    if current_user.role != "admin" and enrollment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return enrollment

@router.get(
    "/by-course/{course_id}",
    response_model=list[EnrollmentRead],
)
def get_enrollments_by_course_id(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":

        raise HTTPException(status_code=403, detail="Admin access required")

    return crud_enrollment.get_by_course_id(db, course_id=course_id)



@router.get("/", response_model=list[EnrollmentRead])
def list_all_enrollments(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
    skip: int = 0,
    limit: int = 10,
):
    return crud_enrollment.get_multi(db, skip=skip, limit=limit)

@router.patch("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def deregister_enrollment(
    *,
    db: Session = Depends(get_db),
    enrollment_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    crud_enrollment.deregister(
        db=db,
        enrollment_id=enrollment_id,
        user=current_user,
    )
    return
