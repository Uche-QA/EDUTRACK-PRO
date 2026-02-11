from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

# 1. THE FOUNDATION
class EnrollmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# 2. CREATE
class EnrollmentCreate(EnrollmentBase):
    course_id: UUID

class EnrollmentCreateAdmin(EnrollmentBase):
    user_id: UUID
    course_id: UUID

# 3. UPDATE
class EnrollmentUpdate(EnrollmentBase):
    completed: Optional[bool] = None
    is_active: Optional[bool] = None

# 4. READ
class EnrollmentRead(EnrollmentBase):
    id: UUID
    user_id: UUID
    course_id: UUID
    completed: bool
    is_active: bool
    created_at: datetime

class EnrollmentStatusRead(EnrollmentBase):
    id: UUID
    is_active: bool

