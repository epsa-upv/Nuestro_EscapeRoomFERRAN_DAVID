"""Usuarios y autenticación (contrato, sección 2).

POST /api/auth/registro   Público  -> 201 {id, nombre, email, rol}
POST /api/auth/login      Público  -> 200 {access_token, usuario}

- Contraseñas con hash y sal única (Werkzeug).
- 3 contraseñas incorrectas seguidas -> cuenta bloqueada (403 CUENTA_BLOQUEADA).
"""
from flask import Blueprint, current_app, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from .. import serial
from .. import validacion as v
from ..auth import crear_token
from ..db import commit, ejecutar, una
from ..errores import conflicto, cuenta_bloqueada, no_autenticado, validacion
from .comun import creado

bp = Blueprint("auth", __name__)

LONGITUD_MINIMA = 8


@bp.post("/auth/registro")
def registro():
    d = v.cuerpo()
    nombre = v.texto(d, "nombre", maximo=100, minimo=2)
    email = v.email(d)
    password = d.get("password")
    if not isinstance(password, str) or len(password) < LONGITUD_MINIMA:
        raise validacion(f"La contraseña debe tener al menos {LONGITUD_MINIMA} caracteres")
    if len(password) > 128:
        raise validacion("La contraseña es demasiado larga")
    if una("SELECT 1 AS x FROM usuarios WHERE lower(email) = :e", e=email):
        raise conflicto("Ya existe un usuario con ese email")

    u = una(
        """INSERT INTO usuarios (nombre, email, password_hash)
           VALUES (:n, :e, :h) RETURNING id, nombre, email, rol""",
        n=nombre, e=email, h=generate_password_hash(password),
    )
    commit()
    return creado(serial.usuario(u), f"/api/usuarios/{u['id']}")


@bp.post("/auth/login")
def login():
    d = v.cuerpo()
    email = d.get("email")
    password = d.get("password")
    if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
        raise validacion("Indica email y contraseña")

    u = una(
        """SELECT id, nombre, email, rol, password_hash, intentos_fallidos, bloqueado
           FROM usuarios WHERE lower(email) = :e""",
        e=email.strip().lower(),
    )
    if u is None:
        raise no_autenticado("Email o contraseña incorrectos")
    if u["bloqueado"]:
        raise cuenta_bloqueada()

    if not _password_correcta(u["password_hash"], password):
        intentos = u["intentos_fallidos"] + 1
        bloquear = intentos >= current_app.config["MAX_INTENTOS_LOGIN"]
        ejecutar("UPDATE usuarios SET intentos_fallidos = :i, bloqueado = :b WHERE id = :id",
                 i=intentos, b=bloquear, id=u["id"])
        commit()
        if bloquear:
            raise cuenta_bloqueada()
        raise no_autenticado("Email o contraseña incorrectos")

    if u["intentos_fallidos"]:
        ejecutar("UPDATE usuarios SET intentos_fallidos = 0 WHERE id = :id", id=u["id"])
        commit()
    return jsonify(access_token=crear_token(u["id"]), usuario=serial.usuario(u))


def _password_correcta(hash_guardado, password):
    # Los hashes ficticios del seed del Sprint 2 no tienen formato Werkzeug
    try:
        return check_password_hash(hash_guardado, password)
    except (ValueError, TypeError):
        return False
