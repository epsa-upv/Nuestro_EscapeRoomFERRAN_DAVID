"""Partidas, respuestas y progreso - jugador (contrato, sección 8).

GET  /api/partidas                                           JUGADOR (las suyas) / ADMIN (todas)
POST /api/partidas                       {reserva_id}        JUGADOR -> 201 partida PENDIENTE
GET  /api/partidas/{id}                                      Titular / ADMIN: detalle y progreso
POST /api/partidas/{id}/iniciar          {}                  Titular / ADMIN -> EN_CURSO
POST /api/partidas/{id}/retos/{reto_id}/intentos            Titular {respuesta}
POST /api/partidas/{id}/retos/{reto_id}/pistas/{pista_id}/usar  Titular
POST /api/partidas/{id}/retos/{reto_id}/usar-objeto         Titular {objeto_id}
POST /api/partidas/{id}/objetos/{objeto_id}/recoger         Titular
POST /api/partidas/{id}/abandonar                           Titular / ADMIN (ruta adicional)

Reglas del juego (decisiones del Sprint 3):
- Iniciar: solo desde 15 min antes de la sesión hasta su hora de fin prevista.
- Al iniciar se crea progreso_retos para cada reto activo:
  DISPONIBLE si no tiene prerrequisitos activos, BLOQUEADO si los tiene.
- Un acierto marca el reto COMPLETADO y desbloquea los retos cuyos prerrequisitos estén completados.
- Victoria: todos los retos de la partida COMPLETADO -> SUPERADA.
- Límite: inicio + duración de la sala. Si se supera -> AGOTADA (se aplica en la siguiente acción;
  un GET nunca modifica datos, solo informa de los segundos restantes).
- Las pistas suman su penalización al tiempo final del resultado.
- Al terminar se guarda el resultado en la tabla resultados (una fila por sesión).
"""
from flask import Blueprint, current_app, g, jsonify

from .. import validacion as v
from ..auth import es_admin, jugador_requerido, login_requerido
from ..db import commit, ejecutar, todas, una, valor
from ..errores import conflicto, no_encontrado, prohibido, regla
from ..juego import exigir, funciones, respuesta_correcta
from .comun import INICIO_SESION_SQL, creado

bp = Blueprint("partidas", __name__)

SELECT = f"""
    SELECT p.id, p.reserva_id, p.sesion_id, p.sala_id, p.estado, p.inicio, p.fin,
           r.usuario_id, r.estado AS reserva_estado, u.nombre AS titular,
           sa.nombre AS sala_nombre, sa.duracion_minutos,
           CAST(EXTRACT(EPOCH FROM (now() - p.inicio)) AS int) AS segundos_jugados,
           {INICIO_SESION_SQL} AS sesion_inicio
    FROM partidas p
    JOIN reservas r  ON r.id  = p.reserva_id
    JOIN usuarios u  ON u.id  = r.usuario_id
    JOIN sesiones se ON se.id = p.sesion_id
    JOIN salas sa    ON sa.id = p.sala_id
"""


# ---------------------------------------------------------------------------
# Carga y permisos
# ---------------------------------------------------------------------------

def _cargar(partida_id, bloquear=False, solo_titular=False):
    p = una(SELECT + " WHERE p.id = :id" + (" FOR UPDATE OF p" if bloquear else ""), id=partida_id)
    if p is None:
        raise no_encontrado("La partida no existe")
    es_titular = p["usuario_id"] == g.usuario["id"]
    if solo_titular and not es_titular:
        raise prohibido("Solo el titular de la reserva puede jugar esta partida")
    if not es_titular and not es_admin():
        raise prohibido("Esta partida no es tuya")
    return p


def _en_curso(partida_id):
    """Partida bloqueada para jugar. Si se ha acabado el tiempo, la cierra como AGOTADA."""
    p = _cargar(partida_id, bloquear=True, solo_titular=True)
    if p["estado"] != "EN_CURSO":
        raise conflicto(f"La partida no está en curso (estado: {p['estado']})")
    if p["segundos_jugados"] > p["duracion_minutos"] * 60:
        _finalizar(p, "AGOTADA")
        commit()
        raise conflicto("Se ha agotado el tiempo: la partida ha terminado")
    return p


