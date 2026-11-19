"""Sesiones (contrato, sección 4).

GET    /api/sesiones          Público  (?sala_id= &fecha= &estado= opcionales)
GET    /api/sesiones/{id}     Público
POST   /api/sesiones          ADMIN    -> 201
PUT    /api/sesiones/{id}     ADMIN    representación completa
DELETE /api/sesiones/{id}     ADMIN    -> 204; 409 si tiene reservas o resultados
"""
from flask import Blueprint, jsonify, request

from .. import serial
from .. import validacion as v
from ..auth import admin_requerido
from ..db import commit, ejecutar, todas, una
from ..errores import conflicto, no_encontrado, regla
from .comun import creado, sin_contenido

bp = Blueprint("sesiones", __name__)

ESTADOS = ("DISPONIBLE", "RESERVADA", "CANCELADA")
SELECT = """
    SELECT se.id, se.sala_id, se.fecha, se.hora_inicio, se.estado,
           sa.nombre AS sala_nombre, sa.capacidad AS sala_capacidad,
           sa.duracion_minutos AS sala_duracion
    FROM sesiones se JOIN salas sa ON sa.id = se.sala_id
"""


def obtener_sesion(sesion_id):
    s = una(SELECT + " WHERE se.id = :id", id=sesion_id)
    if s is None:
        raise no_encontrado("La sesión no existe")
    return s


def _es_futura(fecha, hora):
    return una(
        "SELECT ((CAST(:f AS date) + CAST(:h AS time)) AT TIME ZONE 'Europe/Madrid') > now() AS futura",
        f=fecha, h=hora,
    )["futura"]


def _sala_activa(sala_id):
    s = una("SELECT activa FROM salas WHERE id = :id", id=sala_id)
    if s is None:
        raise regla("La sala indicada no existe")
    if not s["activa"]:
        raise regla("La sala no está activa")


def _sin_duplicado(sala_id, fecha, hora, excepto=0):
    if una("""SELECT 1 AS x FROM sesiones WHERE sala_id = :s AND fecha = :f AND hora_inicio = :h
              AND id <> :id""", s=sala_id, f=fecha, h=hora, id=excepto):
        raise conflicto("Ya existe una sesión en esa sala a esa fecha y hora")


@bp.get("/sesiones")
def listar():
    condiciones, p = [], {}
    sala_id = v.param_entero("sala_id")
    if sala_id is not None:
        condiciones.append("se.sala_id = :sala_id")
        p["sala_id"] = sala_id
    if request.args.get("fecha"):
        condiciones.append("se.fecha = :fecha")
        p["fecha"] = v.fecha(request.args["fecha"], "fecha")
    estado = v.param_opcion("estado", ESTADOS)
    if estado:
        condiciones.append("se.estado = :estado")
        p["estado"] = estado
    sql = SELECT + (" WHERE " + " AND ".join(condiciones) if condiciones else "")
    return jsonify([serial.sesion(s) for s in todas(sql + " ORDER BY se.fecha, se.hora_inicio", **p)])


@bp.get("/sesiones/<int:sesion_id>")
def ver(sesion_id):
    return jsonify(serial.sesion(obtener_sesion(sesion_id)))


@bp.post("/sesiones")
@admin_requerido
def crear():
    d = v.cuerpo()
    sala_id = v.entero(d, "sala_id", minimo=1)
    fecha = v.fecha(d.get("fecha"))
    hora = v.hora(d.get("hora_inicio"))
    _sala_activa(sala_id)
    if not _es_futura(fecha, hora):
        raise regla("No se pueden crear sesiones en el pasado")
    _sin_duplicado(sala_id, fecha, hora)
    nueva = una("INSERT INTO sesiones (sala_id, fecha, hora_inicio) VALUES (:s, :f, :h) RETURNING id",
                s=sala_id, f=fecha, h=hora)
    commit()
    return creado(serial.sesion(obtener_sesion(nueva["id"])), f"/api/sesiones/{nueva['id']}")


@bp.put("/sesiones/<int:sesion_id>")
@admin_requerido
def modificar(sesion_id):
    actual = obtener_sesion(sesion_id)
    d = v.cuerpo()
    sala_id = v.entero(d, "sala_id", minimo=1)
    fecha = v.fecha(d.get("fecha"))
    hora = v.hora(d.get("hora_inicio"))
    estado = v.opcion(d, "estado", ESTADOS)

    reserva = una("SELECT id FROM reservas WHERE sesion_id = :id AND estado = 'ACTIVA'", id=sesion_id)
    cambia_horario = (sala_id, fecha, hora) != (actual["sala_id"], actual["fecha"], actual["hora_inicio"])
    if cambia_horario:
        if reserva:
            raise conflicto("No se puede cambiar sala, fecha u hora de una sesión con reserva activa")
        _sala_activa(sala_id)
        if not _es_futura(fecha, hora):
            raise regla("No se pueden poner sesiones en el pasado")
        _sin_duplicado(sala_id, fecha, hora, excepto=sesion_id)

    if estado == "DISPONIBLE" and reserva:
        raise conflicto("La sesión tiene una reserva activa; cancela la reserva primero")
    if estado == "RESERVADA" and not reserva:
        raise regla("Una sesión solo está RESERVADA cuando tiene una reserva activa")
    if estado == "CANCELADA" and reserva:
        partida = una("SELECT estado FROM partidas WHERE reserva_id = :r", r=reserva["id"])
        if partida and partida["estado"] != "PENDIENTE":
            raise conflicto("La partida de esta sesión ya ha empezado")
        ejecutar("DELETE FROM partidas WHERE reserva_id = :r AND estado = 'PENDIENTE'", r=reserva["id"])
        ejecutar("UPDATE reservas SET estado = 'CANCELADA' WHERE id = :r", r=reserva["id"])

    ejecutar("""UPDATE sesiones SET sala_id = :s, fecha = :f, hora_inicio = :h, estado = :e
                WHERE id = :id""", s=sala_id, f=fecha, h=hora, e=estado, id=sesion_id)
    commit()
    return jsonify(serial.sesion(obtener_sesion(sesion_id)))


@bp.delete("/sesiones/<int:sesion_id>")
@admin_requerido
def eliminar(sesion_id):
    obtener_sesion(sesion_id)
    if una("""SELECT 1 AS x FROM reservas WHERE sesion_id = :id
              UNION ALL SELECT 1 FROM resultados WHERE sesion_id = :id LIMIT 1""", id=sesion_id):
        raise conflicto("La sesión tiene reservas o resultados; cámbiala a CANCELADA")
    ejecutar("DELETE FROM sesiones WHERE id = :id", id=sesion_id)
    commit()
    return sin_contenido()
