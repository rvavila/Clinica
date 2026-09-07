# Schemas package
from app.schemas.user_schema import (
    UserCreate, UserUpdate, PasswordReset, UserResponse, UserLoginRequest, TokenResponse
)
from app.schemas.doctor_schema import (
    DoctorCreate, DoctorUpdate, DoctorResponse, DoctorDetailedResponse
)
from app.schemas.patient_schema import (
    PatientRegistrationCreate, PatientCreate, PatientUpdate, PatientResponse, PatientDetailedResponse
)
from app.schemas.appointment_schema import (
    AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentDetailedResponse
)
from app.schemas.medical_record_schema import (
    MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
)
from app.schemas.payment_schema import (
    PaymentCreate, PaymentUpdate, PaymentResponse
)
from app.schemas.room_schema import (
    RoomCreate, RoomUpdate, RoomResponse
)
from app.schemas.doctor_schedule_schema import (
    DoctorScheduleCreate, DoctorScheduleUpdate, DoctorScheduleResponse
)
from app.schemas.notification_schema import NotificationResponse

__all__ = [
    # User
    "UserCreate", "UserUpdate", "PasswordReset", "UserResponse", "UserLoginRequest", "TokenResponse",
    # Doctor
    "DoctorCreate", "DoctorUpdate", "DoctorResponse", "DoctorDetailedResponse",
    # Patient
    "PatientRegistrationCreate", "PatientCreate", "PatientUpdate", "PatientResponse", "PatientDetailedResponse",
    # Appointment
    "AppointmentCreate", "AppointmentUpdate", "AppointmentResponse", "AppointmentDetailedResponse",
    # Medical Record
    "MedicalRecordCreate", "MedicalRecordUpdate", "MedicalRecordResponse",
    # Payment
    "PaymentCreate", "PaymentUpdate", "PaymentResponse",
    # Room
    "RoomCreate", "RoomUpdate", "RoomResponse",
    # Doctor Schedule
    "DoctorScheduleCreate", "DoctorScheduleUpdate", "DoctorScheduleResponse",
    # Notifications
    "NotificationResponse",
]