def _progreso_reto(p, reto_id):
    pr = una("""SELECT pr.estado, r.tipo, r.respuesta_hash
                FROM progreso_retos pr JOIN retos r ON r.id = pr.reto_id
                WHERE pr.partida_id = :p AND pr.reto_id = :r FOR UPDATE OF pr""", p=p["id"], r=reto_id)
    if pr is None:
        raise no_encontrado("Ese reto no forma parte de esta partida")
    if pr["estado"] == "BLOQUEADO":
        raise conflicto("El reto está bloqueado: antes hay que completar sus prerrequisitos")
    if pr["estado"] == "COMPLETADO":
        raise conflicto("El reto ya está completado")
    return pr


# ---------------------------------------------------------------------------
# Lógica del juego
# ---------------------------------------------------------------------------

def _desbloquear(partida_id):
    """Pasa a DISPONIBLE los retos cuyos prerrequisitos (activos) están todos COMPLETADO."""
    ejecutar(
        """UPDATE progreso_retos pr SET estado = 'DISPONIBLE'
           WHERE pr.partida_id = :p AND pr.estado = 'BLOQUEADO'
             AND NOT EXISTS (
                 SELECT 1 FROM dependencias_reto d
                 JOIN retos rp ON rp.id = d.prerequisito_id AND rp.activo
                 LEFT JOIN progreso_retos pp ON pp.partida_id = :p AND pp.reto_id = d.prerequisito_id
                 WHERE d.reto_id = pr.reto_id AND COALESCE(pp.estado, '') <> 'COMPLETADO')""",
        p=partida_id,
    )


def _completar(p, reto_id):
    ejecutar("""UPDATE progreso_retos SET estado = 'COMPLETADO', fecha_completado = now()
                WHERE partida_id = :p AND reto_id = :r""", p=p["id"], r=reto_id)
    _desbloquear(p["id"])
    if not una("SELECT 1 AS x FROM progreso_retos WHERE partida_id = :p AND estado <> 'COMPLETADO' LIMIT 1",
               p=p["id"]):
        _finalizar(p, "SUPERADA")


def _finalizar(p, estado):
    """Cierra la partida y guarda/actualiza su resultado (una fila por sesión)."""
    ejecutar("UPDATE partidas SET estado = :e, fin = now() WHERE id = :id", e=estado, id=p["id"])
    superada = estado == "SUPERADA"
    ejecutar(
        """INSERT INTO resultados (sesion_id, nombre_equipo, tiempo_minutos, superada)
           SELECT p.sesion_id, :equipo,
                  CASE WHEN :superada THEN CAST(CEIL((EXTRACT(EPOCH FROM (p.fin - p.inicio))
                       + COALESCE((SELECT SUM(pi.penalizacion_segundos)
                                   FROM pistas_utilizadas pu JOIN pistas pi ON pi.id = pu.pista_id
                                   WHERE pu.partida_id = p.id), 0)) / 60.0) AS int) END,
                  :superada
           FROM partidas p WHERE p.id = :id
           ON CONFLICT (sesion_id) DO UPDATE
           SET nombre_equipo = EXCLUDED.nombre_equipo,
               tiempo_minutos = EXCLUDED.tiempo_minutos,
               superada = EXCLUDED.superada""",
        equipo=p["titular"], superada=superada, id=p["id"],
    )


def _estados(partida_id, reto_id):
    return {
        "reto_estado": valor("SELECT estado FROM progreso_retos WHERE partida_id = :p AND reto_id = :r",
                             p=partida_id, r=reto_id),
        "partida_estado": valor("SELECT estado FROM partidas WHERE id = :p", p=partida_id),
    }


# ---------------------------------------------------------------------------
# Representación JSON
# ---------------------------------------------------------------------------

def _resumen(p):
    return {
        "id": p["id"], "reserva_id": p["reserva_id"], "sesion_id": p["sesion_id"], "sala_id": p["sala_id"],
        "sala": {"id": p["sala_id"], "nombre": p["sala_nombre"]},
        "estado": p["estado"], "inicio": p["inicio"], "fin": p["fin"],
    }


