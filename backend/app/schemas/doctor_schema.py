from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class DoctorCreate(BaseModel):
    """Schema para criação de médico."""
    
    user_id: int
    crm: str
    specialty: str
    bio: Optional[str] = None
    office_phone: Optional[str] = None
    vacation_start: Optional[datetime] = None
    vacation_end: Optional[datetime] = None
    
    @field_validator("crm")
    def validate_crm(cls, v):
        if len(v) < 4 or len(v) > 20:
            raise ValueError("CRM deve ter entre 4 e 20 caracteres")
        return v.upper()


class DoctorUpdate(BaseModel):
    """Schema para atualização de médico."""

    crm: Optional[str] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    office_phone: Optional[str] = None
    vacation_start: Optional[datetime] = None
    vacation_end: Optional[datetime] = None

    @field_validator("crm")
    def validate_updated_crm(cls, v):
        if len(v) < 4 or len(v) > 20:
            raise ValueError("CRM deve ter entre 4 e 20 caracteres")
        return v.upper()


class DoctorResponse(BaseModel):
    """Schema de resposta de médico."""
    
    id: int
    user_id: int
    crm: str
    specialty: str
    bio: Optional[str]
    office_phone: Optional[str]
    vacation_start: Optional[datetime]
    vacation_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DoctorDetailedResponse(DoctorResponse):
    """Schema de resposta detalhada de médico com informações do usuário."""
    
    full_name: str
    email: str
    phone: Optional[str]
