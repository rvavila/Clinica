from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.constants import PaymentStatus


class PaymentCreate(BaseModel):
    """Schema para criação de pagamento."""
    
    patient_id: int
    appointment_id: Optional[int] = None
    amount: float
    payment_method: str  # creditcard, debitcard, pix, cash, insurance
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentUpdate(BaseModel):
    """Schema para atualização de pagamento."""
    
    status: Optional[PaymentStatus] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """Schema de resposta de pagamento."""
    
    id: int
    patient_id: int
    appointment_id: Optional[int]
    amount: float
    status: PaymentStatus
    payment_method: str
    transaction_id: Optional[str]
    receipt_number: Optional[str]
    due_date: Optional[datetime]
    payment_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