def _detalle(partida_id):
    p = una(SELECT + " WHERE p.id = :id", id=partida_id)
    f = funciones()
    datos = _resumen(p)

    progreso = todas("""SELECT pr.reto_id, pr.estado, r.orden, r.titulo, r.descripcion, r.tipo
                        FROM progreso_retos pr JOIN retos r ON r.id = pr.reto_id
                        WHERE pr.partida_id = :p ORDER BY r.orden""", p=partida_id)
    pistas = todas("""SELECT pi.id, pi.reto_id, pi.orden, pi.contenido, pi.penalizacion_segundos,
                             (pu.pista_id IS NOT NULL) AS usada
                      FROM pistas pi
                      JOIN progreso_retos pr ON pr.reto_id = pi.reto_id AND pr.partida_id = :p
                      LEFT JOIN pistas_utilizadas pu ON pu.pista_id = pi.id AND pu.partida_id = :p
                      ORDER BY pi.reto_id, pi.orden""", p=partida_id)
    opciones = {}
    if f["opciones"]:
        for o in todas("""SELECT o.reto_id, o.texto FROM opciones_reto o
                          JOIN progreso_retos pr ON pr.reto_id = o.reto_id AND pr.partida_id = :p
                          ORDER BY o.reto_id, o.orden""", p=partida_id):
            opciones.setdefault(o["reto_id"], []).append(o["texto"])

    retos = []
    for r in progreso:
        if r["estado"] == "BLOQUEADO":
            # No se revela el contenido de los retos futuros
            retos.append({"id": r["reto_id"], "orden": r["orden"], "titulo": "Reto bloqueado",
                          "descripcion": None, "tipo": r["tipo"], "estado": "BLOQUEADO", "pistas": []})
            continue
        x = {"id": r["reto_id"], "orden": r["orden"], "titulo": r["titulo"], "descripcion": r["descripcion"],
             "tipo": r["tipo"], "estado": r["estado"], "pistas": []}
        for pi in (q for q in pistas if q["reto_id"] == r["reto_id"]):
            pista = {"id": pi["id"], "orden": pi["orden"], "penalizacion_segundos": pi["penalizacion_segundos"],
                     "usada": pi["usada"]}
            if pi["usada"]:
                pista["contenido"] = pi["contenido"]  # solo después de usarla
            x["pistas"].append(pista)
        if r["tipo"] == "OPCION" and r["reto_id"] in opciones:
            x["opciones"] = opciones[r["reto_id"]]
        retos.append(x)

    datos["retos"] = retos
    datos["inventario"] = todas("""SELECT o.id, o.nombre, ip.consumido
                                   FROM inventario_partida ip JOIN objetos o ON o.id = ip.objeto_id
                                   WHERE ip.partida_id = :p ORDER BY ip.fecha_obtencion""", p=partida_id)
    datos["objetos_disponibles"] = _objetos_disponibles(p, f) if p["estado"] == "EN_CURSO" else []

    penalizacion = valor("""SELECT COALESCE(SUM(pi.penalizacion_segundos), 0)
                            FROM pistas_utilizadas pu JOIN pistas pi ON pi.id = pu.pista_id
                            WHERE pu.partida_id = :p""", p=partida_id)
    datos["retos_totales"] = len(progreso)
    datos["retos_completados"] = sum(1 for r in progreso if r["estado"] == "COMPLETADO")
    datos["penalizacion_segundos"] = int(penalizacion)
    datos["segundos_restantes"] = (max(0, p["duracion_minutos"] * 60 - p["segundos_jugados"])
                                   if p["estado"] == "EN_CURSO" else None)
    return datos


def _objetos_disponibles(p, f):
    condicion = ""
    if f["desbloqueo_objetos"]:
        condicion = """AND (o.reto_desbloqueo_id IS NULL OR EXISTS (
                           SELECT 1 FROM progreso_retos pr WHERE pr.partida_id = :p
                           AND pr.reto_id = o.reto_desbloqueo_id AND pr.estado = 'COMPLETADO'))"""
    return todas(f"""SELECT o.id, o.nombre, o.descripcion FROM objetos o
                     WHERE o.sala_id = :s AND o.activo
                       AND NOT EXISTS (SELECT 1 FROM inventario_partida ip
                                       WHERE ip.partida_id = :p AND ip.objeto_id = o.id)
                       {condicion}
                     ORDER BY o.id""", s=p["sala_id"], p=p["id"])


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@bp.get("/partidas")
@login_requerido
def listar():
    if es_admin():
        filas = todas(SELECT + " ORDER BY p.id")
    else:
        filas = todas(SELECT + " WHERE r.usuario_id = :yo ORDER BY p.id", yo=g.usuario["id"])
    return jsonify([_resumen(p) for p in filas])


