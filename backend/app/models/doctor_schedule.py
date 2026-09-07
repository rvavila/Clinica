from datetime import datetime, time
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship

from app.db.database import Base


class DoctorSchedule(Base):
    """Modelo de agenda/disponibilidade do médico."""
    
    __tablename__ = "doctor_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    
    # Dia da semana (0 = Segunda, 6 = Domingo)
    day_of_week = Column(Integer, nullable=False)
    
    # Horários
    start_time = Column(Time, nullable=False)  # Ex: 08:00
    end_time = Column(Time, nullable=False)    # Ex: 12:00
    
    # Intervalo entre consultas (em minutos)
    interval_minutes = Column(Integer, default=30, nullable=False)
    
    # Status
    is_active = Column(Integer, default=1, nullable=False)  # 1 = ativo, 0 = inativo
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    doctor = relationship("Doctor", back_populates="doctor_schedules")
    
    class Config:
        from_attributes = True
