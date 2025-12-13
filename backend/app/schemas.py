# backend/app/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
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
    last_rating: Optional[float] = None
    fake_ratio: Optional[float] = None
    sentiment_score: Optional[float] = None
    last_scraped: Optional[datetime] = None  
    scrape_note: Optional[str] = None  
    reviews_json: Optional[List[Dict[str, Any]]] = None  

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