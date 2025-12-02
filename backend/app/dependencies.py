# backend/app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .database import get_db
import app.models as models
import os

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            os.getenv("CLERK_SECRET_KEY"),
            algorithms=["HS256"],
            issuer=os.getenv("CLERK_ISSUER"),
            options={"verify_aud": False}
        )
        clerk_id: str = payload.get("sub")
        if clerk_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


    user = db.query(models.User).filter(models.User.clerk_id == clerk_id).first()
    if user is None:
        # Auto-create user on first login
        user = models.User(clerk_id=clerk_id, email=payload.get("email", "unknown"), name=payload.get("name", "User"))
        db.add(user)
        db.commit()
        db.refresh(user)
    return user