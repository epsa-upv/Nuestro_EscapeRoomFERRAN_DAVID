"""Backend de EscapeHub: Flask + SQLAlchemy + PostgreSQL.

- La API está en /api/... (contrato: doc/api_rest.md)
- Flask sirve también la web de src/ (index.html, js/, css/...), así la web
  y la API comparten origen y no hace falta CORS.
"""
import datetime
import decimal
from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory
from flask.json.provider import DefaultJSONProvider

from . import db, errores
from .config import Config, url_bd


class ProveedorJSON(DefaultJSONProvider):
    ensure_ascii = False
    sort_keys = False

    @staticmethod
    def default(o):
        if isinstance(o, datetime.datetime):
            return o.isoformat(timespec="seconds")
        if isinstance(o, datetime.date):
            return o.isoformat()
        if isinstance(o, datetime.time):
            return o.strftime("%H:%M")
        if isinstance(o, decimal.Decimal):
            return float(o)
        return DefaultJSONProvider.default(o)


# Solo se sirven estos tipos de archivo de src/ (nunca .sql, .py, .env...)
EXTENSIONES_WEB = {".html", ".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg",
                   ".ico", ".webp", ".woff", ".woff2", ".ttf", ".json", ".map"}
CARPETAS_PRIVADAS = {"backend", "db"}


def create_app(config=None):
    app = Flask(__name__, static_folder=None)
    app.json = ProveedorJSON(app)
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    app.config["DATABASE_URL"] = url_bd(app.config["DATABASE_URL"])
    for clave in ("SECRET_KEY", "RESPUESTA_SECRET"):
        if not app.config.get(clave):
            raise RuntimeError(f"Falta {clave} en el archivo .env (copia .env.example como .env)")

    db.init_app(app)
    errores.registrar(app)

    @app.after_request
    def cors(resp):
        # Solo para orígenes declarados explícitamente en CORS_ORIGINS
        from flask import request
        origen = request.headers.get("Origin")
        if origen and origen in app.config["CORS_ORIGINS"]:
            resp.headers["Access-Control-Allow-Origin"] = origen
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return resp

    from .rutas import auth, juego_admin, partidas, reservas, resultados, salas, sesiones

    for modulo in (auth, salas, sesiones, reservas, resultados, juego_admin, partidas):
        app.register_blueprint(modulo.bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        db.valor("SELECT 1")
        return jsonify(estado="ok", base_de_datos="ok")

    # ---------- Web (frontend de Ferran) ----------
    carpeta_web = Path(app.config["FRONTEND_DIR"]).resolve()

    @app.get("/")
    def inicio():
        return send_from_directory(carpeta_web, "index.html")

    @app.get("/<path:ruta>")
    def archivos_web(ruta):
        partes = Path(ruta).parts
        if ruta.startswith("api/") or not partes or partes[0] in CARPETAS_PRIVADAS \
                or Path(ruta).suffix.lower() not in EXTENSIONES_WEB \
                or any(p.startswith(".") for p in partes):
            abort(404)
        return send_from_directory(carpeta_web, ruta)

    from .demo import registrar_comando
    registrar_comando(app)
    return app
