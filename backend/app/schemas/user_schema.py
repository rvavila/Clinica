from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional

from app.core.constants import UserRole, UserStatus


class UserCreate(BaseModel):
    """Schema para criação de usuário."""
    
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    cpf: str
    password: str
    role: UserRole = UserRole.PATIENT
    
    @field_validator("cpf")
    def validate_cpf(cls, v):
        # Remove caracteres não numéricos
        cpf = "".join(filter(str.isdigit, v))
        
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        
        # Verificação básica de CPF (simplificada)
        if cpf == cpf[0] * 11:
            raise ValueError("CPF inválido")
        
        return cpf
    
    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres")
        return v


class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    status: Optional[UserStatus] = None

    @field_validator("cpf")
    def validate_updated_cpf(cls, v):
        cpf = "".join(filter(str.isdigit, v))
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            raise ValueError("CPF deve ter 11 dígitos válidos")
        return cpf


class PasswordReset(BaseModel):
    """Nova senha definida pela recepção ou administração."""

    password: str

    @field_validator("password")
    def validate_reset_password(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres")
        return v


class UserResponse(BaseModel):
    """Schema de resposta de usuário."""
    
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    cpf: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    """Schema para login."""
    
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema de resposta de token."""
    
    access_token: str
    token_type: str
    user: UserResponse
