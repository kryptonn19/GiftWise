from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.models.db_models import Gift
from backend.app.schemas.gift import GiftCreate, GiftResponse

router = APIRouter(prefix="/gifts", tags=["gifts"])

@router.get("", response_model=List[GiftResponse])
def list_gifts(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_personalized: Optional[bool] = None,
    is_experience: Optional[bool] = None,
    is_handmade: Optional[bool] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Gift)
    if category:
        query = query.filter(Gift.category == category)
    if min_price is not None:
        query = query.filter(Gift.typical_price_max >= min_price)
    if max_price is not None:
        query = query.filter(Gift.typical_price_min <= max_price)
    if is_personalized is not None:
        query = query.filter(Gift.is_personalized == is_personalized)
    if is_experience is not None:
        query = query.filter(Gift.is_experience == is_experience)
    if is_handmade is not None:
        query = query.filter(Gift.is_handmade == is_handmade)

    gifts = query.order_by(Gift.name).offset(offset).limit(limit).all()
    return gifts

@router.post("", response_model=GiftResponse, status_code=201)
def create_gift(gift_in: GiftCreate, db: Session = Depends(get_db)):
    gift = Gift(**gift_in.model_dump())
    db.add(gift)
    db.commit()
    db.refresh(gift)
    return gift

@router.get("/{gift_id}", response_model=GiftResponse)
def get_gift(gift_id: str, db: Session = Depends(get_db)):
    gift = db.query(Gift).filter(Gift.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    return gift
