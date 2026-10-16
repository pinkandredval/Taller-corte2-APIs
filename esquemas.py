"""Esquemas de entrada."""
from datetime import date,datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class SiniestroEntrada(BaseModel):
    fecha: date
    monto: float = Field(gt=0, description="Monto reclamado, en pesos")
    descripcion: str = Field(min_length=3, max_length=200)
    estado: str = "abierto"


class PolizaEntrada(BaseModel):
    numero: str = Field(min_length=8, max_length=20, description="Formato POL-AAAA-NNNNN")
    asegurado: str = Field(min_length=3, max_length=80)
    tipo: Literal["auto", "hogar", "vida"] = Field(description="auto, hogar o vida")
    prima: float = Field(gt=0, description="Prima anual, en pesos")
    fecha_inicio: date
    fecha_fin: date
    siniestros: list[SiniestroEntrada] = Field(default_factory=list, description="Siniestros ya declarados")

    @field_validator("asegurado")
    @classmethod
    def normalizar_asegurado(cls, v: str) -> str:
        """Quita espacios sobrantes y pone el nombre con mayúscula inicial."""
        return " ".join(v.split()).title()
    @model_validator(mode="after")
    def validar_fechas(self):
        """Verifica que fecha_fin sea posterior a fecha_inicio."""
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return self


class PolizaActualizacion(BaseModel):
    asegurado: Optional[str] = Field(default=None, min_length=3, max_length=80)
    tipo: Optional[Literal["auto", "hogar", "vida"]] = Field(default=None, description="auto, hogar o vida")
    prima: Optional[float] = Field(default=None, gt=0)
    fecha_fin: Optional[date] = None


class PuntuacionEntrada(BaseModel):
    numero: str = Field(min_length=8, max_length=20)

class SiniestroSalida(BaseModel):
    id: int
    fecha: date
    monto: float
    descripcion: str
    estado: str

    model_config = {"from_attributes": True}

class PolizaSalida(BaseModel):
    id: int
    numero: str
    asegurado: Optional[str]
    tipo: Optional[str]
    prima: float
    fecha_inicio: date
    fecha_fin: Optional[date]
    siniestros: list[SiniestroSalida] = []
    model_config = {"from_attributes": True}

class PrediccionSalida(BaseModel):
    id: int
    poliza_id: int
    puntaje: float
    alto_riesgo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


class ScoreSalida(BaseModel):
    numero: str
    puntaje: float
    alto_riesgo: bool


class ResumenSalida(BaseModel):
    numero: str
    n_siniestros: int
    monto_total: float
    
class HealthSalida(BaseModel):
    status: str
    database: str


class SiniestroConPoliza(BaseModel):
    id: int
    poliza_id: int
    numero_poliza: str
    fecha: date
    monto: float
    descripcion: str
    estado: str