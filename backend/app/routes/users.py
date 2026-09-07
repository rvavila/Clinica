from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import PasswordReset, UserResponse, UserUpdate
from app.crud import UserCRUD
from app.core.security import get_current_user, require_role
from app.core.constants import UserRole

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários. Apenas ADMIN pode acessar.
    """
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    users = UserCRUD.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém informações de um usuário específico.
    
    Usuários comuns só podem ver suas próprias informações.
    """
    target_user = UserCRUD.get_by_id(db, user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # A recepção pode editar contas de pacientes e médicos.
    can_edit_patient = (
        current_user["role"] == UserRole.RECEPTION.value
        and target_user.role in [UserRole.PATIENT, UserRole.DOCTOR]
    )
    if (current_user["user_id"] != user_id
            and current_user["role"] != UserRole.ADMIN.value
            and not can_edit_patient):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    user = UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza informações de um usuário.
    
    Usuários comuns só podem atualizar suas próprias informações.
    """
    target_user = UserCRUD.get_by_id(db, user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    can_edit_patient = (
        current_user["role"] == UserRole.RECEPTION.value
        and target_user.role in [UserRole.PATIENT, UserRole.DOCTOR]
    )
    if (current_user["user_id"] != user_id
            and current_user["role"] != UserRole.ADMIN.value
            and not can_edit_patient):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    if user_update.email:
        existing = UserCRUD.get_by_email(db, user_update.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registrado")
    if user_update.cpf:
        existing = UserCRUD.get_by_cpf(db, user_update.cpf)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF já registrado")

    user = UserCRUD.update(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user


@router.put("/{user_id}/password", response_model=UserResponse)
async def reset_user_password(
    user_id: int,
    password_reset: PasswordReset,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite à recepção redefinir a senha de pacientes e médicos."""
    target_user = UserCRUD.get_by_id(db, user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    allowed = current_user["role"] == UserRole.ADMIN.value or (
        current_user["role"] == UserRole.RECEPTION.value
        and target_user.role in [UserRole.PATIENT, UserRole.DOCTOR]
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    return UserCRUD.reset_password(db, user_id, password_reset.password)


@router.get("/role/{role}", response_model=list[UserResponse])
async def get_users_by_role(
    role: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários de uma role específica.
    
    Roles: admin, doctor, reception, patient
    """
    try:
        user_role = UserRole[role.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role inválida. Roles válidas: {', '.join([r.value for r in UserRole])}"
        )
    
    # Apenas ADMIN pode listar usuários
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    users = UserCRUD.get_by_role(db, user_role, skip=skip, limit=limit)
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta um usuário. Apenas ADMIN pode deletar.
    """
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    success = UserCRUD.delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
