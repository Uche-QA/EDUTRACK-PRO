import pytest
from fastapi.testclient import TestClient
from uuid import UUID


def test_login_success(client, student_user, test_password):
    response = client.post(
        "/auth/login",
        data={
            "username": student_user.email,
            "password": test_password,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, student_user):
    response = client.post(
        "/auth/login",
        data={"username": student_user.email, "password": "wrongpass"},
    )

    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_email(client):
    response = client.post(
        "/auth/login",
        data={"username": "notfound@example.com", "password": "pass12345"},
    )

    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_inactive_user(client, db, student_user):
    student_user.is_active = False
    db.commit()

    response = client.post(
        "/auth/login",
        data={"username": student_user.email, "password": "testpass123"},
    )

    assert response.status_code == 403
    assert "Inactive user" in response.json()["detail"]

    
    student_user.is_active = True
    db.commit()


def test_refresh_token_success(client, student_token):
    payload = {"refresh_token": student_token}
    response = client.post("/auth/refresh", json=payload)
    
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_invalid(client):
    payload = {"refresh_token": "invalidtoken"}
    response = client.post("/auth/refresh", json=payload)
    
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]