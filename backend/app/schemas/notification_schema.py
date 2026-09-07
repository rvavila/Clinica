from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    appointment_id: int
    message: str
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True
