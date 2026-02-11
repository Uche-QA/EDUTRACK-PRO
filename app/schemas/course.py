from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class CourseBase(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = None
    
    
    model_config = ConfigDict(from_attributes=True)

class CourseCreate(CourseBase):
    title: str
    code: str
    capacity: int

class CourseUpdate(CourseBase):
    is_active: Optional[bool] = None

class CourseRead(CourseBase):
    id: UUID
    is_active: bool

class CourseStatusUpdate(BaseModel):
    is_active: bool


    
