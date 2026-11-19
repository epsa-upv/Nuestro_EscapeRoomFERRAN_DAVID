"""Utilidades compartidas por las rutas."""
from flask import jsonify


def creado(objeto, ubicacion):
    """Respuesta 201 con cabecera Location (lo pide el contrato)."""
    return jsonify(objeto), 201, {"Location": ubicacion}


def sin_contenido():
    return "", 204


# Momento de inicio de una sesión como fecha-hora con zona (hora local de Madrid)
INICIO_SESION_SQL = "((se.fecha + se.hora_inicio) AT TIME ZONE 'Europe/Madrid')"
