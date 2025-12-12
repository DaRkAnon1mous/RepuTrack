from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv,find_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/app
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")        # backend/.env
load_dotenv(dotenv_path=ENV_PATH)


DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL =", DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}  # Required for Neon
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()