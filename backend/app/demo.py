"""Datos de demostración para el desarrollo (NO se ejecutan en producción).

    flask --app run demo                 # contraseñas demo + retos de ejemplo
    flask --app run demo --sesion-ahora  # además, una sesión de la sala 1 dentro de 10 minutos

- La contraseña de los usuarios demo se lee de DEMO_PASSWORD (.env), así no se sube a GitHub.
  Solo se cambia a los usuarios que tienen los hashes ficticios del seed del Sprint 2.
- Las respuestas de los retos se guardan como HMAC con RESPUESTA_SECRET, igual que las reales.
- Los retos OPCION y OBJETO solo se crean si está aplicada migracion_sprint3.sql.
- Solo crea retos en salas que todavía no tienen ninguno (se puede ejecutar varias veces).
"""
import os

import click
from werkzeug.security import generate_password_hash

from .db import commit, ejecutar, una, valor
from .juego import funciones, hash_respuesta


def _reto(sala, orden, titulo, descripcion, tipo, respuesta=None, objeto=None, prerequisito=None):
    f = funciones()
    columnas = "sala_id, orden, titulo, descripcion, tipo, respuesta_hash"
    valores = ":s, :o, :t, :d, :tipo, :h"
    params = dict(s=sala, o=orden, t=titulo, d=descripcion, tipo=tipo,
                  h=hash_respuesta(respuesta) if respuesta else None)
    if f["objeto_requerido"]:
        columnas += ", objeto_requerido_id"
        valores += ", :obj"
        params["obj"] = objeto
    reto_id = valor(f"INSERT INTO retos ({columnas}) VALUES ({valores}) RETURNING id", **params)
    if prerequisito:
        ejecutar("INSERT INTO dependencias_reto (sala_id, reto_id, prerequisito_id) VALUES (:s, :r, :p)",
                 s=sala, r=reto_id, p=prerequisito)
    return reto_id


def _pista(reto, orden, contenido, segundos):
    ejecutar("""INSERT INTO pistas (reto_id, orden, contenido, penalizacion_segundos)
                VALUES (:r, :o, :c, :s)""", r=reto, o=orden, c=contenido, s=segundos)


def _sala_sin_retos(sala_id):
    return (una("SELECT 1 AS x FROM salas WHERE id = :s", s=sala_id) is not None
            and una("SELECT 1 AS x FROM retos WHERE sala_id = :s", s=sala_id) is None)


def cargar_demo(password=None, sesion_ahora=False):
    f = funciones()
    info = {"usuarios_actualizados": 0, "retos_creados": 0, "sesion_ahora": None}

    if password:
        info["usuarios_actualizados"] = ejecutar(
            "UPDATE usuarios SET password_hash = :h WHERE password_hash LIKE '$2b$10$%'",
            h=generate_password_hash(password),
        )

    # Sala 1 - El Laboratorio Perdido: cadena de retos con dependencias
    if _sala_sin_retos(1):
        r1 = _reto(1, 1, "Tubos de ensayo",
                   "Ordena los colores de los tubos según la etiqueta del armario (separados por guiones).",
                   "TEXTO", respuesta="azul-rojo-verde")
        _pista(r1, 1, "Fíjate en el orden de la tabla periódica del armario.", 30)
        _pista(r1, 2, "El primer color es el del cielo.", 60)
        r2 = _reto(1, 2, "El microscopio", "En la muestra hay cuatro números escondidos. ¿Cuál es el código?",
                   "CODIGO", respuesta="4721", prerequisito=r1)
        _pista(r2, 1, "Ajusta el enfoque al máximo.", 30)
        if f["opciones"]:
            r3 = _reto(1, 3, "La palabra de la puerta", "¿Qué palabra forman las letras de las probetas?",
                       "OPCION", respuesta="GENOMA", prerequisito=r2)
            for i, t in enumerate(["GENOMA", "PROTEINA", "CELULA"], start=1):
                ejecutar("INSERT INTO opciones_reto (reto_id, orden, texto) VALUES (:r, :o, :t)", r=r3, o=i, t=t)
        else:
            r3 = _reto(1, 3, "La palabra de la puerta", "¿Qué palabra forman las letras de las probetas?",
                       "TEXTO", respuesta="genoma", prerequisito=r2)
        _pista(r3, 1, "Cada probeta tiene una letra en la base.", 30)
        info["retos_creados"] += 3
        if f["objeto_requerido"] and f["desbloqueo_objetos"]:
            tarjeta = valor("""INSERT INTO objetos (sala_id, nombre, descripcion, reto_desbloqueo_id)
                               VALUES (1, 'Tarjeta de acceso', 'Aparece al resolver el microscopio', :r)
                               RETURNING id""", r=r2)
            _reto(1, 4, "Puerta de seguridad", "Usa el objeto adecuado para abrir la puerta.",
                  "OBJETO", objeto=tarjeta, prerequisito=r3)
            info["retos_creados"] += 1

    # Sala 2 - La Cripta del Conde: dos retos sencillos
    if _sala_sin_retos(2):
        c1 = _reto(2, 1, "El retrato del Conde", "El año del retrato abre el primer candado.",
                   "CODIGO", respuesta="1789")
        _pista(c1, 1, "Mira la esquina inferior del marco.", 30)
        _reto(2, 2, "El ataúd", "¿Qué aparece en la ventana al apagar las velas?", "TEXTO",
              respuesta="luna", prerequisito=c1)
        info["retos_creados"] += 2

    if sesion_ahora:
        # Empieza dentro de 10 minutos: se puede reservar ya y la partida se puede iniciar
        # porque la ventana se abre 15 minutos antes
        ahora = una("""SELECT CAST(t AS date) AS f, CAST(t AS time) AS h FROM (
                           SELECT date_trunc('minute', now() AT TIME ZONE 'Europe/Madrid') + interval '10 minutes' AS t
                       ) x""")
        existente = una("SELECT id FROM sesiones WHERE sala_id = 1 AND fecha = :f AND hora_inicio = :h",
                        f=ahora["f"], h=ahora["h"])
        info["sesion_ahora"] = existente["id"] if existente else valor(
            "INSERT INTO sesiones (sala_id, fecha, hora_inicio) VALUES (1, :f, :h) RETURNING id",
            f=ahora["f"], h=ahora["h"])
    commit()
    return info


def registrar_comando(app):
    @app.cli.command("demo")
    @click.option("--sesion-ahora", is_flag=True, help="Crea una sesión de la sala 1 que empieza en 10 minutos.")
    def demo(sesion_ahora):
        """Carga contraseñas demo y retos de ejemplo."""
        password = os.environ.get("DEMO_PASSWORD")
        if not password or len(password) < 8:
            raise click.ClickException("Pon DEMO_PASSWORD (8 caracteres o más) en el archivo .env")
        info = cargar_demo(password, sesion_ahora)
        click.echo(f"Usuarios demo actualizados: {info['usuarios_actualizados']}")
        click.echo(f"Retos creados: {info['retos_creados']}")
        if info["sesion_ahora"]:
            click.echo(f"Sesión de la sala 1 (empieza en 10 minutos): id {info['sesion_ahora']}")
