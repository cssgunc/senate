from typing import Optional
from pydantic import BaseModel, EmailStr

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str
    senator_id: Optional[int] = None

class ContactResponse(BaseModel):
    success: bool
