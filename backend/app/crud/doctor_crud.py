from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models import Doctor, User
from app.schemas import DoctorCreate, DoctorUpdate


class DoctorCRUD:
    """Operações de banco de dados para médicos."""
    
    @staticmethod
    def create(db: Session, doctor_create: DoctorCreate) -> Doctor:
        """Cria um novo médico."""
        db_doctor = Doctor(
            user_id=doctor_create.user_id,
            crm=doctor_create.crm,
            specialty=doctor_create.specialty,
            bio=doctor_create.bio,
            office_phone=doctor_create.office_phone
        )
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    
    @staticmethod
    def get_by_id(db: Session, doctor_id: int) -> Doctor:
        """Obtém um médico por ID."""
        return db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Doctor:
        """Obtém um médico por user_id."""
        return db.query(Doctor).filter(Doctor.user_id == user_id).first()
    
    @staticmethod
    def get_by_crm(db: Session, crm: str) -> Doctor:
        """Obtém um médico por CRM."""
        return db.query(Doctor).filter(Doctor.crm == crm).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Doctor]:
        """Obtém todos os médicos."""
        return db.query(Doctor).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_specialty(db: Session, specialty: str, skip: int = 0, limit: int = 100) -> list[Doctor]:
        """Obtém médicos por especialidade."""
        return db.query(Doctor).filter(Doctor.specialty == specialty).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, doctor_id: int, doctor_update: DoctorUpdate) -> Doctor:
        """Atualiza um médico."""
        db_doctor = DoctorCRUD.get_by_id(db, doctor_id)
        if not db_doctor:
            return None
        
        update_data = doctor_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_doctor, key, value)
        
        db_doctor.updated_at = datetime.utcnow()
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    
    @staticmethod
    def delete(db: Session, doctor_id: int) -> bool:
        """Deleta um médico."""
        db_doctor = DoctorCRUD.get_by_id(db, doctor_id)
        if not db_doctor:
            return False
        db.delete(db_doctor)
        db.commit()
        return True
    
    @staticmethod
    def count(db: Session) -> int:
        """Conta o número total de médicos."""
        return db.query(func.count(Doctor.id)).scalar()
