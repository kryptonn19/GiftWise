from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class GiftBase(BaseModel):
    name: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    description: Optional[str] = None
    typical_price_min: float = Field(..., ge=0)
    typical_price_max: float = Field(..., ge=0)
    is_personalized: bool = False
    is_experience: bool = False
    is_handmade: bool = False

class GiftCreate(GiftBase):
    pass

class GiftResponse(GiftBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
