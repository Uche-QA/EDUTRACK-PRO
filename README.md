# EDUTRACK PRO

A comprehensive educational management system built with FastAPI, featuring course management, user enrollment, and role-based access control.

## Overview

EDUTRACK PRO is a modern web application designed to streamline educational operations including:
- **User Management**: Registration, authentication, and role-based authorization (admin/student)
- **Course Management**: Create, update, and manage courses with capacity limits
- **Enrollment System**: Students can enroll in courses with validation and conflict prevention
- **Security**: JWT-based authentication with password hashing and access control

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens with password hashing
- **Testing**: pytest
- **Database Migrations**: Alembic

## Project Structure

```
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── deps.py            # Dependency injection
│   │   └── routes/            # API endpoints
│   ├── core/                  # Core configurations
│   ├── crud/                  # Database operations
│   ├── db/                    # Database configuration
│   ├── models/                # SQLAlchemy models
│   └── schemas/               # Pydantic schemas
├── tests/
│   ├── conftest.py            # pytest fixtures and configuration
│   └── test_api/              # API endpoint tests
├── alembic/                   # Database migrations
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration
└── alembic.ini               # Alembic configuration
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip or poetry

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd edutrack-pro
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venvv
   source venvv/bin/activate  # On Windows: venvv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token

### Users
- `POST /api/users/register` - Register new user
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile
- `GET /api/users/{id}` - Get user by ID (admin only)
- `PUT /api/users/{id}` - Update user (admin only)

### Courses
- `POST /api/courses` - Create course (admin only)
- `GET /api/courses` - List all active courses
- `GET /api/courses/{id}` - Get course details
- `PUT /api/courses/{id}` - Update course (admin only)

### Enrollments
- `POST /api/enrollments` - Enroll in course (students)
- `POST /api/enrollments/admin` - Admin enroll user
- `GET /api/enrollments/{id}` - Get enrollment details
- `GET /api/enrollments/course/{course_id}` - List course enrollments
- `GET /api/enrollments/user/{user_id}` - List user enrollments
- `DELETE /api/enrollments/{id}` - Deregister from course

## Testing

Make sure your virtual environment is activated before running tests.

Run the test suite:

```bash
python -m pytest
```

Run tests with coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Run specific test file:

```bash
python -m pytest tests/test_api/test_auth.py -v

```

### Test Database

Tests use a separate PostgreSQL database configured in [tests/conftest.py](tests/conftest.py). Update `DATABASE_TEST_URL` in the conftest file to match your test database credentials.

## Live Demo

You can access the deployed FastAPI application here:

- **Application URL:** [My FastAPI App](https://edutrack-pro.onrender.com/)
- **Swagger UI (Interactive API docs):** [Swagger Docs](https://edutrack-pro.onrender.com/docs)
- **ReDoc (API documentation):** [ReDoc Docs](https://edutrack-pro.onrender.com/redoc)


### Create new migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Revert to previous migration
```bash
alembic downgrade -1
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/edutrack
DATABASE_TEST_URL=postgresql://postgres:password@localhost:5432/edutrack_test

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
```

## Features

### Role-Based Access Control
- **Admin**: Full system access (manage users, courses, enrollments)
- **Student**: Can enroll/deregister from courses, view own profile

### Enrollment Validation
- Prevents duplicate enrollments
- Validates course capacity
- Checks course and user active status
- Prevents enrollment in inactive courses

### Database Features
- **Performance Indexes**: Optimized queries for common operations
- **Active Status Tracking**: Soft delete support for users and courses
- **Audit Trail**: Track enrollment status changes

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
