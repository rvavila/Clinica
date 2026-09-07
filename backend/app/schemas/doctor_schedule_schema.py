from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional


class DoctorScheduleCreate(BaseModel):
    """Schema para criação de agenda do médico."""
    
    doctor_id: int
    day_of_week: int  # 0 = Segunda, 6 = Domingo
    start_time: time
    end_time: time
    interval_minutes: int = 30


class DoctorScheduleUpdate(BaseModel):
    """Schema para atualização de agenda do médico."""
    
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    interval_minutes: Optional[int] = None
    is_active: Optional[int] = None


class DoctorScheduleResponse(BaseModel):
    """Schema de resposta de agenda do médico."""
    
    id: int
    doctor_id: int
    day_of_week: int
    start_time: time
    end_time: time
    interval_minutes: int
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
