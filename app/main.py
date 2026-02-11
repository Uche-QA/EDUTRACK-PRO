from fastapi import FastAPI

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

from app.api.routes import users, courses, enrollments, auth

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["Enrollments"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
