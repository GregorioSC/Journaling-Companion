from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=3)
    age: int
    gender: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    age: int
    gender: str
    last_entry_date: Optional[str] = None  # "YYYY-MM-DD"
    current_streak: int = 0
    longest_streak: int = 0
