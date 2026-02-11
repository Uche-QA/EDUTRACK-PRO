from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role, get_current_active_user
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, CourseRead, CourseStatusUpdate

from app.crud.course import crud_course
from fastapi import Query
from typing import List



router = APIRouter()

@router.get("/public", response_model=List[CourseRead])
def list_active_courses(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    return crud_course.get_active_paginated(
        db=db,
        skip=skip,
        limit=limit,
    )

@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: UUID,
    db: Session = Depends(get_db),
):
    course = crud_course.get(db, id=course_id)

    if not course or not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course

@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    *,
    db: Session = Depends(get_db),
    course_in: CourseCreate,
    _: User = Depends(require_role("admin")),
):
    return crud_course.create(db, obj_in=course_in)

@router.put("/{course_id}", response_model=CourseRead)
def update_course(
    *,
    db: Session = Depends(get_db),
    course_id: UUID,
    course_in: CourseUpdate,
    _: User = Depends(require_role("admin")),
):
    course = crud_course.get(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return crud_course.update(db, db_obj=course, obj_in=course_in)


@router.patch("/{course_id}/status", response_model=CourseRead)
def update_course_status(
    *,
    db: Session = Depends(get_db),
    course_id: UUID,
    status_in: CourseStatusUpdate,
    _: User = Depends(require_role("admin")),
):
    course = crud_course.get(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.is_active == status_in.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course already in requested state",
        )

    course.is_active = status_in.is_active
    db.commit()
    db.refresh(course)
    return course

