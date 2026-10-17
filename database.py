"""Conexión a la base de datos."""

import sqlite3
from functools import lru_cache

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine():
    """Crea el motor de BD una sola vez, leyendo la configuración."""
    settings = get_settings()
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    return create_engine(settings.database_url, connect_args=connect_args)


@event.listens_for(Engine, "connect")
def activar_fk_sqlite(dbapi_conn, connection_record):
    """Activa PRAGMA foreign_keys en SQLite (H22)."""
    if isinstance(dbapi_conn, sqlite3.Connection):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db():
    """Entrega una sesión por petición. Se cierra al finalizar."""
    SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()