from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.db_models import Occasion, Relationship, Interest, Personality
from backend.app.schemas.lookup import LookupsResponse, LookupItem

router = APIRouter(prefix="/lookups", tags=["lookups"])

@router.get("", response_model=LookupsResponse)
def get_lookups(db: Session = Depends(get_db)):
    occasions = db.query(Occasion).order_by(Occasion.name).all()
    relationships = db.query(Relationship).order_by(Relationship.name).all()
    interests = db.query(Interest).order_by(Interest.name).all()
    personalities = db.query(Personality).order_by(Personality.name).all()

    return LookupsResponse(
        occasions=[LookupItem(id=o.id, name=o.name) for o in occasions],
        relationships=[LookupItem(id=r.id, name=r.name) for r in relationships],
        interests=[LookupItem(id=i.id, name=i.name) for i in interests],
        personalities=[LookupItem(id=p.id, name=p.name) for p in personalities]
    )
