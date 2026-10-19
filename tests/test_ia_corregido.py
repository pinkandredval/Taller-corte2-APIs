"""
Batería corregida para polizas-api-v0.

Defecto 3 (aleatoriedad sin control): se sustituyen random/uuid sin semilla por
datos deterministas y se comprueba el CUERPO de la respuesta, no solo el status.

Se ejecuta desde la raíz del proyecto con:
    pytest tests/test_ia_corregido.py -v
"""
import random

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app, cargar_modelo

# --- Aislamiento real de la BD: SQLite en memoria -------------------------
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class ModeloFalso:
    """Sustituye al pickle real: /score no depende de un archivo externo."""

    def predict_proba(self, rasgos):
        return [[0.2, 0.8] for _ in rasgos]


@pytest.fixture(autouse=True)
def entorno_aislado():
    """BD limpia y dependencias sustituidas antes de CADA test."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[cargar_modelo] = lambda: ModeloFalso()
    yield
    app.dependency_overrides.clear()


cliente = TestClient(app)

# UNA sola instancia con semilla: datos variados pero reproducibles.
# (Crear Random(42) dentro de _poliza() daría siempre el mismo valor.)
_RNG = random.Random(42)


def _poliza(**extra) -> dict:
    base = {
        "numero": "POL-2026-ABC02",
        "asegurado": "Prueba Automática",
        "tipo": _RNG.choice(["auto", "hogar", "vida"]),
        "prima": round(_RNG.uniform(1, 5_000_000), 2),
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-12-31",
    }
    base.update(extra)
    return base


# --- Creación -------------------------------------------------------------
def test_crear_poliza_responde():
    datos = _poliza()
    r = cliente.post("/polizas", json=datos)
    assert r.status_code == 201, f"Se esperaba 201, se obtuvo {r.status_code}"
    assert r.json()["numero"] == datos["numero"]



def test_primas_variadas_son_aceptadas():
    primas = [1.0, 99.99, 123_456.78, 1_500_000.5, 5_000_000.0]
    for i, prima in enumerate(primas):
        datos = _poliza(numero=f"POL-2026-VAR{i:02d}", prima=prima)
        r = cliente.post("/polizas", json=datos)
        assert r.status_code == 201, f"Se esperaba 201, se obtuvo {r.status_code}"
        assert r.json()["numero"] == datos["numero"]
        assert r.json()["prima"] == prima


# --- Consulta -------------------------------------------------------------
def test_consultar_poliza_inexistente():
    r = cliente.get("/polizas/999999")
    assert r.status_code == 404, f"Se esperaba 404, se obtuvo {r.status_code}"


def test_listar_polizas_vacio():
    r = cliente.get("/polizas")
    assert r.status_code == 200


def test_resumen_devuelve_lista():
    r = cliente.get("/resumen")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# --- Puntuación -----------------------------------------------------------
def test_score_de_poliza_recien_creada():
    datos = _poliza()
    assert cliente.post("/polizas", json=datos).status_code == 201
    r = cliente.post("/score", json={"numero": datos["numero"]})
    assert r.status_code == 200
    assert r.json()["puntaje"] == 0.8