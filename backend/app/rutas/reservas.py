"""Reservas (contrato, sección 5).

GET /api/reservas          Autenticado (?estado= opcional). JUGADOR: las suyas; ADMIN: todas
GET /api/reservas/{id}     Titular o ADMIN (ruta adicional, no rompe el contrato)
POST /api/reservas         JUGADOR  {sesion_id, numero_jugadores} -> 201
PUT /api/reservas/{id}     Titular o ADMIN  {"estado": "CANCELADA"}

Reglas:
- El usuario se toma del token, nunca del cuerpo.
- La sesión se bloquea (SELECT ... FOR UPDATE) dentro de la transacción: no hay dobles reservas.
- Jugadores entre 2 y la capacidad de la sala (422).
- Un jugador solo puede cancelar hasta 24 h antes (RF-08); el administrador, hasta que empiece.
"""
from flask import Blueprint, current_app, g, jsonify
from sqlalchemy import exc as sa_exc

from .. import serial
from .. import validacion as v
from ..auth import es_admin, jugador_requerido, login_requerido
from ..db import commit, conexion, ejecutar, todas, una
from ..errores import conflicto, no_encontrado, prohibido, regla, validacion
from .comun import INICIO_SESION_SQL, creado

bp = Blueprint("reservas", __name__)

MIN_JUGADORES = 2
SELECT = """
    SELECT r.id, r.usuario_id, r.sesion_id, r.numero_jugadores, r.estado,
           (r.fecha_reserva AT TIME ZONE 'Europe/Madrid') AS fecha_reserva,
           se.sala_id, se.fecha, se.hora_inicio, sa.nombre AS sala_nombre
    FROM reservas r
    JOIN sesiones se ON se.id = r.sesion_id
    JOIN salas sa    ON sa.id = se.sala_id
"""


def obtener_reserva(reserva_id):
    r = una(SELECT + " WHERE r.id = :id", id=reserva_id)
    if r is None:
        raise no_encontrado("La reserva no existe")
    if r["usuario_id"] != g.usuario["id"] and not es_admin():
        raise prohibido("Esta reserva no es tuya")
    return r


@bp.get("/reservas")
@login_requerido
def listar():
    condiciones, p = [], {}
    estado = v.param_opcion("estado", ("ACTIVA", "CANCELADA"))
    if estado:
        condiciones.append("r.estado = :estado")
        p["estado"] = estado
    if not es_admin():
        condiciones.append("r.usuario_id = :yo")
        p["yo"] = g.usuario["id"]
    sql = SELECT + (" WHERE " + " AND ".join(condiciones) if condiciones else "")
    return jsonify([serial.reserva(r) for r in todas(sql + " ORDER BY se.fecha, se.hora_inicio, r.id", **p)])


@bp.get("/reservas/<int:reserva_id>")
@login_requerido
def ver(reserva_id):
    return jsonify(serial.reserva(obtener_reserva(reserva_id)))


@bp.post("/reservas")
@jugador_requerido
def crear():
    d = v.cuerpo()
    sesion_id = v.entero(d, "sesion_id", minimo=1)
    jugadores = v.entero(d, "numero_jugadores")

    sesion = una(
        f"""SELECT se.id, se.estado, sa.capacidad, sa.activa,
                   {INICIO_SESION_SQL} <= now() AS empezada
            FROM sesiones se JOIN salas sa ON sa.id = se.sala_id
            WHERE se.id = :id
            FOR UPDATE OF se""",
        id=sesion_id,
    )
    if sesion is None:
        raise no_encontrado("La sesión no existe")
    if not sesion["activa"]:
        raise regla("La sala de esta sesión no está activa")
    if sesion["empezada"]:
        raise regla("No se pueden reservar sesiones pasadas o ya empezadas")
    if sesion["estado"] != "DISPONIBLE":
        raise conflicto("La sesión no está disponible")
    if not MIN_JUGADORES <= jugadores <= sesion["capacidad"]:
        raise regla(f"El número de jugadores debe estar entre {MIN_JUGADORES} y {sesion['capacidad']}")

    try:
        nueva = una("""INSERT INTO reservas (usuario_id, sesion_id, numero_jugadores)
                       VALUES (:u, :s, :n) RETURNING id""",
                    u=g.usuario["id"], s=sesion_id, n=jugadores)
    except sa_exc.IntegrityError:
        # Sin la migración A, una sesión con una reserva cancelada no se puede volver a reservar
        conexion().rollback()
        raise conflicto("La sesión no está disponible")
    ejecutar("UPDATE sesiones SET estado = 'RESERVADA' WHERE id = :id", id=sesion_id)
    commit()
    return creado(serial.reserva(obtener_reserva(nueva["id"])), f"/api/reservas/{nueva['id']}")


@bp.put("/reservas/<int:reserva_id>")
@login_requerido
def modificar(reserva_id):
    d = v.cuerpo()
    estado = v.opcion(d, "estado", ("ACTIVA", "CANCELADA"))
    if estado != "CANCELADA":
        raise validacion("Solo se puede cambiar el estado a CANCELADA")

    obtener_reserva(reserva_id)  # 404 / 403
    r = una(
        f"""SELECT r.id, r.estado, r.sesion_id,
                   {INICIO_SESION_SQL} <= now() AS empezada,
                   {INICIO_SESION_SQL} - now() < make_interval(hours => :horas) AS fuera_de_plazo
            FROM reservas r JOIN sesiones se ON se.id = r.sesion_id
            WHERE r.id = :id FOR UPDATE OF r""",
        id=reserva_id, horas=current_app.config["HORAS_CANCELACION"],
    )
    if r["estado"] == "CANCELADA":
        raise conflicto("La reserva ya está cancelada")
    if r["empezada"]:
        raise regla("No se puede cancelar una reserva de una sesión que ya ha empezado")
    if r["fuera_de_plazo"] and not es_admin():
        raise regla(f"Solo se puede cancelar hasta {current_app.config['HORAS_CANCELACION']} horas antes de la sesión")
    partida = una("SELECT estado FROM partidas WHERE reserva_id = :id", id=reserva_id)
    if partida and partida["estado"] != "PENDIENTE":
        raise conflicto("La partida de esta reserva ya ha empezado")

    ejecutar("DELETE FROM partidas WHERE reserva_id = :id AND estado = 'PENDIENTE'", id=reserva_id)
    ejecutar("UPDATE reservas SET estado = 'CANCELADA' WHERE id = :id", id=reserva_id)
    ejecutar("UPDATE sesiones SET estado = 'DISPONIBLE' WHERE id = :s AND estado = 'RESERVADA'", s=r["sesion_id"])
    commit()
    return jsonify(serial.reserva(obtener_reserva(reserva_id)))
