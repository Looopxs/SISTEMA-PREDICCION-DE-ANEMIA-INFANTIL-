from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db, SessionLocal
from app.db.models import Experimento, Dataset, Modelo, Auditoria, Usuario
from app.db.schemas import ExperimentoCreate, ExperimentoResponse
from app.services.experiment_runner import ejecutar_experimento_completo
from app.api.deps import get_current_user

router = APIRouter()

def _run_experiment_task(exp_id: str):
    db = SessionLocal()
    try:
        ejecutar_experimento_completo(exp_id, db)
    finally:
        db.close()

@router.get("/", response_model=List[ExperimentoResponse])
def list_experimentos(db: Session = Depends(get_db)):
    experimentos = db.execute(select(Experimento).order_by(Experimento.created_at.desc())).scalars().all()
    results = []
    for exp in experimentos:
        models_count = len(exp.modelos)
        res = ExperimentoResponse.from_orm(exp)
        res.modelos_count = models_count
        results.append(res)
    return results

@router.post("/", response_model=ExperimentoResponse)
def create_experimento(
    exp_in: ExperimentoCreate,
    db: Session = Depends(get_db),
    current_user: Optional[Usuario] = Depends(get_current_user)
):
    dataset = db.execute(select(Dataset).where(Dataset.id == exp_in.dataset_id)).scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    exp = Experimento(
        dataset_id=exp_in.dataset_id,
        nombre=exp_in.nombre,
        descripcion=exp_in.descripcion,
        semilla_random=exp_in.semilla_random,
        particion_tipo=exp_in.particion_tipo,
        train_pct=exp_in.train_pct,
        val_pct=exp_in.val_pct,
        test_pct=exp_in.test_pct,
        estado="creado",
        progreso_pct=0,
        logs_sanitizados=f"Experimento '{exp_in.nombre}' registrado. Listo para ejecución.\n"
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)

    audit = Auditoria(
        usuario_email=current_user.email if current_user else "investigador",
        accion="CREAR_EXPERIMENTO",
        entidad="experimentos",
        entidad_id=exp.id,
        detalles={"nombre": exp.nombre, "semilla": exp.semilla_random}
    )
    db.add(audit)
    db.commit()

    res = ExperimentoResponse.from_orm(exp)
    res.modelos_count = 0
    return res

@router.post("/{id}/run")
def run_experimento(
    id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[Usuario] = Depends(get_current_user)
):
    exp = db.execute(select(Experimento).where(Experimento.id == id)).scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")

    if exp.estado == "en_progreso":
        raise HTTPException(status_code=400, detail="El experimento ya se encuentra en ejecución")

    # Queue background task
    background_tasks.add_task(_run_experiment_task, exp.id)

    exp.estado = "en_progreso"
    exp.progreso_pct = 5
    db.commit()

    return {
        "status": "en_progreso",
        "mensaje": f"Experimento '{exp.nombre}' encolado con éxito. Ejecutando M1-M5 en segundo plano.",
        "experimento_id": exp.id
    }

@router.get("/{id}", response_model=ExperimentoResponse)
def get_experimento(id: str, db: Session = Depends(get_db)):
    exp = db.execute(select(Experimento).where(Experimento.id == id)).scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")
    res = ExperimentoResponse.from_orm(exp)
    res.modelos_count = len(exp.modelos)
    return res

