"""Resultados (contrato, sección 6). Solo ADMIN.

GET  /api/resultados     -> 200 array
POST /api/resultados     {sesion_id, nombre_equipo, tiempo_minutos, superada} -> 201; 409 si ya existe

Los resultados de las partidas jugadas en la web los guarda el backend automáticamente.
"""
from flask import Blueprint, jsonify

from .. import serial
from .. import validacion as v
from ..auth import admin_requerido
from ..db import commit, todas, una
from ..errores import conflicto, regla, validacion
from .comun import creado

bp = Blueprint("resultados", __name__)

SELECT = "SELECT id, sesion_id, nombre_equipo, tiempo_minutos, superada FROM resultados"


@bp.get("/resultados")
@admin_requerido
def listar():
    return jsonify([serial.resultado(r) for r in todas(SELECT + " ORDER BY id")])


@bp.post("/resultados")
@admin_requerido
def crear():
    d = v.cuerpo()
    sesion_id = v.entero(d, "sesion_id", minimo=1)
    equipo = v.texto(d, "nombre_equipo", maximo=120)
    superada = v.booleano(d, "superada")
    tiempo = v.entero(d, "tiempo_minutos", minimo=0, maximo=1440, obligatorio=False)
    if superada and tiempo is None:
        raise validacion("Si la sala se ha superado hay que indicar 'tiempo_minutos'")
    if una("SELECT 1 AS x FROM sesiones WHERE id = :id", id=sesion_id) is None:
        raise regla("La sesión indicada no existe")
    if una("SELECT 1 AS x FROM resultados WHERE sesion_id = :id", id=sesion_id):
        raise conflicto("Esta sesión ya tiene un resultado")
    if una("SELECT 1 AS x FROM partidas WHERE sesion_id = :id AND estado IN ('PENDIENTE', 'EN_CURSO')", id=sesion_id):
        raise conflicto("La partida de esta sesión todavía no ha terminado")
    r = una(
        """INSERT INTO resultados (sesion_id, nombre_equipo, tiempo_minutos, superada)
           VALUES (:s, :e, :t, :sup) RETURNING id, sesion_id, nombre_equipo, tiempo_minutos, superada""",
        s=sesion_id, e=equipo, t=tiempo if superada else None, sup=superada,
    )
    commit()
    return creado(serial.resultado(r), f"/api/resultados/{r['id']}")
