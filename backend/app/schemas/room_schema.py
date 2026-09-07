from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RoomCreate(BaseModel):
    """Schema para criação de sala."""
    
    name: str
    room_number: str
    description: Optional[str] = None
    equipment: Optional[str] = None


class RoomUpdate(BaseModel):
    """Schema para atualização de sala."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    equipment: Optional[str] = None
    is_active: Optional[int] = None


class RoomResponse(BaseModel):
    """Schema de resposta de sala."""
    
    id: int
    name: str
    room_number: str
    description: Optional[str]
    equipment: Optional[str]
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
