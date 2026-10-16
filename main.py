"""
polizas-api-v0 — Gestión de pólizas y siniestros.
Aseguradora Santo Tomás · prototipo interno.
"""
import hashlib
import pickle
from datetime import date

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import config
from database import Base, get_db
from esquemas import (
    PolizaActualizacion, PolizaEntrada, PuntuacionEntrada, SiniestroEntrada,
    PolizaSalida, SiniestroSalida, PrediccionSalida, ScoreSalida, ResumenSalida,
    HealthSalida, SiniestroConPoliza,
)
from modelos import Poliza, Prediccion, Siniestro



with open(config.RUTA_MODELO, "rb") as fh:
    modelo = pickle.load(fh)

app = FastAPI(title="Pólizas API", version="0.1.0")

@app.get("/health", response_model=HealthSalida)
def health(db: Session = Depends(get_db)):
    """Verifica que el servicio y la base de datos responden."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Base de datos no responde")

def firmar(numero: str) -> str:
    return hashlib.sha256(f"{numero}:{config.SECRETO_FIRMA}".encode()).hexdigest()


def _siniestro(s: Siniestro) -> dict:
    return {"id": s.id, "poliza_id": s.poliza_id, "numero_poliza": s.poliza.numero,
            "fecha": s.fecha, "monto": s.monto, "descripcion": s.descripcion, "estado": s.estado}


def _poliza(p: Poliza) -> dict:
    return {
        "id": p.id, "numero": p.numero, "asegurado": p.asegurado, "tipo": p.tipo,
        "prima": p.prima, "fecha_inicio": p.fecha_inicio, "fecha_fin": p.fecha_fin,
        "token_firma": p.token_firma,
        "siniestros": [{"id": s.id, "fecha": s.fecha, "monto": s.monto,
                        "descripcion": s.descripcion, "estado": s.estado} for s in p.siniestros],
    }


@app.post("/polizas", status_code=201, response_model=PolizaSalida)
def crear_poliza(datos: PolizaEntrada, db: Session = Depends(get_db)):
    poliza = Poliza(numero=datos.numero, asegurado=datos.asegurado, tipo=datos.tipo,
                    prima=datos.prima, fecha_inicio=datos.fecha_inicio, fecha_fin=datos.fecha_fin,
                    token_firma=firmar(datos.numero))
    for s in datos.siniestros:
        poliza.siniestros.append(Siniestro(
        fecha=s.fecha,
        monto=s.monto,
        descripcion=s.descripcion,
        estado=s.estado,
    ))
    db.add(poliza)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"El número de póliza {datos.numero} ya existe"
        )
    db.refresh(poliza)
    return poliza


@app.get("/polizas", response_model=list[PolizaSalida])
def listar_polizas(db: Session = Depends(get_db)):
    return [_poliza(p) for p in db.scalars(select(Poliza).order_by(Poliza.id))]


@app.get("/polizas/{id_poliza}", response_model=PolizaSalida)
def obtener_poliza(id_poliza: int, db: Session = Depends(get_db)):
    poliza = db.get(Poliza, id_poliza)
    if poliza is None:
        raise HTTPException(status_code=404, detail=f"no existe la póliza {id_poliza}")
    return _poliza(poliza)


@app.put("/polizas/{id_poliza}", response_model=PolizaSalida)
def actualizar_poliza(id_poliza: int, datos: PolizaActualizacion, db: Session = Depends(get_db)):
    poliza = db.get(Poliza, id_poliza)
    if poliza is None:
        return {"error": f"no existe la póliza {id_poliza}"}
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(poliza, campo, valor)
    db.commit()
    db.refresh(poliza)
    return _poliza(poliza)


@app.post("/polizas/{id_poliza}/siniestros", status_code=201, response_model=SiniestroSalida)
def declarar_siniestro(id_poliza: int, datos: SiniestroEntrada, db: Session = Depends(get_db)):
    siniestro = Siniestro(poliza_id=id_poliza, fecha=datos.fecha, monto=datos.monto,
                          descripcion=datos.descripcion, estado=datos.estado)
    db.add(siniestro)
    db.commit()
    db.refresh(siniestro)
    return {"id": siniestro.id, "poliza_id": siniestro.poliza_id, "fecha": siniestro.fecha,
            "monto": siniestro.monto, "descripcion": siniestro.descripcion, "estado": siniestro.estado}


@app.get("/siniestros", response_model=list[SiniestroConPoliza])
def listar_siniestros(db: Session = Depends(get_db)):
    return [_siniestro(s) for s in db.scalars(select(Siniestro).order_by(Siniestro.id))]


@app.get("/resumen", response_model=list[ResumenSalida])
def resumen(db: Session = Depends(get_db)):
    filas = []
    for p in db.scalars(select(Poliza).order_by(Poliza.id)):
        filas.append({"numero": p.numero, "n_siniestros": len(p.siniestros),
                      "monto_total": round(sum(s.monto for s in p.siniestros), 2)})
    return filas


@app.post("/score", response_model=ScoreSalida)
def puntuar(datos: PuntuacionEntrada, db: Session = Depends(get_db)):
    poliza = db.scalar(select(Poliza).where(Poliza.numero == datos.numero))
    if poliza is None:
        return {"error": f"no existe la póliza {datos.numero}"}
    rasgos = [[poliza.prima, len(poliza.siniestros), sum(s.monto for s in poliza.siniestros),
               (date.today() - poliza.fecha_inicio).days]]
    puntaje = float(modelo.predict_proba(rasgos)[0][1])
    prediccion = Prediccion(poliza_id=poliza.id, puntaje=puntaje,
                            alto_riesgo=puntaje > config.UMBRAL_ALTO_RIESGO)
    db.add(prediccion)
    db.commit()
    return {"numero": poliza.numero, "puntaje": round(puntaje, 4),
            "alto_riesgo": prediccion.alto_riesgo}


@app.get("/predicciones", response_model=list[PrediccionSalida])
def listar_predicciones(db: Session = Depends(get_db)):
    return [{"id": pr.id, "poliza_id": pr.poliza_id, "puntaje": pr.puntaje,
             "alto_riesgo": pr.alto_riesgo, "creado_en": pr.creado_en}
            for pr in db.scalars(select(Prediccion).order_by(Prediccion.id))]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
