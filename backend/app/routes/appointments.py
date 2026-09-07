from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.db.database import get_db
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentDetailedResponse
from app.crud import AppointmentCRUD, PatientCRUD, UserCRUD, DoctorCRUD
from app.core.security import get_current_user
from app.core.constants import UserRole, AppointmentStatus
from app.models.notification import Notification
from app.models.user import User
from app.models.appointment import Appointment

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def _validate_schedule_slot(appointment_datetime: datetime):
    """A agenda usa slots fixos de 30 minutos, das 08:00 às 22:00."""
    sao_paulo = ZoneInfo("America/Sao_Paulo")
    current_datetime = datetime.now(appointment_datetime.tzinfo) if appointment_datetime.tzinfo else datetime.now(sao_paulo).replace(tzinfo=None)
    if appointment_datetime <= current_datetime:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não é possível agendar uma consulta em data ou horário que já passou.",
        )
    if appointment_datetime.minute not in (0, 30) or appointment_datetime.second or appointment_datetime.microsecond:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Escolha um horário em intervalos de 30 minutos, entre 08:00 e 22:00.",
        )
    if appointment_datetime.hour < 8 or appointment_datetime.hour > 22 or (
        appointment_datetime.hour == 22 and appointment_datetime.minute != 0
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Os agendamentos podem ser marcados somente entre 08:00 e 22:00.",
        )


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_create: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo agendamento.
    
    PATIENT pode agendar para si mesmo.
    RECEPTION pode agendar para qualquer paciente.
    DOCTOR pode agendar para pacientes.
    """
    
    # Verificar se paciente existe
    patient = PatientCRUD.get_by_id(db, appointment_create.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Verificar permissão do paciente
    if (current_user["role"] == UserRole.PATIENT.value and 
        current_user["user_id"] != patient.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pacientes só podem agendar para si mesmos"
        )
    
    # Verificar se médico existe
    doctor = DoctorCRUD.get_by_id(db, appointment_create.doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )

    _validate_schedule_slot(appointment_create.appointment_datetime)

    if (
        doctor.vacation_start
        and doctor.vacation_end
        and doctor.vacation_start <= appointment_create.appointment_datetime <= doctor.vacation_end
        ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este médico está de férias no período informado e não pode receber agendamentos.",
        )

    # Consultas do mesmo médico precisam ter pelo menos 30 minutos de intervalo.
    interval_start = appointment_create.appointment_datetime - timedelta(minutes=30)
    interval_end = appointment_create.appointment_datetime + timedelta(minutes=30)
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == appointment_create.doctor_id,
        Appointment.status.notin_([AppointmentStatus.CANCELLED]),
        Appointment.appointment_datetime > interval_start,
        Appointment.appointment_datetime < interval_end,
    ).first()
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este médico já possui uma consulta em um intervalo menor que 30 minutos.",
        )
    
    appointment = AppointmentCRUD.create(db, appointment_create)
    return appointment


@router.get("/", response_model=list[AppointmentDetailedResponse])
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista agendamentos.
    
    PATIENT: vê seus próprios agendamentos
    DOCTOR: vê seus agendamentos
    RECEPTION e ADMIN: veem todos
    """
    
    if current_user["role"] == UserRole.PATIENT.value:
        patient = PatientCRUD.get_by_user_id(db, current_user["user_id"])
        if not patient:
            return []
        appointments = AppointmentCRUD.get_by_patient(db, patient.id, skip=skip, limit=limit)
    elif current_user["role"] == UserRole.DOCTOR.value:
        doctor = DoctorCRUD.get_by_user_id(db, current_user["user_id"])
        if not doctor:
            return []
        appointments = AppointmentCRUD.get_by_doctor(db, doctor.id, skip=skip, limit=limit)
    else:
        appointments = AppointmentCRUD.get_all(db, skip=skip, limit=limit)
    
    # Enriquecer com dados
    result = []
    for appt in appointments:
        patient = PatientCRUD.get_by_id(db, appt.patient_id)
        doctor = DoctorCRUD.get_by_id(db, appt.doctor_id)
        patient_user = UserCRUD.get_by_id(db, patient.user_id)
        doctor_user = UserCRUD.get_by_id(db, doctor.user_id)
        
        result.append({
            **appt.__dict__,
            "patient_name": patient_user.full_name,
            "doctor_name": doctor_user.full_name,
            "doctor_specialty": doctor.specialty,
            "room_name": None  # Will be filled if room exists
        })
    
    return result


