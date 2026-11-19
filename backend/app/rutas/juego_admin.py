"""Retos, pistas, objetos y dependencias - administración (contrato, sección 7).

GET    /api/salas/{sala_id}/retos        ADMIN  retos SIN hash ni solución (+ pistas, prerrequisitos y opciones)
POST   /api/salas/{sala_id}/retos        ADMIN  {titulo, descripcion, tipo, orden, activo, respuesta?} -> 201
PUT    /api/retos/{id}                   ADMIN  representación completa; 'respuesta' opcional
DELETE /api/retos/{id}                   ADMIN  -> 204; 409 si hay partidas que lo han usado
POST   /api/retos/{id}/pistas            ADMIN  {orden, contenido, penalizacion_segundos} -> 201
POST   /api/salas/{sala_id}/objetos      ADMIN  {nombre, descripcion, activo} -> 201
GET    /api/salas/{sala_id}/objetos      ADMIN  (ruta adicional)
POST   /api/retos/{id}/dependencias      ADMIN  {prerequisito_id} -> 201; 422 si crea un ciclo

Campos adicionales (solo si se aplica migracion_sprint3.sql):
- reto OPCION:  "opciones": ["texto 1", "texto 2", ...]  (la 'respuesta' debe ser una de ellas)
- reto OBJETO:  "objeto_requerido_id": id de un objeto de la misma sala
- objeto:       "reto_desbloqueo_id": reto que hay que completar para poder recogerlo
"""
from flask import Blueprint, jsonify

from .. import validacion as v
from ..auth import admin_requerido
from ..db import commit, ejecutar, todas, una, valor
from ..errores import conflicto, no_encontrado, regla, validacion
from ..juego import exigir, funciones, hash_respuesta, normalizar
from .comun import creado, sin_contenido
from .salas import obtener_sala

bp = Blueprint("juego_admin", __name__)

TIPOS = ("CODIGO", "TEXTO", "OPCION", "OBJETO")


def _reto_publico(r, f):
    datos = {
        "id": r["id"], "sala_id": r["sala_id"], "titulo": r["titulo"], "descripcion": r["descripcion"],
        "tipo": r["tipo"], "orden": r["orden"], "activo": r["activo"],
    }
    if f["objeto_requerido"]:
        datos["objeto_requerido_id"] = r.get("objeto_requerido_id")
    return datos


def _select_reto(f):
    extra = ", objeto_requerido_id" if f["objeto_requerido"] else ""
    return f"SELECT id, sala_id, titulo, descripcion, tipo, orden, activo, respuesta_hash{extra} FROM retos"


def _obtener_reto(reto_id, f):
    r = una(_select_reto(f) + " WHERE id = :id", id=reto_id)
    if r is None:
        raise no_encontrado("El reto no existe")
    return r


def _sin_partidas_en_curso(sala_id):
    if una("SELECT 1 AS x FROM partidas WHERE sala_id = :s AND estado = 'EN_CURSO' LIMIT 1", s=sala_id):
        raise conflicto("Hay partidas en curso en esta sala; no se pueden cambiar sus retos ahora")


def _opciones_validas(d):
    ops = d.get("opciones")
    if not isinstance(ops, list) or len(ops) < 2 or not all(isinstance(o, str) and o.strip() for o in ops):
        raise validacion("Un reto OPCION necesita 'opciones': una lista de al menos 2 textos")
    ops = [o.strip() for o in ops]
    if len({normalizar(o) for o in ops}) != len(ops):
        raise validacion("Las opciones no pueden repetirse")
    if any(len(o) > 200 for o in ops):
        raise validacion("Cada opción puede tener como máximo 200 caracteres")
    return ops


def _objeto_de_sala(objeto_id, sala_id):
    if una("SELECT 1 AS x FROM objetos WHERE id = :o AND sala_id = :s", o=objeto_id, s=sala_id) is None:
        raise regla("El objeto indicado no existe en esta sala")


