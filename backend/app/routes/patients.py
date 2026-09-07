from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import PatientRegistrationCreate, PatientCreate, PatientUpdate, PatientResponse, PatientDetailedResponse
from app.crud import PatientCRUD, UserCRUD
from app.core.security import get_current_user
from app.core.constants import UserRole

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(
    patient_registration: PatientRegistrationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cadastra o acesso e o perfil de um paciente pela recepção."""
    if current_user["role"] not in [UserRole.ADMIN.value, UserRole.RECEPTION.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente a recepção pode cadastrar pacientes"
        )

    if UserCRUD.get_by_email(db, patient_registration.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registrado")
    if UserCRUD.get_by_cpf(db, patient_registration.cpf):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF já registrado")

    user_data = patient_registration.model_copy(update={"role": UserRole.PATIENT})
    user = UserCRUD.create(db, user_data)
    try:
        patient = PatientCRUD.create(db, PatientCreate(
            user_id=user.id,
            date_of_birth=patient_registration.date_of_birth,
            gender=patient_registration.gender,
        ))
    except Exception:
        db.rollback()
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não foi possível criar o perfil do paciente")

    return patient


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_create: PatientCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo paciente. Apenas ADMIN, RECEPTION e PATIENT podem criar.
    """
    if current_user["role"] not in [UserRole.ADMIN.value, UserRole.RECEPTION.value, UserRole.PATIENT.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Verificar se user_id existe
    user = UserCRUD.get_by_id(db, patient_create.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    patient = PatientCRUD.create(db, patient_create)
    return patient


@router.get("/", response_model=list[PatientDetailedResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os pacientes.
    
    DOCTOR e RECEPTION podem ver todos. PATIENT só vê a si mesmo.
    """
    
    # PATIENT só pode ver a si mesmo
    if current_user["role"] == UserRole.PATIENT.value:
        patient = PatientCRUD.get_by_user_id(db, current_user["user_id"])
        if not patient:
            return []
        user = UserCRUD.get_by_id(db, patient.user_id)
        return [{
            **patient.__dict__,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "cpf": user.cpf
        }]
    
    patients = PatientCRUD.get_all(db, skip=skip, limit=limit)
    
    # Enriquecer com dados do usuário
    result = []
    for patient in patients:
        user = UserCRUD.get_by_id(db, patient.user_id)
        result.append({
            **patient.__dict__,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "cpf": user.cpf
        })
    
    return result


@router.get("/{patient_id}", response_model=PatientDetailedResponse)
async def get_patient(
    patient_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém informações de um paciente específico.
    
    PATIENT só pode ver suas próprias informações.
    """
    patient = PatientCRUD.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Verificar permissão
    if (current_user["role"] == UserRole.PATIENT.value and 
        current_user["user_id"] != patient.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    user = UserCRUD.get_by_id(db, patient.user_id)
    
    return {
        **patient.__dict__,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "cpf": user.cpf
    }


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza informações de um paciente.
    
    PATIENT só pode atualizar suas próprias informações.
    """
    patient = PatientCRUD.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Verificar permissão
    if (current_user["user_id"] != patient.user_id and 
        current_user["role"] not in [UserRole.ADMIN.value, UserRole.RECEPTION.value]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    patient = PatientCRUD.update(db, patient_id, patient_update)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta um paciente. Apenas ADMIN pode deletar.
    """
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    success = PatientCRUD.delete(db, patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
