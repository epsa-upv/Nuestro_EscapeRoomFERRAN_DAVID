"""Validación de los datos recibidos (cuerpo JSON y parámetros de la URL)."""
import datetime
import re

from flask import request

from .errores import validacion

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def cuerpo():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise validacion("El cuerpo de la petición debe ser un objeto JSON")
    return datos


def _falta(campo):
    return validacion(f"El campo '{campo}' es obligatorio")


def texto(d, campo, maximo=255, minimo=1, obligatorio=True):
    v = d.get(campo)
    if v is None:
        if obligatorio:
            raise _falta(campo)
        return None
    if not isinstance(v, str):
        raise validacion(f"El campo '{campo}' debe ser texto")
    v = v.strip()
    if not minimo <= len(v) <= maximo:
        raise validacion(f"El campo '{campo}' debe tener entre {minimo} y {maximo} caracteres")
    return v


def entero(d, campo, minimo=None, maximo=None, obligatorio=True):
    v = d.get(campo)
    if v is None:
        if obligatorio:
            raise _falta(campo)
        return None
    if isinstance(v, bool) or not isinstance(v, int):
        raise validacion(f"El campo '{campo}' debe ser un número entero")
    if minimo is not None and v < minimo:
        raise validacion(f"El campo '{campo}' debe ser como mínimo {minimo}")
    if maximo is not None and v > maximo:
        raise validacion(f"El campo '{campo}' debe ser como máximo {maximo}")
    return v


def booleano(d, campo, obligatorio=True):
    v = d.get(campo)
    if v is None:
        if obligatorio:
            raise _falta(campo)
        return None
    if not isinstance(v, bool):
        raise validacion(f"El campo '{campo}' debe ser true o false")
    return v


def opcion(d, campo, opciones, obligatorio=True):
    v = d.get(campo)
    if v is None:
        if obligatorio:
            raise _falta(campo)
        return None
    if not isinstance(v, str) or v.strip().upper() not in opciones:
        raise validacion(f"El campo '{campo}' debe ser uno de: {', '.join(opciones)}")
    return v.strip().upper()


def fecha(valor, campo="fecha"):
    if not isinstance(valor, str):
        raise validacion(f"El campo '{campo}' es obligatorio (AAAA-MM-DD)")
    try:
        return datetime.date.fromisoformat(valor)
    except ValueError:
        raise validacion(f"El campo '{campo}' debe tener formato AAAA-MM-DD")


def hora(valor, campo="hora_inicio"):
    if not isinstance(valor, str) or not re.fullmatch(r"\d{2}:\d{2}", valor):
        raise validacion(f"El campo '{campo}' debe tener formato HH:mm")
    try:
        return datetime.time.fromisoformat(valor)
    except ValueError:
        raise validacion(f"El campo '{campo}' no es una hora válida")


def email(d, campo="email"):
    v = texto(d, campo).lower()
    if not EMAIL_RE.match(v):
        raise validacion("El email no tiene un formato válido")
    return v


def param_bool(nombre):
    v = request.args.get(nombre)
    if v is None:
        return None
    if v.lower() in ("true", "1"):
        return True
    if v.lower() in ("false", "0"):
        return False
    raise validacion(f"El parámetro '{nombre}' debe ser true o false")


def param_entero(nombre):
    v = request.args.get(nombre)
    if v is None:
        return None
    try:
        return int(v)
    except ValueError:
        raise validacion(f"El parámetro '{nombre}' debe ser un número entero")


def param_opcion(nombre, opciones):
    v = request.args.get(nombre)
    if v is None:
        return None
    if v.upper() not in opciones:
        raise validacion(f"El parámetro '{nombre}' debe ser uno de: {', '.join(opciones)}")
    return v.upper()
