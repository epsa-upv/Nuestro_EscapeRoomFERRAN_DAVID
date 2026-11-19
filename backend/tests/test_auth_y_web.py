"""Autenticación (contrato §2), formato de errores y servidor web."""
from conftest import PASSWORD, error, login


def test_registro_devuelve_usuario_sin_hash(client, bd):
    r = client.post("/api/auth/registro",
                    json={"nombre": "Carlos Vidal", "email": "Carlos@Mail.com", "password": "ClaveSegura123!"})
    assert r.status_code == 201
    assert r.get_json() == {"id": 11, "nombre": "Carlos Vidal", "email": "carlos@mail.com", "rol": "JUGADOR"}
    assert r.headers["Location"] == "/api/usuarios/11"
    (h,), = bd("SELECT password_hash FROM usuarios WHERE id = 11")
    assert "ClaveSegura123!" not in h and h.startswith(("scrypt:", "pbkdf2:"))


def test_registro_email_repetido_409(client):
    r = client.post("/api/auth/registro",
                    json={"nombre": "Otra", "email": "MARTA.GARCIA@mail.com", "password": "ClaveSegura123!"})
    assert r.status_code == 409 and error(r) == "CONFLICTO"


def test_registro_datos_incorrectos_400(client):
    for malo in ({"nombre": "Ana", "email": "no-email", "password": "ClaveSegura123!"},
                 {"nombre": "Ana", "email": "ana@mail.com", "password": "corta"},
                 {"email": "ana@mail.com", "password": "ClaveSegura123!"}):
        r = client.post("/api/auth/registro", json=malo)
        assert r.status_code == 400 and error(r) == "VALIDACION", malo


def test_formato_de_error_del_contrato(client):
    r = client.post("/api/auth/registro", json={})
    cuerpo = r.get_json()
    assert set(cuerpo) == {"error"} and set(cuerpo["error"]) == {"codigo", "mensaje"}


def test_login_devuelve_access_token_y_usuario(client):
    r = client.post("/api/auth/login", json={"email": "marta.garcia@mail.com", "password": PASSWORD})
    datos = r.get_json()
    assert r.status_code == 200 and datos["access_token"]
    assert datos["usuario"] == {"id": 3, "nombre": "Marta García", "email": "marta.garcia@mail.com", "rol": "JUGADOR"}


def test_registro_y_login_de_usuario_nuevo(client):
    client.post("/api/auth/registro", json={"nombre": "Carlos", "email": "c@mail.com", "password": "ClaveSegura123!"})
    assert client.post("/api/auth/login", json={"email": "c@mail.com", "password": "ClaveSegura123!"}).status_code == 200


def test_credenciales_incorrectas_401(client):
    r = client.post("/api/auth/login", json={"email": "marta.garcia@mail.com", "password": "mala"})
    assert r.status_code == 401 and error(r) == "NO_AUTENTICADO"
    assert client.post("/api/auth/login", json={"email": "nadie@mail.com", "password": "x"}).status_code == 401


def test_tres_fallos_bloquean_la_cuenta(client, bd):
    datos = {"email": "lucia.sanchis@mail.com", "password": "mala"}
    assert client.post("/api/auth/login", json=datos).status_code == 401
    assert client.post("/api/auth/login", json=datos).status_code == 401
    r = client.post("/api/auth/login", json=datos)
    assert r.status_code == 403 and error(r) == "CUENTA_BLOQUEADA"
    datos["password"] = PASSWORD
    assert client.post("/api/auth/login", json=datos).status_code == 403
    assert bd("SELECT bloqueado, intentos_fallidos FROM usuarios WHERE id = 5") == [(True, 3)]


def test_cuenta_bloqueada_del_seed_403(client):
    r = client.post("/api/auth/login", json={"email": "nerea.domenech@mail.com", "password": PASSWORD})
    assert r.status_code == 403 and error(r) == "CUENTA_BLOQUEADA"


def test_login_correcto_reinicia_intentos(client, bd):
    login(client, "javi.perez@mail.com")  # tenía 1 intento fallido en el seed
    assert bd("SELECT intentos_fallidos FROM usuarios WHERE id = 4") == [(0,)]


def test_token_falso_o_ausente_401(client):
    assert error(client.get("/api/reservas")) == "NO_AUTENTICADO"
    r = client.get("/api/reservas", headers={"Authorization": "Bearer inventado"})
    assert r.status_code == 401


def test_hash_ficticio_del_seed_no_permite_entrar(client_sin_migracion, bd):
    bd("UPDATE usuarios SET password_hash = '$2b$10$ficticio' WHERE id = 4")
    r = client_sin_migracion.post("/api/auth/login", json={"email": "javi.perez@mail.com", "password": "loquesea"})
    assert r.status_code == 401


# ----- Servidor web -----

def test_flask_sirve_la_web(client):
    assert client.get("/").status_code == 200
    r = client.get("/js/api.js")
    assert r.status_code == 200 and b"EscapeAPI" in r.data


def test_no_sirve_archivos_privados(client):
    for ruta in ("/db/schema.sql", "/backend/run.py", "/backend/.env", "/backend/app/config.py", "/../README.md"):
        assert client.get(ruta).status_code == 404, ruta


def test_ruta_api_inexistente_json(client):
    r = client.get("/api/no-existe")
    assert r.status_code == 404 and error(r) == "NO_ENCONTRADO"


def test_health(client):
    assert client.get("/api/health").get_json() == {"estado": "ok", "base_de_datos": "ok"}
