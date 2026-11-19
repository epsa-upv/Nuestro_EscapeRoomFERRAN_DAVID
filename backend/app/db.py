"""Acceso a PostgreSQL con SQLAlchemy (Core + SQL en texto).

Cada petición usa una conexión propia (guardada en flask.g) dentro de una transacción:
- las rutas llaman a commit() cuando todo ha ido bien;
- si algo falla, al terminar la petición se hace rollback y no se guarda nada a medias.
"""
from flask import current_app, g
from sqlalchemy import create_engine, text

_motores = {}


def motor():
    url = current_app.config["DATABASE_URL"]
    if url not in _motores:
        _motores[url] = create_engine(
            url,
            pool_pre_ping=True,
            # Las fechas y horas del negocio son de Madrid
            connect_args={"options": f"-c timezone={current_app.config['ZONA_HORARIA']}"},
        )
    return _motores[url]


def conexion():
    if "conexion" not in g:
        g.conexion = motor().connect()
    return g.conexion


def todas(sql, **params):
    return [dict(f) for f in conexion().execute(text(sql), params).mappings().all()]


def una(sql, **params):
    fila = conexion().execute(text(sql), params).mappings().first()
    return dict(fila) if fila else None


def valor(sql, **params):
    return conexion().execute(text(sql), params).scalar()


def ejecutar(sql, **params):
    return conexion().execute(text(sql), params).rowcount


def commit():
    conexion().commit()


def cerrar(exc=None):
    c = g.pop("conexion", None)
    if c is not None:
        try:
            c.rollback()
        finally:
            c.close()


def init_app(app):
    app.teardown_appcontext(cerrar)
