from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    name: str  
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=72,
        description="Password must be between 8 and 72 characters"
    )
    role: str = "student"


class UserUpdateMe(UserBase):
    name: str

class UserUpdateAdmin(UserBase):
    role: Optional[str] = None

class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRead(UserBase):
    id: UUID
    name: str
    email: EmailStr
    role: str
    is_active: bool