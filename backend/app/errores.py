"""Errores de la API con el formato del contrato:
    { "error": { "codigo": "VALIDACION", "mensaje": "Texto comprensible" } }
Nunca se envían trazas ni datos internos al cliente.
"""
import logging

from flask import jsonify, request
from sqlalchemy import exc as sa_exc
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, status, codigo, mensaje):
        super().__init__(mensaje)
        self.status, self.codigo, self.mensaje = status, codigo, mensaje


def validacion(msg):
    return ApiError(400, "VALIDACION", msg)


def no_autenticado(msg="Debes iniciar sesión"):
    return ApiError(401, "NO_AUTENTICADO", msg)


def prohibido(msg="No tienes permiso para esta acción"):
    return ApiError(403, "PROHIBIDO", msg)


def cuenta_bloqueada():
    return ApiError(403, "CUENTA_BLOQUEADA",
                    "Cuenta bloqueada por demasiados intentos fallidos; contacta con un administrador")


def no_encontrado(msg="Recurso no encontrado"):
    return ApiError(404, "NO_ENCONTRADO", msg)


def conflicto(msg):
    return ApiError(409, "CONFLICTO", msg)


def regla(msg):
    return ApiError(422, "REGLA_NEGOCIO", msg)


def respuesta_error(status, codigo, mensaje):
    return jsonify(error={"codigo": codigo, "mensaje": mensaje}), status


def registrar(app):
    @app.errorhandler(ApiError)
    def _api(e):
        return respuesta_error(e.status, e.codigo, e.mensaje)

    @app.errorhandler(sa_exc.IntegrityError)
    def _integridad(e):
        estado = getattr(e.orig, "sqlstate", "") or ""
        if estado == "23505":
            return respuesta_error(409, "CONFLICTO", "Ya existe un registro con esos datos")
        if estado == "23503":
            return respuesta_error(409, "CONFLICTO", "Operación no permitida: hay datos relacionados")
        return respuesta_error(400, "VALIDACION", "Algún dato no cumple las restricciones de la base de datos")

    @app.errorhandler(sa_exc.OperationalError)
    def _sin_bd(e):
        log.error("Error de conexión con la base de datos: %s", e)
        return respuesta_error(503, "SIN_BASE_DE_DATOS", "No se puede conectar con la base de datos")

    @app.errorhandler(HTTPException)
    def _http(e):
        if e.code == 404:
            return respuesta_error(404, "NO_ENCONTRADO", "Ruta no encontrada")
        if e.code == 405:
            return respuesta_error(405, "METODO_NO_PERMITIDO", "Método no permitido en esta ruta")
        return respuesta_error(e.code or 500, "ERROR_HTTP", e.description or "Error")

    @app.errorhandler(Exception)
    def _interno(e):
        log.exception("Error no controlado en %s %s", request.method, request.path)
        return respuesta_error(500, "ERROR_INTERNO", "Error interno del servidor")
