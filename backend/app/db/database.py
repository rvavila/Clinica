from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings


# Engine do banco de dados
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool if settings.DEBUG else None,
)

# Session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
