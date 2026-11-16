from app.core.database import SessionLocal
from app.db.models import Dataset, Experimento
from app.services.experiment_runner import ejecutar_experimento_completo
from sqlalchemy import select

def seed_experiment():
    with SessionLocal() as db:
        # Check if already trained
        exp_existing = db.execute(select(Experimento).where(Experimento.estado == "completado")).scalars().first()
        if exp_existing:
            print(f"Experimento ya existe y completado: {exp_existing.nombre} (ID: {exp_existing.id})")
            return

        dataset = db.execute(select(Dataset).where(Dataset.es_sintetico == True)).scalars().first()
        if not dataset:
            print("No synthetic dataset found, please run init_db first.")
            return

        exp = Experimento(
            dataset_id=dataset.id,
            nombre="Protocolo Multitarea M1-M5 (Validación Estratificada por PSU)",
            descripcion="Estudio comparativo experimental de las cinco arquitecturas: baselines independientes (M1, M2, M3) frente a Multi-Task Learning (M4) e Híbrido Residual (M5).",
            semilla_random=42,
            particion_tipo="Estratificada por Conglomerados",
            train_pct=0.70,
            val_pct=0.15,
            test_pct=0.15,
            estado="creado",
            progreso_pct=0,
            logs_sanitizados="Iniciando ejecución programada de experimento base...\n"
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)

        print(f"Executing experiment {exp.id}...")
        ejecutar_experimento_completo(exp.id, db)
        print(f"Experiment completed successfully! Models M1-M5 generated.")

if __name__ == "__main__":
    seed_experiment()

