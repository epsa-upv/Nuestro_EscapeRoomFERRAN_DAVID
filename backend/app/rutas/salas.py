"""Salas (contrato, sección 3).

GET    /api/salas            Público  (?activa=true|false opcional)
GET    /api/salas/{id}       Público
POST   /api/salas            ADMIN    -> 201
PUT    /api/salas/{id}       ADMIN    representación completa
DELETE /api/salas/{id}       ADMIN    -> 204; 409 si tiene sesiones, retos u objetos
"""
from flask import Blueprint, jsonify

from .. import serial
from .. import validacion as v
from ..auth import admin_requerido
from ..db import commit, todas, una, valor
from ..errores import conflicto, no_encontrado, regla
from .comun import creado, sin_contenido

bp = Blueprint("salas", __name__)

DIFICULTADES = ("BAJA", "MEDIA", "ALTA")
SELECT = "SELECT id, nombre, tematica, dificultad, duracion_minutos, capacidad, activa FROM salas"


def obtener_sala(sala_id):
    s = una(SELECT + " WHERE id = :id", id=sala_id)
    if s is None:
        raise no_encontrado("La sala no existe")
    return s


def _nombre_libre(nombre, excepto=0):
    if una("SELECT 1 AS x FROM salas WHERE lower(nombre) = lower(:n) AND id <> :id", n=nombre, id=excepto):
        raise conflicto("Ya existe una sala con ese nombre")


def _datos(d, completa):
    return {
        "nombre": v.texto(d, "nombre", maximo=120),
        "tematica": v.texto(d, "tematica", maximo=80),
        "dificultad": v.opcion(d, "dificultad", DIFICULTADES),
        "duracion": v.entero(d, "duracion_minutos", minimo=1, maximo=600, obligatorio=completa),
        "capacidad": v.entero(d, "capacidad", minimo=2, maximo=50),
        "activa": v.booleano(d, "activa", obligatorio=completa),
    }


@bp.get("/salas")
def listar():
    activa = v.param_bool("activa")
    if activa is None:
        return jsonify([serial.sala(s) for s in todas(SELECT + " ORDER BY id")])
    return jsonify([serial.sala(s) for s in todas(SELECT + " WHERE activa = :a ORDER BY id", a=activa)])


@bp.get("/salas/<int:sala_id>")
def ver(sala_id):
    return jsonify(serial.sala(obtener_sala(sala_id)))


@bp.post("/salas")
@admin_requerido
def crear():
    x = _datos(v.cuerpo(), completa=False)
    _nombre_libre(x["nombre"])
    s = una(
        """INSERT INTO salas (nombre, tematica, dificultad, duracion_minutos, capacidad, activa)
           VALUES (:nombre, :tematica, :dificultad, :duracion, :capacidad, :activa)
           RETURNING id, nombre, tematica, dificultad, duracion_minutos, capacidad, activa""",
        nombre=x["nombre"], tematica=x["tematica"], dificultad=x["dificultad"],
        duracion=x["duracion"] or 60, capacidad=x["capacidad"],
        activa=True if x["activa"] is None else x["activa"],
    )
    commit()
    return creado(serial.sala(s), f"/api/salas/{s['id']}")


@bp.put("/salas/<int:sala_id>")
@admin_requerido
def modificar(sala_id):
    obtener_sala(sala_id)
    x = _datos(v.cuerpo(), completa=True)
    _nombre_libre(x["nombre"], excepto=sala_id)
    # No dejar reservas futuras con más jugadores que la nueva capacidad
    maximo = valor(
        """SELECT COALESCE(MAX(r.numero_jugadores), 0)
           FROM reservas r JOIN sesiones se ON se.id = r.sesion_id
           WHERE se.sala_id = :id AND r.estado = 'ACTIVA' AND se.fecha >= CURRENT_DATE""",
        id=sala_id,
    )
    if x["capacidad"] < maximo:
        raise regla(f"Hay reservas futuras de {maximo} jugadores; la capacidad no puede ser menor")
    s = una(
        """UPDATE salas SET nombre = :nombre, tematica = :tematica, dificultad = :dificultad,
                  duracion_minutos = :duracion, capacidad = :capacidad, activa = :activa
           WHERE id = :id
           RETURNING id, nombre, tematica, dificultad, duracion_minutos, capacidad, activa""",
        id=sala_id, **x,
    )
    commit()
    return jsonify(serial.sala(s))


@bp.delete("/salas/<int:sala_id>")
@admin_requerido
def eliminar(sala_id):
    obtener_sala(sala_id)
    if una("SELECT 1 AS x FROM sesiones WHERE sala_id = :id LIMIT 1", id=sala_id):
        raise conflicto("La sala tiene sesiones vinculadas; desactívala en lugar de eliminarla")
    if una("""SELECT 1 AS x FROM retos WHERE sala_id = :id
              UNION ALL SELECT 1 FROM objetos WHERE sala_id = :id LIMIT 1""", id=sala_id):
        raise conflicto("La sala tiene retos u objetos configurados; elimínalos antes")
    una("DELETE FROM salas WHERE id = :id RETURNING id", id=sala_id)
    commit()
    return sin_contenido()
