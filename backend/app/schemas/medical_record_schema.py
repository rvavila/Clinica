from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MedicalRecordCreate(BaseModel):
    """Schema para criação de prontuário."""
    
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    chief_complaint: str
    history_of_present_illness: Optional[str] = None
    physical_examination: Optional[str] = None
    diagnosis: str
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    prescription: Optional[str] = None
    medical_certificate: Optional[str] = None
    referral: Optional[str] = None


class MedicalRecordUpdate(BaseModel):
    """Schema para atualização de prontuário."""
    
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    physical_examination: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    prescription: Optional[str] = None
    medical_certificate: Optional[str] = None
    referral: Optional[str] = None


class MedicalRecordResponse(BaseModel):
    """Schema de resposta de prontuário."""
    
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    chief_complaint: str
    history_of_present_illness: Optional[str]
    physical_examination: Optional[str]
    diagnosis: str
    treatment_plan: Optional[str]
    notes: Optional[str]
    prescription: Optional[str]
    medical_certificate: Optional[str]
    referral: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PatientPrescriptionResponse(BaseModel):
    """Únicos dados clínicos que podem ser visualizados pelo paciente."""

    id: int
    patient_id: int
    appointment_id: Optional[int]
    prescription: Optional[str]
    created_at: datetime
    updated_at: datetime
