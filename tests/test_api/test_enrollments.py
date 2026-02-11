import pytest
from uuid import uuid4
from app.crud.enrollment import enrollment_crud
from app.main import app
from app.api.deps import get_current_user


def test_student_enroll_success(student_client, test_course):
    payload = {"course_id": str(test_course.id)}
    response = student_client.post("/enrollments/", json=payload)
    assert response.status_code == 201
    assert response.json()["course_id"] == str(test_course.id)

def test_enroll_in_inactive_course(student_client, test_course, db):
    test_course.is_active = False
    db.commit()
    
    response = student_client.post("/enrollments/", json={"course_id": str(test_course.id)})
    assert response.status_code == 400
    
    payload = {"course_id": str(test_course.id)}
    response = student_client.post("/enrollments/", json=payload)
    assert response.status_code == 400
    assert "inactive" in response.json()["detail"]

def test_enroll_already_active_fails(student_client, test_course):
    payload = {"course_id": str(test_course.id)}
    
    student_client.post("/enrollments/", json=payload)
    
    response = student_client.post("/enrollments/", json=payload)
    assert response.status_code == 400
    assert "already enrolled" in response.json()["detail"]

def test_admin_enroll_user(admin_client, student_user, test_course):
    payload = {"user_id": str(student_user.id), "course_id": str(test_course.id)}
    response = admin_client.post("/enrollments/admin", json=payload)
    assert response.status_code == 200
    assert response.json()["user_id"] == str(student_user.id)


def test_list_enrollments_by_user_not_student(admin_client, admin_user):
    response = admin_client.get(f"/enrollments/user/{admin_user.id}")
    assert response.status_code == 400
    assert "Only students have enrollments" in response.json()["detail"]

def test_get_enrollments_by_course_student_forbidden(student_client, test_course):
    response = student_client.get(f"/enrollments/by-course/{test_course.id}")
    assert response.status_code == 403

def test_get_my_enrollments_success(student_client, test_course):
    
    student_client.post("/enrollments/", json={"course_id": str(test_course.id)})
    
    response = student_client.get("/enrollments/me")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["course_id"] == str(test_course.id)

def test_my_enrollments_admin_forbidden(admin_client):
    response = admin_client.get("/enrollments/me")
    assert response.status_code == 403


def test_get_enrollment_by_id_owner(student_client, test_course):
    res = student_client.post("/enrollments/", json={"course_id": str(test_course.id)})
    enrollment_id = res.json()["id"]
    
    response = student_client.get(f"/enrollments/{enrollment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == enrollment_id

def test_get_enrollment_by_id_admin(admin_client, student_user, test_course):
    res = admin_client.post("/enrollments/admin", json={
        "user_id": str(student_user.id), "course_id": str(test_course.id)
    })
    enrollment_id = res.json()["id"]
    
    response = admin_client.get(f"/enrollments/{enrollment_id}")
    assert response.status_code == 200

def test_get_enrollments_by_user_id_positive(admin_client, student_user, test_course):
    admin_client.post("/enrollments/admin", json={
        "user_id": str(student_user.id), "course_id": str(test_course.id)
    })
    
    response = admin_client.get(f"/enrollments/user/{student_user.id}")
    assert response.status_code == 200
    assert response.json()[0]["user_id"] == str(student_user.id)

def test_get_enrollments_by_course_id_positive(admin_client, student_user, test_course):
    admin_client.post("/enrollments/admin", json={
        "user_id": str(student_user.id), "course_id": str(test_course.id)
    })
    
    response = admin_client.get(f"/enrollments/by-course/{test_course.id}")
    assert response.status_code == 200
    assert response.json()[0]["course_id"] == str(test_course.id)

def test_deregister_success(student_client, test_course):
    res = student_client.post("/enrollments/", json={"course_id": str(test_course.id)})
    assert res.status_code == 201  
    enrollment_id = res.json()["id"]
    
    response = student_client.patch(f"/enrollments/{enrollment_id}")
    assert response.status_code == 204
    
def test_enrollment_fails_when_course_full(student_client, db, test_course, other_student):
    test_course.capacity = 1
    db.commit()

    enrollment_crud.enroll(
        db=db,
        user_id=other_student.id,
        course_id=test_course.id
    )

    response = student_client.post("/enrollments/", json={"course_id": str(test_course.id)})
    

    assert response.status_code == 400
    assert "Course is full" in response.json()["detail"]