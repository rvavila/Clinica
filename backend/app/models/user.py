from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.constants import UserRole, UserStatus
from app.db.database import Base


class User(Base):
    """Modelo de usuário."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    
    # Autenticação
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.PATIENT, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relacionamentos
    doctor = relationship("Doctor", back_populates="user", uselist=False)
    patient = relationship("Patient", back_populates="user", uselist=False)
    
    class Config:
        from_attributes = True
