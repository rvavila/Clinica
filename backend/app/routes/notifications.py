from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.notification import Notification
from app.schemas.notification_schema import NotificationResponse


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    limit: int = Query(30, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna os avisos internos destinados ao usuário autenticado."""
    return (
        db.query(Notification)
        .filter(Notification.recipient_user_id == current_user["user_id"])
        # Data primeiro; o ID desempata cancelamentos registrados no mesmo instante.
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(limit)
        .all()
    )
