from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Float, Text
from sqlalchemy.orm import relationship

from app.core.constants import PaymentStatus
from app.db.database import Base


class Payment(Base):
    """Modelo de pagamento."""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    # Informações de pagamento
    amount = Column(Float, nullable=False)  # Valor em reais
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(String(50), nullable=False)  # creditcard, debitcard, pix, cash, insurance
    
    # Referência da transação
    transaction_id = Column(String(100), nullable=True)  # ID da transação no gateway
    receipt_number = Column(String(50), unique=True, nullable=True)
    
    # Datas
    due_date = Column(DateTime, nullable=True)  # Data de vencimento
    payment_date = Column(DateTime, nullable=True)  # Data do pagamento
    
    # Notas
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", back_populates="payments")
    appointment = relationship("Appointment", back_populates="payment")
    
    class Config:
        from_attributes = True
