import pytest
from uuid import uuid4

# --------------------------
# Registration
# --------------------------

def test_register_user_success(client):
    response = client.post(
        "/users/",
        json={
            "email": "new_student@example.com",
            "password": "securepassword",
            "name": "New Student",
            "role": "student",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "new_student@example.com"


def test_register_user_duplicate_email(client, student_user):
    response = client.post(
        "/users/",
        json={
            "email": student_user.email,
            "password": "password",
            "name": "Clone",
            "role": "student",
        },
    )
    assert response.status_code == 400

# --------------------------
# Admin
# --------------------------

def test_list_users_as_admin(admin_client, student_user):
    response = admin_client.get("/users")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_user_by_id_not_found(admin_client):
    response = admin_client.get(f"/users/{uuid4()}")
    assert response.status_code == 404


def test_read_me_admin(admin_client, admin_user):
    response = admin_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["id"] == str(admin_user.id)
    assert response.json()["role"] == "admin"


def test_update_user_status_admin(admin_client, student_user):
    response = admin_client.patch(
        f"/users/{student_user.id}/status",
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_get_user_by_id_success(admin_client, student_user):
    response = admin_client.get(f"/users/{student_user.id}")
    assert response.status_code == 200


def test_admin_update_user_email_conflict(admin_client, admin_user, student_user):
    response = admin_client.patch(
        f"/users/{student_user.id}",
        json={"email": admin_user.email},
    )
    assert response.status_code == 400

# --------------------------
# Student
# --------------------------

def test_list_users_as_student_forbidden(student_client):
    response = student_client.get("/users/")
    assert response.status_code == 403


def test_read_me_student(student_client, student_user):
    response = student_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["id"] == str(student_user.id)


def test_update_user_status_student_forbidden(student_client, admin_user):
    response = student_client.patch(
        f"/users/{admin_user.id}/status",
        json={"is_active": False},
    )
    assert response.status_code == 403


def test_update_me_role_escalation_attempt(student_client):
    response = student_client.patch(
        "/users/me",
        json={"name": "Hacker", "role": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "student"


