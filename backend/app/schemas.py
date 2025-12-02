# backend/app/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ProductLinkCreate(BaseModel):
    platform: str
    url: str

class ProductCreate(BaseModel):
    name: str
    image_url: Optional[str] = None
    links: List[ProductLinkCreate]

class ProductLinkOut(BaseModel):
    id: int
    platform: str
    url: str
    last_rating: Optional[float]
    fake_ratio: float

    class Config:
        from_attributes = True

class ProductOut(BaseModel):
    id: int
    name: str
    image_url: Optional[str]
    created_at: datetime
    links: List[ProductLinkOut]

    class Config:
        from_attributes = True