# backend/app/routers/products.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List
import app.models as models
import app.schemas as schemas
from database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", response_model=schemas.ProductOut)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Create product
    db_product = models.Product(
        user_id=current_user.id,
        name=product_in.name,
        image_url=product_in.image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  # Now product has an ID

    # Create all links
    for link in product_in.links:
        db_link = models.ProductLink(
            product_id=db_product.id,
            platform=link.platform,
            url=link.url
        )
        db.add(db_link)

    db.commit()  # Save links to DB

    # CRITICAL: Reload product WITH links
    db_product = (
        db.query(models.Product)
        .options(joinedload(models.Product.links))
        .filter(models.Product.id == db_product.id)
        .first()
    )

    return db_product


@router.get("/", response_model=List[schemas.ProductOut])
def get_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    products = (
        db.query(models.Product)
        .options(joinedload(models.Product.links))
        .filter(models.Product.user_id == current_user.id)
        .all()
    )
    return products