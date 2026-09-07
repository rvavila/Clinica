# CRUD package
from app.crud.user_crud import UserCRUD
from app.crud.doctor_crud import DoctorCRUD
from app.crud.patient_crud import PatientCRUD
from app.crud.appointment_crud import AppointmentCRUD

__all__ = [
    "UserCRUD",
    "DoctorCRUD",
    "PatientCRUD",
    "AppointmentCRUD",
]
