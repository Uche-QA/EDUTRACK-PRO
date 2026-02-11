from uuid import uuid4

def test_list_public_courses(client, test_course):
    response = client.get("/courses/public")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    codes = [course["code"] for course in response.json()]
    assert "CS101" in codes


def test_get_course_by_id_success(client, test_course):
    response = client.get(f"/courses/{test_course.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(test_course.id)
    assert data["title"] == test_course.title
    assert data["code"] == test_course.code

def test_create_course_admin(admin_client):
    data = {"title": "Test Course", "description": "Desc", "code": "T101", "capacity": 20}
    response = admin_client.post("/courses/", json=data)
    assert response.status_code == 201
    assert response.json()["code"] == "T101"

def test_update_course_status_success(admin_client, test_course):
    response = admin_client.patch(
        f"/courses/{test_course.id}/status", 
        json={"is_active": False}
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(test_course.id)


def test_create_course_student_forbidden(student_client):
    data = {"title": "Steal Course", "description": "No", "code": "BAD", "capacity": 1}
    response = student_client.post("/courses/", json=data)
    assert response.status_code == 403

def test_update_course_not_found(admin_client):
    full_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "code": "UPDT101",
        "capacity": 50
    }
    response = admin_client.put(f"/courses/{uuid4()}", json=full_payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"

def test_update_course_success(admin_client, test_course):
    """Test that an admin can fully update a course."""
    payload = {
        "title": "Advanced FastAPI",
        "description": "Mastering asynchronous Python",
        "code": "CS102",
        "capacity": 50
    }
    response = admin_client.put(f"/courses/{test_course.id}", json=payload)
    
    assert response.status_code == 200
    assert response.json()["title"] == "Advanced FastAPI"
    assert response.json()["code"] == "CS102"
    assert response.json()["capacity"] == 50

def test_update_course_not_found_admin(admin_client):
    payload = {
        "title": "Ghost Course",
        "description": "Does not exist",
        "code": "GHOST",
        "capacity": 10
    }
    response = admin_client.put(f"/courses/{uuid4()}", json=payload)
    assert response.status_code == 404

def test_get_course_inactive_returns_404(client, db, test_course):
    test_course.is_active = False
    db.commit()
    
    response = client.get(f"/courses/{test_course.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"