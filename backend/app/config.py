"""Configuración leída de variables de entorno (archivo .env)."""
import os
from pathlib import Path

def _carpeta_src():
    """Carpeta de la web (index.html, js/, db/...). Vale para las dos organizaciones:
    - backend/ en la raíz del repo  ->  <repo>/src
    - src/backend/                  ->  <repo>/src
    """
    backend = Path(__file__).resolve().parents[1]
    for candidata in (backend.parent / "src", backend.parent):
        if (candidata / "index.html").exists() or (candidata / "db").is_dir():
            return candidata
    return backend.parent / "src"


CARPETA_SRC = _carpeta_src()


def url_bd(url):
    """SQLAlchemy necesita saber el driver: postgresql:// -> postgresql+psycopg://"""
    if url and url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Config:
    DATABASE_URL = url_bd(os.environ.get(
        "DATABASE_URL", "postgresql+psycopg://escapeuser:escape2026@localhost:5432/escapehub"
    ))
    SECRET_KEY = os.environ.get("SECRET_KEY")
    RESPUESTA_SECRET = os.environ.get("RESPUESTA_SECRET")
    TOKEN_HORAS = int(os.environ.get("TOKEN_HORAS", "8"))
    ZONA_HORARIA = "Europe/Madrid"
    FRONTEND_DIR = str(CARPETA_SRC)
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
    MAX_INTENTOS_LOGIN = 3
    HORAS_CANCELACION = 24
    MINUTOS_ANTES_INICIO = 15
