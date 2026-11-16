from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.db.models import Usuario, Auditoria
from app.db.schemas import UserLogin, Token, UserResponse, UserCreate
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.execute(select(Usuario).where(Usuario.email == login_data.email)).scalar_one_or_none()
    if not user or not verify_password(login_data.password, user.hashed_password):
        # Audit failed login
        audit = Auditoria(
            usuario_email=login_data.email,
            accion="LOGIN_FALLIDO",
            entidad="usuarios",
            exito=False,
            detalles={"motivo": "Credenciales inválidas"}
        )
        db.add(audit)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Audit successful login
    audit = Auditoria(
        usuario_id=user.id,
        usuario_email=user.email,
        accion="LOGIN_EXITOSO",
        entidad="usuarios",
        entidad_id=user.id,
        exito=True
    )
    db.add(audit)
    db.commit()

    token = create_access_token(subject=user.id, role=user.rol)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "rol": user.rol
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    return current_user

