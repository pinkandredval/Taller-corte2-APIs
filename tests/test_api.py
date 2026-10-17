"""Pruebas del servicio (aisladas)."""
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from database import get_db, Base

# 1. Configurar base de datos en memoria para los tests
engine = create_engine(
    "sqlite://", 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)
Base.metadata.create_all(engine)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 2. Sustituir la dependencia real por la de prueba
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

cliente = TestClient(app)

# 3. Usar un número que cumpla el patrón POL-AAAA-NNNNN (H31)
POLIZA = {
    "numero": "POL-2026-00001", 
    "asegurado": "Prueba Interna",
    "tipo": "auto",
    "prima": 1_000_000,
    "fecha_inicio": "2026-01-01",
    "fecha_fin": "2026-12-31",
}

def test_crear_poliza():
    r = cliente.post("/polizas", json=POLIZA)
    assert r.status_code == 201  # <-- Ahora espera 201 correctamente
    assert r.json()["numero"] == POLIZA["numero"]

def test_listar_polizas():
    r = cliente.get("/polizas")
    assert r.status_code == 200
    assert any(p["numero"] == POLIZA["numero"] for p in r.json())