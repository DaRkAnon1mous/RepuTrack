from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import engine, Base, get_db
from .routers import products

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RepuTrack API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)

@app.get("/")
def read_root():
    return {"message": "RepuTrack API is running!", "docs": "/docs"}

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "db": "connected"}