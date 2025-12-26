from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class IngestionPayload(BaseModel):
    venue_id: UUID
    timestamp: datetime
    transaction_count: int

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
