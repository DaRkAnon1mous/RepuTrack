# backend/app/routers/products.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import backend.app.models as models
import backend.app.schemas as schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", response_model=schemas.ProductOut)
def create_product(
    product_in: schemas.ProductCreate,
    background_tasks: BackgroundTasks,
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
    db.refresh(db_product)

    # Create all links
    for link in product_in.links:
        # Validate Amazon links
        if "amazon" not in link.url.lower():
            db.rollback()
            raise HTTPException(
                status_code=400, 
                detail="Only Amazon product links are supported for review analysis"
            )
        
        db_link = models.ProductLink(
            product_id=db_product.id,
            platform=link.platform,
            url=link.url
        )
        db.add(db_link)

    db.commit()

    # Trigger immediate scraping in background
    from ..celery_tasks import scrape_single_product
    scrape_single_product.delay(db_product.id)

    # Reload product WITH links
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


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    product = (
        db.query(models.Product)
        .options(joinedload(models.Product.links))
        .filter(
            models.Product.id == product_id,
            models.Product.user_id == current_user.id
        )
        .first()
    )
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.post("/{product_id}/scrape")
def trigger_scrape(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Manually trigger scraping for a product"""
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    from backend.app.celery_tasks import scrape_single_product
    task = scrape_single_product.delay(product_id)
    
    return {"message": "Scraping started", "task_id": task.id}


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}