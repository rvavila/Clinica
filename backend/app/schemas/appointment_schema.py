from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.constants import AppointmentStatus, ConsultationType


class AppointmentCreate(BaseModel):
    """Schema para criação de agendamento."""
    
    patient_id: int
    doctor_id: int
    appointment_datetime: datetime
    room_id: Optional[int] = None
    duration_minutes: int = 30
    consultation_type: ConsultationType = ConsultationType.FOLLOW_UP
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    """Schema para atualização de agendamento."""
    
    appointment_datetime: Optional[datetime] = None
    room_id: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    consultation_type: Optional[ConsultationType] = None
    notes: Optional[str] = None
    cancel_reason: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Schema de resposta de agendamento."""
    
    id: int
    patient_id: int
    doctor_id: int
    room_id: Optional[int]
    appointment_datetime: datetime
    duration_minutes: int
    status: AppointmentStatus
    consultation_type: ConsultationType
    notes: Optional[str]
    cancel_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentDetailedResponse(AppointmentResponse):
    """Schema de resposta detalhada com informações do paciente e médico."""
    
    patient_name: str
    doctor_name: str
    doctor_specialty: str
    room_name: Optional[str]
