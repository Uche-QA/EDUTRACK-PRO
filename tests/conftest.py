import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.db.base import Base

from app.core.security import create_access_token
from app.schemas.user import UserCreate
from app.crud.user import crud_user
from app.schemas.course import CourseCreate
from app.crud.course import crud_course
from app.crud.enrollment import enrollment_crud as crud_enrollment

# -----------------------
# Database setup
# -----------------------
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_TEST_URL",
    "postgresql://postgres:test@localhost:5432/edutrack_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# -----------------------
# Base client
# -----------------------
@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# -----------------------
# Users
# -----------------------
@pytest.fixture
def test_password():
    return "testpass123"

@pytest.fixture
def admin_user(db, test_password):
    user = crud_user.get_by_email(db, email="admin@example.com")
    if not user:
        user = crud_user.create(
            db=db,
            obj_in=UserCreate(
                email="admin@example.com",
                password=test_password,
                name="Admin",
                role="admin",
            ),
        )
    return user

@pytest.fixture
def student_user(db, test_password):
    user = crud_user.get_by_email(db, email="student@example.com")
    if not user:
        user = crud_user.create(
            db=db,
            obj_in=UserCreate(
                email="student@example.com",
                password=test_password,
                name="Student",
                role="student",
            ),
        )
    return user

@pytest.fixture
def other_student(db, test_password):
    """Creates a second student for unauthorized access tests."""
    return crud_user.create(
        db=db,
        obj_in=UserCreate(
            email="other_student@example.com",
            password=test_password,
            name="Other Student",
            role="student",
        ),
    )


# -----------------------
# Tokens
# -----------------------
@pytest.fixture
def admin_token(admin_user):
    return create_access_token(subject=str(admin_user.id))

@pytest.fixture
def student_token(student_user):
    return create_access_token(subject=str(student_user.id))

# -----------------------
# Authenticated clients
# -----------------------
@pytest.fixture
def admin_client(client, admin_token):
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client

@pytest.fixture
def student_client(client, student_user):
    from app.core.security import create_access_token

    token = create_access_token(subject=str(student_user.id))
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    client.headers.clear()


@pytest.fixture
def other_student_client(client, other_student):
    from app.core.security import create_access_token

    token = create_access_token(subject=str(other_student.id))
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    client.headers.clear()


# -----------------------
# Course & Enrollment
# -----------------------
@pytest.fixture
def test_course(db):
    course = CourseCreate(
        title="Intro to CS",
        description="Basics",
        code="CS101",
        capacity=30,
    )
    return crud_course.create(db=db, obj_in=course)


@pytest.fixture
def test_enrollment(db, student_user, test_course):
    return crud_enrollment.enroll(
        db=db,
        user_id=student_user.id,
        course_id=test_course.id,
    )
