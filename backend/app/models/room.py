from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Room(Base):
    """Modelo de sala da clínica."""
    
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Sala 1, Sala de Pediatria, etc.
    room_number = Column(String(20), unique=True, nullable=False)
    
    # Características
    description = Column(Text, nullable=True)
    equipment = Column(Text, nullable=True)  # Equipamentos disponíveis
    
    # Status
    is_active = Column(Integer, default=1, nullable=False)  # 1 = ativa, 0 = inativa
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    appointments = relationship("Appointment", back_populates="room")
    
    class Config:
        from_attributes = True
