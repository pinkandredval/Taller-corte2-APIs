"""Configuración del servicio cargada desde variables de entorno."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración tipada leída desde .env."""

    secreto_firma: str
    clave_api_reaseguro: str
    database_url: str = "sqlite:///app.db"
    ruta_modelo: str = "modelo.pkl"
    umbral_alto_riesgo: float = 0.6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración cacheada (se instancia una sola vez)."""
    return Settings()

# --- Variables de módulo temporales para compatibilidad ---
# Se eliminarán en la Parte B cuando se refactorice database.py y main.py.
settings = get_settings()
SECRETO_FIRMA = settings.secreto_firma
CLAVE_API_REASEGURO = settings.clave_api_reaseguro
DATABASE_URL = settings.database_url
RUTA_MODELO = settings.ruta_modelo
UMBRAL_ALTO_RIESGO = settings.umbral_alto_riesgo