from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.category import Category, CategoryCreate
from app.models.category import Category as CategoryModel

router = APIRouter()


@router.get("/", response_model=List[Category])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(CategoryModel).all()
    return categories


@router.get("/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID"""
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/slug/{slug}", response_model=Category)
def get_category_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a category by slug"""
    category = db.query(CategoryModel).filter(CategoryModel.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=Category, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category (admin function)"""
    # Check if category with same slug exists
    existing = db.query(CategoryModel).filter(CategoryModel.slug == category.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this slug already exists")

    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category
