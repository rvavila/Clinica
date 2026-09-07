from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text

from app.core.config import settings
from app.db.database import Base, engine
from app.routes import auth, users, doctors, patients, appointments, notifications, medical_records
from app.db.database import SessionLocal
from app.models import Appointment, Notification, User
from app.core.constants import AppointmentStatus, UserRole

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Migração leve para instalações existentes (sem Alembic neste projeto).
doctor_columns = {column["name"] for column in inspect(engine).get_columns("doctors")}
with engine.begin() as connection:
    if engine.dialect.name == "postgresql":
        connection.execute(text("ALTER TYPE appointmentstatus ADD VALUE IF NOT EXISTS 'IN_PROGRESS'"))
    if "vacation_start" not in doctor_columns:
        connection.execute(text("ALTER TABLE doctors ADD COLUMN vacation_start TIMESTAMP NULL"))
    if "vacation_end" not in doctor_columns:
        connection.execute(text("ALTER TABLE doctors ADD COLUMN vacation_end TIMESTAMP NULL"))

# Recupera cancelamentos antigos que foram feitos antes do sistema de avisos.
with SessionLocal() as migration_db:
    cancelled = migration_db.query(Appointment).filter(
        Appointment.status == AppointmentStatus.CANCELLED
    ).all()
    for appointment in cancelled:
        doctor_user_id = migration_db.query(User.id).join(User.doctor).filter(
            User.doctor.has(id=appointment.doctor_id)
        ).scalar()
        patient_user_id = migration_db.query(User.id).join(User.patient).filter(
            User.patient.has(id=appointment.patient_id)
        ).scalar()
        recipient_ids = [doctor_user_id, patient_user_id]
        recipient_ids.extend(
            user_id for (user_id,) in migration_db.query(User.id).filter(
                User.role == UserRole.RECEPTION
            ).all()
        )
        message = (
            f"Aviso: a consulta de {appointment.appointment_datetime.strftime('%d/%m/%Y às %H:%M')} "
            "foi cancelada."
        )
        existing_recipients = {
            user_id for (user_id,) in migration_db.query(Notification.recipient_user_id).filter(
                Notification.appointment_id == appointment.id
            ).all()
        }
        migration_db.add_all([
            Notification(recipient_user_id=user_id, appointment_id=appointment.id, message=message)
            for user_id in set(filter(None, recipient_ids))
            if user_id not in existing_recipients
        ])
    migration_db.commit()

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API para gerenciamento de clínica médica",
    version=settings.APP_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(notifications.router)
app.include_router(medical_records.router)


# Rotas de saúde
@app.get("/health")
async def health_check():
    """Verifica a saúde da API."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Bem-vindo à {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Rota não encontrada"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