@bp.post("/partidas")
@jugador_requerido
def crear():
    d = v.cuerpo()
    reserva_id = v.entero(d, "reserva_id", minimo=1)
    r = una(f"""SELECT r.id, r.usuario_id, r.estado, r.sesion_id, se.sala_id,
                       {INICIO_SESION_SQL} + make_interval(mins => sa.duracion_minutos) < now() AS terminada
                FROM reservas r JOIN sesiones se ON se.id = r.sesion_id JOIN salas sa ON sa.id = se.sala_id
                WHERE r.id = :id FOR UPDATE OF r""", id=reserva_id)
    if r is None:
        raise no_encontrado("La reserva no existe")
    if r["usuario_id"] != g.usuario["id"]:
        raise prohibido("Esta reserva no es tuya")
    if r["estado"] != "ACTIVA":
        raise conflicto("La reserva está cancelada")
    if una("SELECT 1 AS x FROM partidas WHERE reserva_id = :id", id=reserva_id):
        raise conflicto("Ya existe una partida para esta reserva")
    if r["terminada"]:
        raise regla("La sesión de esta reserva ya ha terminado")
    # sesion_id y sala_id se derivan de la reserva: nunca se aceptan del navegador
    nueva = una("""INSERT INTO partidas (reserva_id, sesion_id, sala_id)
                   VALUES (:r, :s, :sala) RETURNING id""", r=reserva_id, s=r["sesion_id"], sala=r["sala_id"])
    commit()
    return creado(_detalle(nueva["id"]), f"/api/partidas/{nueva['id']}")


@bp.get("/partidas/<int:partida_id>")
@login_requerido
def ver(partida_id):
    _cargar(partida_id)
    return jsonify(_detalle(partida_id))


@bp.post("/partidas/<int:partida_id>/iniciar")
@login_requerido
def iniciar(partida_id):
    p = _cargar(partida_id, bloquear=True)
    if p["estado"] != "PENDIENTE":
        raise conflicto(f"La partida ya se ha iniciado (estado: {p['estado']})")
    if p["reserva_estado"] != "ACTIVA":
        raise conflicto("La reserva está cancelada")
    ventana = una(
        """SELECT now() >= CAST(:ini AS timestamptz) - make_interval(mins => :antes) AS abierta,
                  now() <= CAST(:ini AS timestamptz) + make_interval(mins => :dur) AS a_tiempo""",
        ini=p["sesion_inicio"], antes=current_app.config["MINUTOS_ANTES_INICIO"], dur=p["duracion_minutos"],
    )
    if not ventana["abierta"]:
        raise regla(f"Todavía no se puede empezar: se abre {current_app.config['MINUTOS_ANTES_INICIO']} "
                    "minutos antes de la hora de la sesión")
    if not ventana["a_tiempo"]:
        raise regla("La sesión ya ha terminado")
    if not una("SELECT 1 AS x FROM retos WHERE sala_id = :s AND activo LIMIT 1", s=p["sala_id"]):
        raise regla("La sala todavía no tiene retos activos")

    ejecutar("UPDATE partidas SET estado = 'EN_CURSO', inicio = now() WHERE id = :id", id=partida_id)
    ejecutar(
        """INSERT INTO progreso_retos (partida_id, sala_id, reto_id, estado)
           SELECT :p, r.sala_id, r.id,
                  CASE WHEN EXISTS (SELECT 1 FROM dependencias_reto d
                                    JOIN retos rp ON rp.id = d.prerequisito_id AND rp.activo
                                    WHERE d.reto_id = r.id)
                       THEN 'BLOQUEADO' ELSE 'DISPONIBLE' END
           FROM retos r WHERE r.sala_id = :s AND r.activo""",
        p=partida_id, s=p["sala_id"],
    )
    commit()
    return jsonify(_detalle(partida_id))


@bp.post("/partidas/<int:partida_id>/retos/<int:reto_id>/intentos")
@login_requerido
def responder(partida_id, reto_id):
    d = v.cuerpo()
    respuesta = v.texto(d, "respuesta", maximo=200)
    p = _en_curso(partida_id)
    pr = _progreso_reto(p, reto_id)
    if pr["tipo"] == "OBJETO":
        raise regla("Este reto se resuelve usando un objeto, no con una respuesta")
    correcta = respuesta_correcta(respuesta, pr["respuesta_hash"])
    ejecutar("""INSERT INTO intentos_reto (partida_id, sala_id, reto_id, correcta)
                VALUES (:p, :s, :r, :c)""", p=partida_id, s=p["sala_id"], r=reto_id, c=correcta)
    if correcta:
        _completar(p, reto_id)
    commit()
    return jsonify(correcta=correcta, **_estados(partida_id, reto_id))