def _datos_reto(d, sala_id, previo=None):
    """Valida el cuerpo y devuelve (columnas, opciones). 'previo' = reto actual al editar."""
    f = funciones()
    tipo = v.opcion(d, "tipo", TIPOS)
    datos = {
        "titulo": v.texto(d, "titulo", maximo=150),
        "descripcion": v.texto(d, "descripcion", maximo=5000),
        "tipo": tipo,
        "orden": v.entero(d, "orden", minimo=1, obligatorio=previo is not None),
        "activo": v.booleano(d, "activo", obligatorio=previo is not None),
    }
    respuesta = v.texto(d, "respuesta", maximo=200, obligatorio=False)
    opciones = None

    if tipo == "OBJETO":
        exigir("objeto_requerido", "El tipo OBJETO")
        if respuesta is not None:
            raise validacion("Los retos OBJETO no tienen respuesta de texto; se resuelven con 'objeto_requerido_id'")
        objeto_id = v.entero(d, "objeto_requerido_id", minimo=1)
        _objeto_de_sala(objeto_id, sala_id)
        datos["respuesta_hash"] = None
        datos["objeto_requerido_id"] = objeto_id
        return datos, None

    if tipo == "OPCION":
        exigir("opciones", "El tipo OPCION")
        if "opciones" in d or previo is None or previo["tipo"] != "OPCION":
            opciones = _opciones_validas(d)
            if respuesta is None:
                raise validacion("Indica 'respuesta' (una de las opciones)")
        elif respuesta is not None:
            # Se cambia solo la respuesta: tiene que ser una de las opciones guardadas
            guardadas = [o["texto"] for o in todas("SELECT texto FROM opciones_reto WHERE reto_id = :r",
                                                   r=previo["id"])]
            if normalizar(respuesta) not in {normalizar(o) for o in guardadas}:
                raise regla("La respuesta tiene que ser una de las opciones")
    if opciones is not None and normalizar(respuesta) not in {normalizar(o) for o in opciones}:
        raise regla("La respuesta tiene que ser una de las opciones")

    if respuesta is not None:
        datos["respuesta_hash"] = hash_respuesta(respuesta)
    elif previo is not None and previo["respuesta_hash"] and previo["tipo"] != "OBJETO":
        if tipo == "OPCION" and previo["tipo"] != "OPCION":
            raise validacion("Indica 'respuesta' al cambiar el tipo")
        datos["respuesta_hash"] = previo["respuesta_hash"]  # se conserva la solución actual
    else:
        raise validacion("El campo 'respuesta' es obligatorio para este tipo de reto")
    if f["objeto_requerido"]:
        datos["objeto_requerido_id"] = None
    return datos, opciones


def _guardar_opciones(reto_id, opciones):
    ejecutar("DELETE FROM opciones_reto WHERE reto_id = :r", r=reto_id)
    for i, texto in enumerate(opciones, start=1):
        ejecutar("INSERT INTO opciones_reto (reto_id, orden, texto) VALUES (:r, :o, :t)", r=reto_id, o=i, t=texto)


@bp.get("/salas/<int:sala_id>/retos")
@admin_requerido
def listar_retos(sala_id):
    obtener_sala(sala_id)
    f = funciones()
    retos = todas(_select_reto(f) + " WHERE sala_id = :s ORDER BY orden", s=sala_id)
    salida = []
    for r in retos:
        x = _reto_publico(r, f)
        x["pistas"] = todas("""SELECT id, orden, contenido, penalizacion_segundos FROM pistas
                               WHERE reto_id = :r ORDER BY orden""", r=r["id"])
        x["prerequisitos"] = [p["prerequisito_id"] for p in todas(
            "SELECT prerequisito_id FROM dependencias_reto WHERE reto_id = :r ORDER BY prerequisito_id", r=r["id"])]
        if f["opciones"] and r["tipo"] == "OPCION":
            x["opciones"] = [o["texto"] for o in todas(
                "SELECT texto FROM opciones_reto WHERE reto_id = :r ORDER BY orden", r=r["id"])]
        salida.append(x)
    return jsonify(salida)


