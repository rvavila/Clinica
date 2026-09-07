from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models import Appointment
from app.schemas import AppointmentCreate, AppointmentUpdate
from app.core.constants import AppointmentStatus


class AppointmentCRUD:
    """Operações de banco de dados para agendamentos."""
    
    @staticmethod
    def create(db: Session, appointment_create: AppointmentCreate) -> Appointment:
        """Cria um novo agendamento."""
        db_appointment = Appointment(
            patient_id=appointment_create.patient_id,
            doctor_id=appointment_create.doctor_id,
            room_id=appointment_create.room_id,
            appointment_datetime=appointment_create.appointment_datetime,
            duration_minutes=appointment_create.duration_minutes,
            consultation_type=appointment_create.consultation_type,
            notes=appointment_create.notes
        )
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    
    @staticmethod
    def get_by_id(db: Session, appointment_id: int) -> Appointment:
        """Obtém um agendamento por ID."""
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Appointment]:
        """Obtém todos os agendamentos."""
        return db.query(Appointment).order_by(Appointment.appointment_datetime.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> list[Appointment]:
        """Obtém agendamentos de um paciente."""
        return db.query(Appointment).filter(Appointment.patient_id == patient_id).order_by(Appointment.appointment_datetime.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_doctor(db: Session, doctor_id: int, skip: int = 0, limit: int = 100) -> list[Appointment]:
        """Obtém agendamentos de um médico."""
        return db.query(Appointment).filter(Appointment.doctor_id == doctor_id).order_by(Appointment.appointment_datetime.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_doctor_date(db: Session, doctor_id: int, date: datetime) -> list[Appointment]:
        """Obtém agendamentos de um médico em um dia específico."""
        from sqlalchemy import and_, func
        
        return db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                func.date(Appointment.appointment_datetime) == date.date()
            )
        ).order_by(Appointment.appointment_datetime).all()
    
    @staticmethod
    def get_by_status(db: Session, status: AppointmentStatus, skip: int = 0, limit: int = 100) -> list[Appointment]:
        """Obtém agendamentos por status."""
        return db.query(Appointment).filter(Appointment.status == status).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(
        db: Session,
        appointment_id: int,
        appointment_update: AppointmentUpdate,
        commit: bool = True,
    ) -> Appointment:
        """Atualiza um agendamento."""
        db_appointment = AppointmentCRUD.get_by_id(db, appointment_id)
        if not db_appointment:
            return None
        
        update_data = appointment_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_appointment, key, value)
        
        db_appointment.updated_at = datetime.utcnow()
        db.add(db_appointment)
        if commit:
            db.commit()
            db.refresh(db_appointment)
        else:
            db.flush()
        return db_appointment
    
    @staticmethod
    def cancel(
        db: Session,
        appointment_id: int,
        reason: str = None,
        commit: bool = True,
    ) -> Appointment:
        """Cancela um agendamento."""
        db_appointment = AppointmentCRUD.get_by_id(db, appointment_id)
        if not db_appointment:
            return None
        
        db_appointment.status = AppointmentStatus.CANCELLED
        db_appointment.cancel_reason = reason
        db_appointment.updated_at = datetime.utcnow()
        db.add(db_appointment)
        if commit:
            db.commit()
            db.refresh(db_appointment)
        else:
            db.flush()
        return db_appointment
    
    @staticmethod
    def delete(db: Session, appointment_id: int) -> bool:
        """Deleta um agendamento."""
        db_appointment = AppointmentCRUD.get_by_id(db, appointment_id)
        if not db_appointment:
            return False
        db.delete(db_appointment)
        db.commit()
        return True
    
    @staticmethod
    def count(db: Session) -> int:
        """Conta o número total de agendamentos."""
        return db.query(func.count(Appointment.id)).scalar()