@bp.post("/partidas/<int:partida_id>/retos/<int:reto_id>/pistas/<int:pista_id>/usar")
@login_requerido
def usar_pista(partida_id, reto_id, pista_id):
    p = _en_curso(partida_id)
    pista = una("SELECT id, contenido, penalizacion_segundos FROM pistas WHERE id = :id AND reto_id = :r",
                id=pista_id, r=reto_id)
    if pista is None:
        raise no_encontrado("Esa pista no existe en este reto")
    _progreso_reto(p, reto_id)
    if una("SELECT 1 AS x FROM pistas_utilizadas WHERE partida_id = :p AND pista_id = :id", p=partida_id, id=pista_id):
        raise conflicto("Esta pista ya se ha usado")
    ejecutar("""INSERT INTO pistas_utilizadas (partida_id, sala_id, reto_id, pista_id)
                VALUES (:p, :s, :r, :pi)""", p=partida_id, s=p["sala_id"], r=reto_id, pi=pista_id)
    commit()
    return jsonify(pista)


@bp.post("/partidas/<int:partida_id>/retos/<int:reto_id>/usar-objeto")
@login_requerido
def usar_objeto(partida_id, reto_id):
    exigir("objeto_requerido", "El uso de objetos en retos")
    d = v.cuerpo()
    objeto_id = v.entero(d, "objeto_id", minimo=1)
    p = _en_curso(partida_id)
    pr = _progreso_reto(p, reto_id)
    if pr["tipo"] != "OBJETO":
        raise regla("Este reto no se resuelve con un objeto")
    inv = una("""SELECT consumido FROM inventario_partida WHERE partida_id = :p AND objeto_id = :o
                 FOR UPDATE""", p=partida_id, o=objeto_id)
    if inv is None:
        raise regla("No tienes ese objeto en el inventario")
    if inv["consumido"]:
        raise regla("Ese objeto ya se ha usado")
    requerido = valor("SELECT objeto_requerido_id FROM retos WHERE id = :r", r=reto_id)
    correcta = objeto_id == requerido
    ejecutar("""INSERT INTO intentos_reto (partida_id, sala_id, reto_id, correcta)
                VALUES (:p, :s, :r, :c)""", p=partida_id, s=p["sala_id"], r=reto_id, c=correcta)
    if correcta:
        ejecutar("UPDATE inventario_partida SET consumido = TRUE WHERE partida_id = :p AND objeto_id = :o",
                 p=partida_id, o=objeto_id)
        _completar(p, reto_id)
    commit()
    return jsonify(correcta=correcta, **_estados(partida_id, reto_id))


@bp.post("/partidas/<int:partida_id>/objetos/<int:objeto_id>/recoger")
@login_requerido
def recoger(partida_id, objeto_id):
    p = _en_curso(partida_id)
    f = funciones()
    extra = ", reto_desbloqueo_id" if f["desbloqueo_objetos"] else ""
    o = una(f"SELECT id, activo{extra} FROM objetos WHERE id = :o AND sala_id = :s",
            o=objeto_id, s=p["sala_id"])
    if o is None or not o["activo"]:
        raise no_encontrado("Ese objeto no existe en esta sala")
    if una("SELECT 1 AS x FROM inventario_partida WHERE partida_id = :p AND objeto_id = :o", p=partida_id, o=objeto_id):
        raise conflicto("Ya tienes ese objeto")
    if f["desbloqueo_objetos"] and o["reto_desbloqueo_id"] is not None:
        hecho = valor("SELECT estado FROM progreso_retos WHERE partida_id = :p AND reto_id = :r",
                      p=partida_id, r=o["reto_desbloqueo_id"])
        if hecho != "COMPLETADO":
            raise regla("Ese objeto todavía no está disponible")
    ejecutar("""INSERT INTO inventario_partida (partida_id, sala_id, objeto_id)
                VALUES (:p, :s, :o)""", p=partida_id, s=p["sala_id"], o=objeto_id)
    commit()
    return jsonify(objeto_id=objeto_id, consumido=False)


@bp.post("/partidas/<int:partida_id>/abandonar")
@login_requerido
def abandonar(partida_id):
    p = _cargar(partida_id, bloquear=True)
    if p["estado"] != "EN_CURSO":
        raise conflicto(f"Solo se puede abandonar una partida en curso (estado: {p['estado']})")
    _finalizar(p, "ABANDONADA")
    commit()
    return jsonify(_detalle(partida_id))
