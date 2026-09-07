from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.database import get_db
from app.schemas import UserCreate, UserLoginRequest, TokenResponse, UserResponse
from app.crud import UserCRUD
from app.core.security import create_access_token, get_current_user
from app.core.config import settings
from app.core.constants import UserRole

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário.
    
    - **email**: Email do usuário (único)
    - **full_name**: Nome completo
    - **cpf**: CPF (único, 11 dígitos)
    - **password**: Senha (mín. 8 caracteres)
    - **role**: Role do usuário (admin, doctor, reception, patient)
    """
    
    if user_create.role == UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O paciente deve ser cadastrado pela recepção"
        )

    # Verificar se email já existe
    existing_user = UserCRUD.get_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Verificar se CPF já existe
    existing_cpf = UserCRUD.get_by_cpf(db, user_create.cpf)
    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já registrado"
        )
    
    # Criar usuário
    user = UserCRUD.create(db, user_create)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Realiza login e retorna token JWT.
    
    - **email**: Email do usuário
    - **password**: Senha
    """
    
    # Autenticar usuário
    user = UserCRUD.authenticate(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obtém informações do usuário atualmente logado.
    """
    user = UserCRUD.get_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user
