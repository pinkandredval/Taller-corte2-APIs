"""Conexión a la base de datos."""

import sqlite3

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import config


class Base(DeclarativeBase):
    pass


engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@event.listens_for(Engine, "connect")
def activar_fk_sqlite(dbapi_conn, connection_record):
    """Activa PRAGMA foreign_keys en SQLite (H18)."""
    if isinstance(dbapi_conn, sqlite3.Connection):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db():
    """Entrega una sesión por petición. Se cierra al finalizar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()