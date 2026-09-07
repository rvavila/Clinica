from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from app.schemas.user_schema import UserCreate


class PatientRegistrationCreate(UserCreate):
    """Dados de acesso e perfil usados pela recepção para cadastrar paciente."""

    date_of_birth: Optional[date] = None
    gender: Optional[str] = None


class PatientCreate(BaseModel):
    """Schema para criação de paciente."""
    
    user_id: int
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None  # Masculino, Feminino, Outro
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    responsible_name: Optional[str] = None  # Para pediatria
    responsible_phone: Optional[str] = None
    responsible_cpf: Optional[str] = None


class PatientUpdate(BaseModel):
    """Schema para atualização de paciente."""
    
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    responsible_name: Optional[str] = None
    responsible_phone: Optional[str] = None
    responsible_cpf: Optional[str] = None


class PatientResponse(BaseModel):
    """Schema de resposta de paciente."""
    
    id: int
    user_id: int
    date_of_birth: Optional[date]
    gender: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    blood_type: Optional[str]
    allergies: Optional[str]
    medical_conditions: Optional[str]
    responsible_name: Optional[str]
    responsible_phone: Optional[str]
    responsible_cpf: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PatientDetailedResponse(PatientResponse):
    """Schema de resposta detalhada com informações do usuário."""
    
    full_name: str
    email: str
    phone: Optional[str]
    cpf: str