@bp.post("/salas/<int:sala_id>/retos")
@admin_requerido
def crear_reto(sala_id):
    obtener_sala(sala_id)
    d = v.cuerpo()
    datos, opciones = _datos_reto(d, sala_id)
    _sin_partidas_en_curso(sala_id)
    if datos["orden"] is None:
        datos["orden"] = valor("SELECT COALESCE(MAX(orden), 0) + 1 FROM retos WHERE sala_id = :s", s=sala_id)
    elif una("SELECT 1 AS x FROM retos WHERE sala_id = :s AND orden = :o", s=sala_id, o=datos["orden"]):
        raise conflicto("Ya hay un reto con ese orden en la sala")
    if datos["activo"] is None:
        datos["activo"] = True

    columnas = ", ".join(datos)
    valores = ", ".join(f":{c}" for c in datos)
    nuevo = una(f"INSERT INTO retos (sala_id, {columnas}) VALUES (:sala_id, {valores}) RETURNING id",
                sala_id=sala_id, **datos)
    if opciones:
        _guardar_opciones(nuevo["id"], opciones)
    commit()
    f = funciones()
    return creado(_reto_publico(_obtener_reto(nuevo["id"], f), f), f"/api/retos/{nuevo['id']}")


@bp.put("/retos/<int:reto_id>")
@admin_requerido
def modificar_reto(reto_id):
    f = funciones()
    previo = _obtener_reto(reto_id, f)
    d = v.cuerpo()
    datos, opciones = _datos_reto(d, previo["sala_id"], previo=previo)
    _sin_partidas_en_curso(previo["sala_id"])
    if una("SELECT 1 AS x FROM retos WHERE sala_id = :s AND orden = :o AND id <> :id",
           s=previo["sala_id"], o=datos["orden"], id=reto_id):
        raise conflicto("Ya hay un reto con ese orden en la sala")

    asignaciones = ", ".join(f"{c} = :{c}" for c in datos)
    ejecutar(f"UPDATE retos SET {asignaciones} WHERE id = :id", id=reto_id, **datos)
    if f["opciones"]:
        if datos["tipo"] != "OPCION":
            ejecutar("DELETE FROM opciones_reto WHERE reto_id = :r", r=reto_id)
        elif opciones:
            _guardar_opciones(reto_id, opciones)
    commit()
    return jsonify(_reto_publico(_obtener_reto(reto_id, f), f))


@bp.delete("/retos/<int:reto_id>")
@admin_requerido
def eliminar_reto(reto_id):
    f = funciones()
    reto = _obtener_reto(reto_id, f)
    _sin_partidas_en_curso(reto["sala_id"])
    if una("SELECT 1 AS x FROM progreso_retos WHERE reto_id = :r LIMIT 1", r=reto_id):
        raise conflicto("El reto ya se ha usado en partidas; desactívalo con activo = false")
    if f["desbloqueo_objetos"] and una("SELECT 1 AS x FROM objetos WHERE reto_desbloqueo_id = :r", r=reto_id):
        raise conflicto("Hay objetos que se desbloquean con este reto")
    ejecutar("DELETE FROM retos WHERE id = :id", id=reto_id)
    commit()
    return sin_contenido()


@bp.post("/retos/<int:reto_id>/pistas")
@admin_requerido
def crear_pista(reto_id):
    _obtener_reto(reto_id, funciones())
    d = v.cuerpo()
    contenido = v.texto(d, "contenido", maximo=2000)
    penalizacion = v.entero(d, "penalizacion_segundos", minimo=0, maximo=3600, obligatorio=False) or 0
    orden = v.entero(d, "orden", minimo=1, obligatorio=False)
    if orden is None:
        orden = valor("SELECT COALESCE(MAX(orden), 0) + 1 FROM pistas WHERE reto_id = :r", r=reto_id)
    elif una("SELECT 1 AS x FROM pistas WHERE reto_id = :r AND orden = :o", r=reto_id, o=orden):
        raise conflicto("Ya hay una pista con ese orden en el reto")
    p = una("""INSERT INTO pistas (reto_id, orden, contenido, penalizacion_segundos)
               VALUES (:r, :o, :c, :p)
               RETURNING id, reto_id, orden, contenido, penalizacion_segundos""",
            r=reto_id, o=orden, c=contenido, p=penalizacion)
    commit()
    return creado(p, f"/api/pistas/{p['id']}")


def _objeto_json(o, f):
    x = {"id": o["id"], "sala_id": o["sala_id"], "nombre": o["nombre"],
         "descripcion": o["descripcion"], "activo": o["activo"]}
    if f["desbloqueo_objetos"]:
        x["reto_desbloqueo_id"] = o.get("reto_desbloqueo_id")
    return x


