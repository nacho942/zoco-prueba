from datetime import datetime
from pydantic import BaseModel

class PlaceBase(BaseModel):
    name: str
    location: str
    category: str | None = None
    source: str | None = "manual"

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    category: str | None = None
    is_active: bool | None = None

class Place(PlaceBase):
    id: int
    obtained_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
