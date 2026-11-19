"""Preparación de las pruebas.

Antes de CADA prueba se borra la base de datos de pruebas y se vuelve a crear con:
    schema.sql + seed.sql (Sprint 2) + ampliacion_sprint3.sql (+ migracion_sprint3.sql)
y se cargan los datos demo (contraseñas y retos de ejemplo).

Usa TEST_DATABASE_URL (por defecto escapehub_test). ¡Nunca la base de datos de trabajo!
"""
import os
from pathlib import Path

import psycopg
import pytest

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from app import create_app
from app.demo import cargar_demo

TEST_DB = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://escapeuser:escape2026@localhost:5432/escapehub_test"
)
DSN = TEST_DB.replace("postgresql+psycopg://", "postgresql://")
DIR_SQL = Path(__file__).resolve().parents[2] / "db"
PASSWORD = "Demo2026!"


def reiniciar_bd(migracion=True):
    scripts = ["schema.sql", "seed.sql", "ampliacion_sprint3.sql"]
    if migracion:
        scripts.append("migracion_sprint3.sql")
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")
        for nombre in scripts:
            conn.execute((DIR_SQL / nombre).read_text(encoding="utf-8"))
        # El seed se escribió para el 04/11/2026: se mueven las sesiones los días que hayan
        # pasado, para que las sesiones "futuras" sigan siéndolo el día de la prueba.
        # (en dos pasos para no chocar con la restricción UNIQUE mientras se actualiza)
        conn.execute("UPDATE sesiones SET fecha = fecha + 10000")
        conn.execute("UPDATE sesiones SET fecha = fecha - 10000 + GREATEST(CURRENT_DATE - DATE '2026-11-04', 0)")


def _crear_app(migracion):
    # Cerrar las conexiones del pool: las tablas se acaban de recrear
    from app import db
    for motor in db._motores.values():
        motor.dispose()
    db._motores.clear()
    reiniciar_bd(migracion)
    app = create_app({"TESTING": True, "DATABASE_URL": TEST_DB,
                      "SECRET_KEY": "clave-pruebas", "RESPUESTA_SECRET": "secreto-pruebas"})
    with app.app_context():
        cargar_demo(password=PASSWORD)
    return app


@pytest.fixture
def app():
    return _crear_app(migracion=True)


@pytest.fixture
def app_sin_migracion():
    return _crear_app(migracion=False)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def client_sin_migracion(app_sin_migracion):
    return app_sin_migracion.test_client()


@pytest.fixture
def bd():
    """Consultas directas a la BD para comprobar lo que se ha guardado."""
    def consulta(sql, params=None):
        with psycopg.connect(DSN) as conn:
            cur = conn.execute(sql, params)
            return cur.fetchall() if cur.description else None
    return consulta


def login(client, email, password=PASSWORD):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.get_json()
    return {"Authorization": "Bearer " + r.get_json()["access_token"]}


@pytest.fixture
def admin(client):
    return login(client, "ferran@escapehub.es")


@pytest.fixture
def marta(client):
    return login(client, "marta.garcia@mail.com")


@pytest.fixture
def javier(client):
    return login(client, "javi.perez@mail.com")


def momento(bd, minutos):
    """Fecha y hora de Madrid dentro de N minutos, como texto (AAAA-MM-DD, HH:mm)."""
    (f, h), = bd("""SELECT to_char(t, 'YYYY-MM-DD'), to_char(t, 'HH24:MI') FROM (
                        SELECT date_trunc('minute', now() AT TIME ZONE 'Europe/Madrid')
                               + make_interval(mins => %s) AS t) x""", (minutos,))
    return f, h


def crear_sesion(client, admin, bd, sala_id=1, minutos=10):
    f, h = momento(bd, minutos)
    r = client.post("/api/sesiones", json={"sala_id": sala_id, "fecha": f, "hora_inicio": h}, headers=admin)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["id"]


def reservar(client, jugador, sesion_id, n=2):
    r = client.post("/api/reservas", json={"sesion_id": sesion_id, "numero_jugadores": n}, headers=jugador)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["id"]


def partida_en_curso(client, admin, jugador, bd, sala_id=1):
    sesion = crear_sesion(client, admin, bd, sala_id=sala_id, minutos=10)
    reserva = reservar(client, jugador, sesion)
    p = client.post("/api/partidas", json={"reserva_id": reserva}, headers=jugador).get_json()
    r = client.post(f"/api/partidas/{p['id']}/iniciar", json={}, headers=jugador)
    assert r.status_code == 200, r.get_json()
    return r.get_json()


def error(resp):
    return resp.get_json()["error"]["codigo"]
