"""Conversión de filas de la base de datos a los objetos JSON del contrato."""


def sala(f):
    return {
        "id": f["id"], "nombre": f["nombre"], "tematica": f["tematica"],
        "dificultad": f["dificultad"], "duracion_minutos": f["duracion_minutos"],
        "capacidad": f["capacidad"], "activa": f["activa"],
    }


def sesion(f):
    return {
        "id": f["id"], "sala_id": f["sala_id"], "fecha": f["fecha"],
        "hora_inicio": f["hora_inicio"], "estado": f["estado"],
        "sala": {
            "id": f["sala_id"], "nombre": f["sala_nombre"],
            "capacidad": f["sala_capacidad"], "duracion_minutos": f["sala_duracion"],
        },
    }


def reserva(f):
    return {
        "id": f["id"], "usuario_id": f["usuario_id"], "sesion_id": f["sesion_id"],
        "numero_jugadores": f["numero_jugadores"], "estado": f["estado"],
        "fecha_reserva": f["fecha_reserva"],
        "sesion": {
            "id": f["sesion_id"], "sala_id": f["sala_id"], "fecha": f["fecha"],
            "hora_inicio": f["hora_inicio"], "sala": {"nombre": f["sala_nombre"]},
        },
    }


def resultado(f):
    return {
        "id": f["id"], "sesion_id": f["sesion_id"], "nombre_equipo": f["nombre_equipo"],
        "tiempo_minutos": f["tiempo_minutos"], "superada": f["superada"],
    }


def usuario(f):
    return {"id": f["id"], "nombre": f["nombre"], "email": f["email"], "rol": f["rol"]}
