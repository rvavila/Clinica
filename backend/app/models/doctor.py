from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Doctor(Base):
    """Modelo de médico."""
    
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    crm = Column(String(20), unique=True, index=True, nullable=False)  # Conselho Regional de Medicina
    specialty = Column(String(100), nullable=False)  # Especialidade
    bio = Column(Text, nullable=True)  # Biografia/Descrição
    
    # Contato profissional
    office_phone = Column(String(20), nullable=True)

    # Período de férias/indisponibilidade programada.
    vacation_start = Column(DateTime, nullable=True)
    vacation_end = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    medical_records = relationship("MedicalRecord", back_populates="doctor")
    doctor_schedules = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan")
    
    class Config:
        from_attributes = True
