"""Autenticación por token firmado y control de permisos.

El cliente envía en cada petición privada:  Authorization: Bearer <token>
El rol se lee SIEMPRE de la base de datos, nunca del cliente.
"""
from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from .db import una
from .errores import cuenta_bloqueada, no_autenticado, prohibido


def _firmador():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="escapehub-token")


def crear_token(usuario_id):
    return _firmador().dumps({"id": usuario_id})


def _usuario_actual():
    cabecera = request.headers.get("Authorization", "")
    if not cabecera.startswith("Bearer "):
        raise no_autenticado()
    try:
        datos = _firmador().loads(cabecera[7:].strip(), max_age=current_app.config["TOKEN_HORAS"] * 3600)
    except SignatureExpired:
        raise no_autenticado("La sesión ha caducado; vuelve a iniciar sesión")
    except BadSignature:
        raise no_autenticado("Token no válido")
    u = una("SELECT id, nombre, email, rol, bloqueado FROM usuarios WHERE id = :id", id=datos.get("id"))
    if u is None:
        raise no_autenticado("El usuario ya no existe")
    if u["bloqueado"]:
        raise cuenta_bloqueada()
    return u


def login_requerido(f):
    @wraps(f)
    def envoltura(*a, **k):
        g.usuario = _usuario_actual()
        return f(*a, **k)
    return envoltura


def admin_requerido(f):
    @wraps(f)
    def envoltura(*a, **k):
        g.usuario = _usuario_actual()
        if g.usuario["rol"] != "ADMIN":
            raise prohibido("Solo un administrador puede realizar esta acción")
        return f(*a, **k)
    return envoltura


def jugador_requerido(f):
    @wraps(f)
    def envoltura(*a, **k):
        g.usuario = _usuario_actual()
        if g.usuario["rol"] != "JUGADOR":
            raise prohibido("Esta acción solo la puede realizar un jugador")
        return f(*a, **k)
    return envoltura


def es_admin():
    return g.get("usuario") is not None and g.usuario["rol"] == "ADMIN"
