from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.constants import UserRole, UserStatus


class UserCRUD:
    """Operações de banco de dados para usuários."""
    
    @staticmethod
    def create(db: Session, user_create: UserCreate) -> User:
        """Cria um novo usuário."""
        db_user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            phone=user_create.phone,
            cpf=user_create.cpf,
            hashed_password=get_password_hash(user_create.password),
            role=user_create.role,
            status=UserStatus.ACTIVE
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        """Obtém um usuário por ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> User:
        """Obtém um usuário por email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_cpf(db: Session, cpf: str) -> User:
        """Obtém um usuário por CPF."""
        return db.query(User).filter(User.cpf == cpf).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Obtém todos os usuários."""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_role(db: Session, role: UserRole, skip: int = 0, limit: int = 100) -> list[User]:
        """Obtém usuários por role."""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """Atualiza um usuário."""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db_user.updated_at = datetime.utcnow()
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def reset_password(db: Session, user_id: int, password: str) -> User:
        """Redefine a senha de um usuário."""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        db_user.hashed_password = get_password_hash(password)
        db_user.updated_at = datetime.utcnow()
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User:
        """Autentica um usuário."""
        user = UserCRUD.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        
        return user
    
    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """Deleta um usuário."""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def count(db: Session) -> int:
        """Conta o número total de usuários."""
        return db.query(func.count(User.id)).scalar()
