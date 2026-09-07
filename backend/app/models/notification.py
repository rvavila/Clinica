from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Notification(Base):
    """Aviso interno destinado a um usuário da clínica."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False, index=True)
    message = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    recipient = relationship("User")
    appointment = relationship("Appointment")
