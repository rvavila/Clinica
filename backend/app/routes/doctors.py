from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import DoctorCreate, DoctorUpdate, DoctorResponse, DoctorDetailedResponse, UserResponse
from app.crud import DoctorCRUD, UserCRUD
from app.core.security import get_current_user, require_role
from app.core.constants import UserRole

router = APIRouter(prefix="/api/doctors", tags=["doctors"])


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor_create: DoctorCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo médico. Apenas ADMIN e DOCTOR podem criar.
    """
    if current_user["role"] not in [UserRole.ADMIN.value, UserRole.DOCTOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Verificar se user_id existe
    user = UserCRUD.get_by_id(db, doctor_create.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar se CRM já existe
    existing_doctor = DoctorCRUD.get_by_crm(db, doctor_create.crm)
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CRM já registrado"
        )
    
    doctor = DoctorCRUD.create(db, doctor_create)
    return doctor


@router.get("/users/unassigned", response_model=list[UserResponse])
async def list_unassigned_doctor_users(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista contas de médicos que ainda não possuem perfil profissional."""
    if current_user["role"] not in [UserRole.ADMIN.value, UserRole.RECEPTION.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    users = UserCRUD.get_by_role(db, UserRole.DOCTOR)
    return [user for user in users if not DoctorCRUD.get_by_user_id(db, user.id)]


@router.post("/profile", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor_profile(
    doctor_create: DoctorCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Completa o perfil profissional de uma conta de médico."""
    if current_user["role"] not in [UserRole.ADMIN.value, UserRole.RECEPTION.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    user = UserCRUD.get_by_id(db, doctor_create.user_id)
    if not user or user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta de médico não encontrada")
    if DoctorCRUD.get_by_user_id(db, doctor_create.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este médico já possui cadastro profissional")
    if DoctorCRUD.get_by_crm(db, doctor_create.crm):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CRM já registrado")

    return DoctorCRUD.create(db, doctor_create)


@router.get("/", response_model=list[DoctorDetailedResponse])
async def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    specialty: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os médicos.
    
    Parâmetros:
    - **specialty**: Filtrar por especialidade (opcional)
    """
    
    if specialty:
        doctors = DoctorCRUD.get_by_specialty(db, specialty, skip=skip, limit=limit)
    else:
        doctors = DoctorCRUD.get_all(db, skip=skip, limit=limit)
    
    # Enriquecer com dados do usuário
    result = []
    for doctor in doctors:
        user = UserCRUD.get_by_id(db, doctor.user_id)
        result.append({
            **doctor.__dict__,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone
        })
    
    return result


@router.get("/{doctor_id}", response_model=DoctorDetailedResponse)
async def get_doctor(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém informações de um médico específico.
    """
    doctor = DoctorCRUD.get_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    user = UserCRUD.get_by_id(db, doctor.user_id)
    
    return {
        **doctor.__dict__,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone
    }


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_update: DoctorUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza informações de um médico.
    
    Apenas o próprio médico, ADMIN ou RECEPTION podem atualizar.
    """
    doctor = DoctorCRUD.get_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    # Verificar permissão
    if (current_user["user_id"] != doctor.user_id and 
        current_user["role"] not in [UserRole.ADMIN.value, UserRole.RECEPTION.value]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )

    if doctor_update.crm:
        existing_doctor = DoctorCRUD.get_by_crm(db, doctor_update.crm)
        if existing_doctor and existing_doctor.id != doctor_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CRM já registrado")
    
    if bool(doctor_update.vacation_start) != bool(doctor_update.vacation_end):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe o início e o fim das férias.",
        )
    if doctor_update.vacation_start and doctor_update.vacation_end:
        if doctor_update.vacation_start >= doctor_update.vacation_end:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O fim das férias deve ser posterior ao início.",
            )

    doctor = DoctorCRUD.update(db, doctor_id, doctor_update)
    return doctor


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta um médico. Apenas ADMIN pode deletar.
    """
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    success = DoctorCRUD.delete(db, doctor_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