@bp.get("/salas/<int:sala_id>/objetos")
@admin_requerido
def listar_objetos(sala_id):
    obtener_sala(sala_id)
    f = funciones()
    extra = ", reto_desbloqueo_id" if f["desbloqueo_objetos"] else ""
    objetos = todas(f"SELECT id, sala_id, nombre, descripcion, activo{extra} FROM objetos WHERE sala_id = :s ORDER BY id",
                    s=sala_id)
    return jsonify([_objeto_json(o, f) for o in objetos])


@bp.post("/salas/<int:sala_id>/objetos")
@admin_requerido
def crear_objeto(sala_id):
    obtener_sala(sala_id)
    f = funciones()
    d = v.cuerpo()
    datos = {
        "nombre": v.texto(d, "nombre", maximo=120),
        "descripcion": v.texto(d, "descripcion", maximo=2000, minimo=0, obligatorio=False) or "",
        "activo": v.booleano(d, "activo", obligatorio=False),
    }
    if datos["activo"] is None:
        datos["activo"] = True
    if d.get("reto_desbloqueo_id") is not None:
        exigir("desbloqueo_objetos", "El desbloqueo de objetos por reto")
        reto = v.entero(d, "reto_desbloqueo_id", minimo=1)
        if una("SELECT 1 AS x FROM retos WHERE id = :r AND sala_id = :s", r=reto, s=sala_id) is None:
            raise regla("El reto de desbloqueo no existe en esta sala")
        datos["reto_desbloqueo_id"] = reto
    if una("SELECT 1 AS x FROM objetos WHERE sala_id = :s AND lower(nombre) = lower(:n)", s=sala_id, n=datos["nombre"]):
        raise conflicto("Ya existe un objeto con ese nombre en la sala")
    columnas = ", ".join(datos)
    valores = ", ".join(f":{c}" for c in datos)
    extra = ", reto_desbloqueo_id" if f["desbloqueo_objetos"] else ""
    o = una(f"""INSERT INTO objetos (sala_id, {columnas}) VALUES (:sala_id, {valores})
                RETURNING id, sala_id, nombre, descripcion, activo{extra}""", sala_id=sala_id, **datos)
    commit()
    return creado(_objeto_json(o, f), f"/api/objetos/{o['id']}")


@bp.post("/retos/<int:reto_id>/dependencias")
@admin_requerido
def crear_dependencia(reto_id):
    reto = _obtener_reto(reto_id, funciones())
    d = v.cuerpo()
    prerequisito = v.entero(d, "prerequisito_id", minimo=1)
    if prerequisito == reto_id:
        raise regla("Un reto no puede depender de sí mismo")
    if una("SELECT 1 AS x FROM retos WHERE id = :p AND sala_id = :s", p=prerequisito, s=reto["sala_id"]) is None:
        raise regla("El prerrequisito tiene que ser un reto de la misma sala")
    if una("SELECT 1 AS x FROM dependencias_reto WHERE reto_id = :r AND prerequisito_id = :p", r=reto_id, p=prerequisito):
        raise conflicto("Esa dependencia ya existe")
    # ¿El prerrequisito depende ya (directa o indirectamente) de este reto? -> ciclo
    ciclo = una(
        """WITH RECURSIVE requisitos(id) AS (
               SELECT prerequisito_id FROM dependencias_reto WHERE reto_id = :p
               UNION
               SELECT d.prerequisito_id FROM dependencias_reto d JOIN requisitos q ON d.reto_id = q.id
           )
           SELECT 1 AS x FROM requisitos WHERE id = :r""",
        p=prerequisito, r=reto_id,
    )
    if ciclo:
        raise regla("Esa dependencia crearía un ciclo entre retos")
    _sin_partidas_en_curso(reto["sala_id"])
    ejecutar("INSERT INTO dependencias_reto (sala_id, reto_id, prerequisito_id) VALUES (:s, :r, :p)",
             s=reto["sala_id"], r=reto_id, p=prerequisito)
    commit()
    return creado({"reto_id": reto_id, "prerequisito_id": prerequisito, "sala_id": reto["sala_id"]},
                  f"/api/retos/{reto_id}/dependencias")
