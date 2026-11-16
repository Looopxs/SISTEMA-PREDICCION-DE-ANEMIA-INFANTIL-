from app.core.database import engine, Base, SessionLocal
from app.db.models import Usuario
from app.core.security import get_password_hash
from sqlalchemy import select

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as session:
        admin = session.execute(select(Usuario).where(Usuario.email == "admin@nutripredict.pe")).scalar_one_or_none()
        if not admin:
            admin = Usuario(
                email="admin@nutripredict.pe",
                hashed_password=get_password_hash("AdminNutri2026!"),
                nombre="Dra. Elena Ramos (Admin Epidemiología)",
                rol="admin",
                activo=True
            )
            session.add(admin)

        investigador = session.execute(select(Usuario).where(Usuario.email == "investigador@nutripredict.pe")).scalar_one_or_none()
        if not investigador:
            investigador = Usuario(
                email="investigador@nutripredict.pe",
                hashed_password=get_password_hash("Investiga2026!"),
                nombre="Lic. Carlos Morales (Investigador Principal)",
                rol="investigador",
                activo=True
            )
            session.add(investigador)

        session.commit()
    print("Database tables initialized successfully and default users created.")

if __name__ == "__main__":
    init_db()
