from enum import Enum


class UserRole(str, Enum):
    """Roles de usuário no sistema."""
    
    ADMIN = "admin"              # Administrador da clínica
    DOCTOR = "doctor"            # Médico
    RECEPTION = "reception"      # Recepção
    PATIENT = "patient"          # Paciente/Cliente


class UserStatus(str, Enum):
    """Status do usuário."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class AppointmentStatus(str, Enum):
    """Status do agendamento."""
    
    SCHEDULED = "scheduled"      # Agendado
    CONFIRMED = "confirmed"      # Confirmado
    IN_PROGRESS = "in_progress"  # Em atendimento
    COMPLETED = "completed"      # Concluído
    CANCELLED = "cancelled"      # Cancelado
    NO_SHOW = "no_show"         # Paciente não compareceu


class PaymentStatus(str, Enum):
    """Status do pagamento."""
    
    PENDING = "pending"          # Pendente
    PAID = "paid"               # Pago
    CANCELLED = "cancelled"      # Cancelado
    REFUNDED = "refunded"        # Reembolsado


class ConsultationType(str, Enum):
    """Tipos de consulta."""
    
    FIRST_VISIT = "first_visit"    # Primeira consulta
    FOLLOW_UP = "follow_up"        # Retorno/Acompanhamento
    EMERGENCY = "emergency"        # Emergência
    PROCEDURE = "procedure"        # Procedimento


# Especialidades médicas
MEDICAL_SPECIALTIES = [
    "Pediatria",
    "Cardiologia",
    "Dermatologia",
    "Ortopedia",
    "Oftalmologia",
    "Otorrinolaringologia",
    "Pneumologia",
    "Gastroenterologia",
    "Ginecologia",
    "Medicina Geral",
]
