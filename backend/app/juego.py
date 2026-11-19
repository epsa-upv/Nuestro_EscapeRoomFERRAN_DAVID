"""Utilidades del juego: verificador HMAC de respuestas y detección de la migración.

- Las soluciones NUNCA se guardan en claro: se normalizan y se guarda HMAC-SHA256
  con el secreto RESPUESTA_SECRET del servidor (columna retos.respuesta_hash).
- Las funciones de la migración propuesta (opciones_reto, retos.objeto_requerido_id,
  objetos.reto_desbloqueo_id) solo se usan si existen en la base de datos.
"""
import hashlib
import hmac
import unicodedata

from flask import current_app

from .db import una
from .errores import regla


def normalizar(texto):
    """Sin mayúsculas, tildes ni espacios sobrantes: '  Génoma ' == 'genoma'."""
    t = unicodedata.normalize("NFKD", texto.strip().casefold())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.split())


def hash_respuesta(texto):
    secreto = current_app.config["RESPUESTA_SECRET"].encode()
    return hmac.new(secreto, normalizar(texto).encode(), hashlib.sha256).hexdigest()


def respuesta_correcta(texto, hash_guardado):
    return bool(hash_guardado) and hmac.compare_digest(hash_respuesta(texto), hash_guardado)


def funciones():
    """Qué partes de la migración propuesta están instaladas en la BD."""
    return {
        "opciones": una("SELECT to_regclass('public.opciones_reto') IS NOT NULL AS x")["x"],
        "objeto_requerido": una(
            """SELECT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name = 'retos' AND column_name = 'objeto_requerido_id') AS x""")["x"],
        "desbloqueo_objetos": una(
            """SELECT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name = 'objetos' AND column_name = 'reto_desbloqueo_id') AS x""")["x"],
    }


def exigir(funcion, que):
    if not funciones()[funcion]:
        raise regla(f"{que} todavía no está disponible: falta aplicar migracion_sprint3.sql (pendiente de acordar)")
