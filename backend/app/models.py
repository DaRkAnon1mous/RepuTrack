# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import text
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True, nullable=False)  # from Clerk
    email = Column(String, nullable=False)
    name = Column(String)

    products = relationship("Product", back_populates="owner")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())"))

    owner = relationship("User", back_populates="products")
    links = relationship("ProductLink", back_populates="product", cascade="all, delete-orphan")


class ProductLink(Base):
    __tablename__ = "product_links"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String, nullable=False)        # amazon, flipkart, myntra, etc.
    url = Column(String, nullable=False)
    last_rating = Column(Float, nullable=True)
    last_scraped = Column(DateTime(timezone=True), nullable=True)
    fake_ratio = Column(Float, default=0.0)

    product = relationship("Product", back_populates="links")