from pydantic import BaseModel, EmailStr

from pydantic import BaseModel, EmailStr, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password should be at least 8 characters long")
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
