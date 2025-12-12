# backend/app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .database import get_db
import backend.app.models as models
import os
import requests

bearer_scheme = HTTPBearer()

# Cache for JWKS
_jwks_cache = None

def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        jwks_url = f"{os.getenv('CLERK_ISSUER')}/.well-known/jwks.json"
        response = requests.get(jwks_url)
        _jwks_cache = response.json()
    return _jwks_cache

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        # Get the JWKS (public keys)
        jwks = get_jwks()
        
        # Decode the token header to get the key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        # Find the right key
        rsa_key = None
        for key in jwks["keys"]:
            if key["kid"] == kid:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if rsa_key is None:
            raise HTTPException(status_code=401, detail="Invalid token - key not found")
        
        # Verify and decode the token with RS256
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=os.getenv("CLERK_ISSUER"),
            options={"verify_aud": False}
        )
        
        clerk_id: str = payload.get("sub")
        if clerk_id is None:
            raise HTTPException(status_code=401, detail="Invalid token - no subject")
            
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

    user = db.query(models.User).filter(models.User.clerk_id == clerk_id).first()
    if user is None:
        # Auto-create user on first login
        user = models.User(
            clerk_id=clerk_id, 
            email=payload.get("email", "unknown"), 
            name=payload.get("name", "User")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user