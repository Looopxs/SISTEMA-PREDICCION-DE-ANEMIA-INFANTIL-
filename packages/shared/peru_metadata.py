import json
from pathlib import Path

METADATA_FILE = Path(__file__).parent / "peru_metadata.json"

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    _data = json.load(f)

DEPARTAMENTOS_METADATA = _data["departamentos"]
REGLAS_CLINICAS = _data["reglas_clinicas"]

