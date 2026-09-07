from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models import Patient
from app.schemas import PatientCreate, PatientUpdate


class PatientCRUD:
    """Operações de banco de dados para pacientes."""
    
    @staticmethod
    def create(db: Session, patient_create: PatientCreate) -> Patient:
        """Cria um novo paciente."""
        db_patient = Patient(
            user_id=patient_create.user_id,
            date_of_birth=patient_create.date_of_birth,
            gender=patient_create.gender,
            address=patient_create.address,
            city=patient_create.city,
            state=patient_create.state,
            zip_code=patient_create.zip_code,
            blood_type=patient_create.blood_type,
            allergies=patient_create.allergies,
            medical_conditions=patient_create.medical_conditions,
            responsible_name=patient_create.responsible_name,
            responsible_phone=patient_create.responsible_phone,
            responsible_cpf=patient_create.responsible_cpf
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    
    @staticmethod
    def get_by_id(db: Session, patient_id: int) -> Patient:
        """Obtém um paciente por ID."""
        return db.query(Patient).filter(Patient.id == patient_id).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Patient:
        """Obtém um paciente por user_id."""
        return db.query(Patient).filter(Patient.user_id == user_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Patient]:
        """Obtém todos os pacientes."""
        return db.query(Patient).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_city(db: Session, city: str, skip: int = 0, limit: int = 100) -> list[Patient]:
        """Obtém pacientes por cidade."""
        return db.query(Patient).filter(Patient.city == city).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, patient_id: int, patient_update: PatientUpdate) -> Patient:
        """Atualiza um paciente."""
        db_patient = PatientCRUD.get_by_id(db, patient_id)
        if not db_patient:
            return None
        
        update_data = patient_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_patient, key, value)
        
        db_patient.updated_at = datetime.utcnow()
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    
    @staticmethod
    def delete(db: Session, patient_id: int) -> bool:
        """Deleta um paciente."""
        db_patient = PatientCRUD.get_by_id(db, patient_id)
        if not db_patient:
            return False
        db.delete(db_patient)
        db.commit()
        return True
    
    @staticmethod
    def count(db: Session) -> int:
        """Conta o número total de pacientes."""
        return db.query(func.count(Patient.id)).scalar()
