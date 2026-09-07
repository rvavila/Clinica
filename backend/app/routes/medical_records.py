from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.constants import UserRole, AppointmentStatus
from app.core.security import get_current_user
from app.crud import DoctorCRUD, PatientCRUD
from app.db.database import get_db
from app.models.medical_record import MedicalRecord
from app.models.appointment import Appointment
from app.schemas.medical_record_schema import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse, PatientPrescriptionResponse

router = APIRouter(prefix="/api/medical-records", tags=["medical-records"])


def _can_access(record, current_user, db):
    if current_user["role"] == UserRole.ADMIN.value:
        return True
    patient = PatientCRUD.get_by_id(db, record.patient_id)
    doctor = DoctorCRUD.get_by_id(db, record.doctor_id)
    return (
        current_user["role"] == UserRole.PATIENT.value and patient and patient.user_id == current_user["user_id"]
    ) or (
        current_user["role"] == UserRole.DOCTOR.value and doctor and doctor.user_id == current_user["user_id"]
    )


@router.get("/", response_model=list[MedicalRecordResponse | PatientPrescriptionResponse])
async def list_medical_records(
    appointment_id: int | None = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user["role"] == UserRole.RECEPTION.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A recepção não possui acesso aos laudos.")
    records = db.query(MedicalRecord).outerjoin(Appointment).filter(
        (MedicalRecord.appointment_id.is_(None)) | (Appointment.status != AppointmentStatus.CANCELLED)
    )
    if appointment_id:
        records = records.filter(MedicalRecord.appointment_id == appointment_id)
    if current_user["role"] == UserRole.PATIENT.value:
        patient = PatientCRUD.get_by_user_id(db, current_user["user_id"])
        records = records.filter(MedicalRecord.patient_id == patient.id if patient else False)
        return [
            PatientPrescriptionResponse(
                id=record.id,
                patient_id=record.patient_id,
                appointment_id=record.appointment_id,
                prescription=record.prescription,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record in records.order_by(MedicalRecord.created_at.desc()).all()
        ]
    elif current_user["role"] == UserRole.DOCTOR.value:
        doctor = DoctorCRUD.get_by_user_id(db, current_user["user_id"])
        records = records.filter(MedicalRecord.doctor_id == doctor.id if doctor else False)
    return records.order_by(MedicalRecord.created_at.desc()).all()


@router.post("/", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    record_data: MedicalRecordCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user["role"] != UserRole.DOCTOR.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Somente o médico pode criar o laudo.")
    doctor = DoctorCRUD.get_by_user_id(db, current_user["user_id"])
    if not doctor or doctor.id != record_data.doctor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Laudo deve ser criado pelo médico responsável.")
    patient = PatientCRUD.get_by_id(db, record_data.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado.")
    if record_data.appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == record_data.appointment_id).first()
        if not appointment or appointment.patient_id != patient.id or appointment.doctor_id != doctor.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Consulta não pertence ao médico e paciente informados.")
        if appointment.status.value == "cancelled":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Consultas canceladas não podem receber laudo.")
        if appointment.status not in {AppointmentStatus.IN_PROGRESS, AppointmentStatus.COMPLETED}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Inicie o atendimento antes de criar o laudo.")
    existing = db.query(MedicalRecord).filter(
        MedicalRecord.appointment_id == record_data.appointment_id
    ).order_by(MedicalRecord.id.desc()).first() if record_data.appointment_id else None
    if existing:
        for key, value in record_data.model_dump(exclude={"patient_id", "doctor_id", "appointment_id"}).items():
            setattr(existing, key, value)
        if record_data.appointment_id:
            appointment.status = AppointmentStatus.COMPLETED
        db.commit()
        db.refresh(existing)
        return existing
    record = MedicalRecord(**record_data.model_dump())
    db.add(record)
    if record_data.appointment_id:
        appointment.status = AppointmentStatus.COMPLETED
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: int,
    record_data: MedicalRecordUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permite ao médico responsável corrigir um laudo após a consulta."""
    if current_user["role"] != UserRole.DOCTOR.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Somente o médico pode editar o laudo.")

    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Laudo não encontrado.")

    doctor = DoctorCRUD.get_by_user_id(db, current_user["user_id"])
    if not doctor or record.doctor_id != doctor.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não pode editar este laudo.")

    for key, value in record_data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record