@router.get("/{appointment_id}", response_model=AppointmentDetailedResponse)
async def get_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém informações de um agendamento específico.
    """
    appointment = AppointmentCRUD.get_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Verificar permissão
    patient = PatientCRUD.get_by_id(db, appointment.patient_id)
    doctor = DoctorCRUD.get_by_id(db, appointment.doctor_id)

    if (current_user["role"] == UserRole.PATIENT.value and 
        current_user["user_id"] != patient.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    if (current_user["role"] == UserRole.DOCTOR.value and 
        current_user["user_id"] != doctor.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    patient_user = UserCRUD.get_by_id(db, patient.user_id)
    doctor_user = UserCRUD.get_by_id(db, doctor.user_id)
    
    return {
        **appointment.__dict__,
        "patient_name": patient_user.full_name,
        "doctor_name": doctor_user.full_name,
        "doctor_specialty": doctor.specialty,
        "room_name": None
    }


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um agendamento.
    
    RECEPTION e ADMIN podem atualizar qualquer agendamento.
    DOCTOR pode atualizar seus próprios agendamentos.
    """
    appointment = AppointmentCRUD.get_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Verificar permissão
    doctor = DoctorCRUD.get_by_id(db, appointment.doctor_id)
    if current_user["role"] == UserRole.PATIENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O paciente não pode alterar a consulta; solicite à recepção.",
        )
    if (current_user["role"] == UserRole.DOCTOR.value and 
        current_user["user_id"] != doctor.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    patient = PatientCRUD.get_by_id(db, appointment.patient_id)
    patient_user = UserCRUD.get_by_id(db, patient.user_id) if patient else None
    old_datetime = appointment.appointment_datetime
    old_status = appointment.status
    if appointment_update.appointment_datetime and doctor.vacation_start and doctor.vacation_end:
        if doctor.vacation_start <= appointment_update.appointment_datetime <= doctor.vacation_end:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este médico está de férias na nova data informada.",
            )

    if appointment_update.appointment_datetime:
        _validate_schedule_slot(appointment_update.appointment_datetime)
        candidate_datetime = appointment_update.appointment_datetime
        conflict = db.query(Appointment).filter(
            Appointment.id != appointment.id,
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.status.notin_([AppointmentStatus.CANCELLED]),
            Appointment.appointment_datetime > candidate_datetime - timedelta(minutes=30),
            Appointment.appointment_datetime < candidate_datetime + timedelta(minutes=30),
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este médico já possui uma consulta em um intervalo menor que 30 minutos.",
            )

    if (
        current_user["role"] == UserRole.DOCTOR.value
        and appointment_update.status == AppointmentStatus.IN_PROGRESS
        and appointment.appointment_datetime.date() != datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O paciente só pode ser chamado no dia da consulta.",
        )

    if current_user["role"] == UserRole.DOCTOR.value and appointment_update.status == AppointmentStatus.IN_PROGRESS:
        active_appointment = db.query(Appointment).filter(
            Appointment.id != appointment.id,
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.status == AppointmentStatus.IN_PROGRESS,
        ).first()
        if active_appointment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Encerre o atendimento atual antes de chamar outro paciente.",
            )

    appointment = AppointmentCRUD.update(db, appointment_id, appointment_update, commit=False)

    if current_user["role"] == UserRole.RECEPTION.value and appointment.appointment_datetime != old_datetime:
        doctor_user = UserCRUD.get_by_id(db, doctor.user_id)
        changes = []
        if appointment.appointment_datetime != old_datetime:
            changes.append(
                f"nova data: {appointment.appointment_datetime.strftime('%d/%m/%Y às %H:%M')}"
            )
        if appointment.status != old_status:
            changes.append(f"status: {appointment.status.value}")
        message = f"A recepção atualizou sua consulta ({'; '.join(changes)})."
        db.add_all([
            Notification(recipient_user_id=doctor_user.id, appointment_id=appointment.id, message=message),
            Notification(recipient_user_id=patient_user.id, appointment_id=appointment.id, message=message),
        ])

    # Iniciar ou finalizar atendimento não gera aviso para a recepção.
    if (
        current_user["role"] == UserRole.DOCTOR.value
        and appointment.status == AppointmentStatus.IN_PROGRESS
    ):
        label = "iniciou o atendimento" if appointment.status == AppointmentStatus.IN_PROGRESS else "encerrou o atendimento"
        message = f"O médico {label} do paciente {patient_user.full_name if patient_user else 'agendado'}."
        message = f"O medico esta chamando o paciente {patient_user.full_name if patient_user else 'agendado'} para entrar."
        db.add_all([
            Notification(recipient_user_id=user.id, appointment_id=appointment.id, message=message)
            for user in db.query(User).filter(User.role == UserRole.RECEPTION.value).all()
        ])

    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    reason: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancela um agendamento.
    """
    appointment = AppointmentCRUD.get_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Verificar permissão
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este agendamento já está cancelado.",
        )

    if appointment.status not in {
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.IN_PROGRESS,
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente consultas agendadas ou confirmadas podem ser canceladas.",
        )

    patient = PatientCRUD.get_by_id(db, appointment.patient_id)
    doctor = DoctorCRUD.get_by_id(db, appointment.doctor_id)
    
    if (current_user["role"] == UserRole.PATIENT.value and 
        current_user["user_id"] != patient.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    if (current_user["role"] == UserRole.DOCTOR.value and 
        current_user["user_id"] != doctor.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # O prazo é aplicado somente ao paciente. Recepção e médico mantêm a
    # possibilidade de intervir na agenda quando necessário.
    if current_user["role"] == UserRole.PATIENT.value:
        appointment_time = appointment.appointment_datetime
        # O banco pode retornar datetime sem fuso; mantenha os dois valores
        # no mesmo formato antes de calcular o prazo de 24 horas.
        now = (
            datetime.now(appointment_time.tzinfo)
            if appointment_time.tzinfo
            else datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
        )
        if appointment_time - now < timedelta(hours=24):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O cancelamento pelo paciente só é permitido com no mínimo 24 horas de antecedência.",
            )

    # O cancelamento e os avisos devem ser gravados juntos.
    appointment = AppointmentCRUD.cancel(db, appointment_id, reason, commit=False)

    if current_user["role"] == UserRole.PATIENT.value:
        patient_user = UserCRUD.get_by_id(db, patient.user_id)
        doctor_user = UserCRUD.get_by_id(db, doctor.user_id)
        message = (
            f"Cancelada pelo usuário: {patient_user.full_name} cancelou a consulta de "
            f"{appointment.appointment_datetime.strftime('%d/%m/%Y às %H:%M')}."
        )
        recipient_ids = [doctor_user.id]
        recipient_ids.extend(
            user.id
            for user in db.query(User).filter(User.role == UserRole.RECEPTION.value).all()
        )
        db.add_all([
            Notification(
                recipient_user_id=recipient_id,
                appointment_id=appointment.id,
                message=message,
            )
            for recipient_id in set(recipient_ids)
        ])
    elif current_user["role"] == UserRole.RECEPTION.value:
        patient_user = UserCRUD.get_by_id(db, patient.user_id)
        doctor_user = UserCRUD.get_by_id(db, doctor.user_id)
        message = (
            f"Cancelada pela clínica: a recepção cancelou a consulta de {patient_user.full_name} em "
            f"{appointment.appointment_datetime.strftime('%d/%m/%Y às %H:%M')}."
        )
        db.add_all([
            Notification(recipient_user_id=doctor_user.id, appointment_id=appointment.id, message=message),
            Notification(recipient_user_id=patient_user.id, appointment_id=appointment.id, message=message),
        ])
    elif current_user["role"] == UserRole.DOCTOR.value:
        patient_user = UserCRUD.get_by_id(db, patient.user_id)
        message = (
            f"Cancelada pela clínica: o médico cancelou a consulta de {patient_user.full_name} em "
            f"{appointment.appointment_datetime.strftime('%d/%m/%Y às %H:%M')}."
        )
        recipient_ids = [patient_user.id]
        recipient_ids.extend(
            user.id
            for user in db.query(User).filter(User.role == UserRole.RECEPTION.value).all()
        )
        db.add_all([
            Notification(recipient_user_id=recipient_id, appointment_id=appointment.id, message=message)
            for recipient_id in set(recipient_ids)
        ])
    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta um agendamento. Apenas ADMIN pode deletar.
    """
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    success = AppointmentCRUD.delete(db, appointment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
