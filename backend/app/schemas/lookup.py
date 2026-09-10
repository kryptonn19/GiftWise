from pydantic import BaseModel, ConfigDict
from typing import List

class LookupItem(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class LookupsResponse(BaseModel):
    occasions: List[LookupItem]
    relationships: List[LookupItem]
    interests: List[LookupItem]
    personalities: List[LookupItem]
