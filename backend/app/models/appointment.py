from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, Float
from sqlalchemy.orm import relationship

from app.core.constants import AppointmentStatus, ConsultationType
from app.db.database import Base


class Appointment(Base):
    """Modelo de agendamento."""
    
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    
    # Data e hora
    appointment_datetime = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=30, nullable=False)  # Duração em minutos
    
    # Status e tipo
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    consultation_type = Column(SQLEnum(ConsultationType), default=ConsultationType.FOLLOW_UP, nullable=False)
    
    # Observações
    notes = Column(Text, nullable=True)  # Notas da recepção
    cancel_reason = Column(String(255), nullable=True)  # Motivo do cancelamento
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    room = relationship("Room", back_populates="appointments")
    payment = relationship("Payment", back_populates="appointment", uselist=False)
    medical_record = relationship("MedicalRecord", back_populates="appointment", uselist=False)
    
    class Config:
        from_attributes = True
