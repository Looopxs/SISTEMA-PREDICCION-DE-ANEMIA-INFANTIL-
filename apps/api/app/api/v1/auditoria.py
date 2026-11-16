from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import Auditoria
from app.db.schemas import AuditoriaItem

router = APIRouter()

@router.get("/", response_model=List[AuditoriaItem])
def list_auditoria(limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns sanitized audit logs for compliance, governance, and traceability.
    """
    logs = db.execute(select(Auditoria).order_by(Auditoria.timestamp.desc()).limit(limit)).scalars().all()
    return logs

