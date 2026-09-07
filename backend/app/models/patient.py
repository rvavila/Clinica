from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship

from app.db.database import Base


class Patient(Base):
    """Modelo de paciente."""
    
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Informações pessoais
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)  # Masculino, Feminino, Outro
    
    # Endereço
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)
    
    # Informações médicas
    blood_type = Column(String(5), nullable=True)
    allergies = Column(Text, nullable=True)
    medical_conditions = Column(Text, nullable=True)  # Condições médicas conhecidas
    
    # Responsável (para pediatria)
    responsible_name = Column(String(255), nullable=True)
    responsible_phone = Column(String(20), nullable=True)
    responsible_cpf = Column(String(11), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    payments = relationship("Payment", back_populates="patient")
    
    class Config:
        from_attributes = True
