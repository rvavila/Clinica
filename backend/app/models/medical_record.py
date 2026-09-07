from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class MedicalRecord(Base):
    """Modelo de prontuário eletrônico (PEP)."""
    
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, unique=True)
    
    # Conteúdo do prontuário
    chief_complaint = Column(Text, nullable=False)  # Queixa principal
    history_of_present_illness = Column(Text, nullable=True)  # Histórico da doença atual
    physical_examination = Column(Text, nullable=True)  # Exame físico
    diagnosis = Column(Text, nullable=False)  # Diagnóstico
    treatment_plan = Column(Text, nullable=True)  # Plano de tratamento
    notes = Column(Text, nullable=True)  # Notas adicionais
    
    # Prescrições e recomendações
    prescription = Column(Text, nullable=True)  # Prescrição de medicamentos
    medical_certificate = Column(Text, nullable=True)  # Atestado médico
    referral = Column(Text, nullable=True)  # Encaminhamento para outro especialista
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")
    appointment = relationship("Appointment", back_populates="medical_record")
    
    class Config:
        from_attributes = True
