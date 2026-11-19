"""Reservas (contrato §5) y resultados (§6)."""
import re

from conftest import crear_sesion, error, login, reservar


def test_reservar_devuelve_objeto_del_contrato(client, marta, bd):
    r = client.post("/api/reservas", json={"sesion_id": 11, "numero_jugadores": 4}, headers=marta)
    assert r.status_code == 201 and r.headers["Location"].startswith("/api/reservas/")
    x = r.get_json()
    assert set(x) == {"id", "usuario_id", "sesion_id", "numero_jugadores", "estado", "fecha_reserva", "sesion"}
    assert x["usuario_id"] == 3 and x["estado"] == "ACTIVA"
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d", x["fecha_reserva"])
    assert x["sesion"]["sala"] == {"nombre": "Atraco al Banco"}
    assert bd("SELECT estado FROM sesiones WHERE id = 11") == [("RESERVADA",)]


def test_el_usuario_sale_del_token_no_del_cuerpo(client, marta, bd):
    r = client.post("/api/reservas", json={"sesion_id": 11, "numero_jugadores": 2, "usuario_id": 4}, headers=marta)
    assert r.get_json()["usuario_id"] == 3


def test_admin_no_reserva(client, admin):
    assert client.post("/api/reservas", json={"sesion_id": 11, "numero_jugadores": 2}, headers=admin).status_code == 403


def test_reglas_de_jugadores_422(client, marta):
    for n in (1, 7):  # mínimo 2; capacidad de la sala 3 = 6
        r = client.post("/api/reservas", json={"sesion_id": 11, "numero_jugadores": n}, headers=marta)
        assert r.status_code == 422 and error(r) == "REGLA_NEGOCIO", n


def test_sesion_ocupada_409(client, marta):
    r = client.post("/api/reservas", json={"sesion_id": 8, "numero_jugadores": 2}, headers=marta)
    assert r.status_code == 409


def test_sesion_pasada_422(client, marta):
    assert client.post("/api/reservas", json={"sesion_id": 1, "numero_jugadores": 2}, headers=marta).status_code in (409, 422)
    r = client.post("/api/reservas", json={"sesion_id": 7, "numero_jugadores": 2}, headers=marta)
    assert r.status_code == 422


def test_listar_reservas_propias_y_admin(client, marta, admin):
    mias = client.get("/api/reservas", headers=marta).get_json()
    assert mias and all(r["usuario_id"] == 3 for r in mias)
    assert len(client.get("/api/reservas", headers=admin).get_json()) == 10
    assert all(r["estado"] == "CANCELADA" for r in client.get("/api/reservas?estado=CANCELADA", headers=admin).get_json())


def test_reserva_ajena_403(client, marta):
    assert client.get("/api/reservas/2", headers=marta).status_code == 403


def test_cancelar_y_volver_a_reservar(client, marta, javier, bd):
    rid = reservar(client, marta, 11)
    r = client.put(f"/api/reservas/{rid}", json={"estado": "CANCELADA"}, headers=marta)
    assert r.status_code == 200 and r.get_json()["estado"] == "CANCELADA"
    assert bd("SELECT estado FROM sesiones WHERE id = 11") == [("DISPONIBLE",)]
    # Con la migración A, otra persona puede reservar la sesión liberada
    assert client.post("/api/reservas", json={"sesion_id": 11, "numero_jugadores": 2}, headers=javier).status_code == 201


def test_sin_migracion_no_se_puede_volver_a_reservar(client_sin_migracion):
    c = client_sin_migracion
    marta, javier = login(c, "marta.garcia@mail.com"), login(c, "javi.perez@mail.com")
    rid = reservar(c, marta, 11)
    c.put(f"/api/reservas/{rid}", json={"estado": "CANCELADA"}, headers=marta)
    r = c.post("/api/reservas", json={"sesion_id": 11, "numero_jugadores": 2}, headers=javier)
    assert r.status_code == 409


def test_cancelar_reglas(client, marta, javier, admin):
    rid = reservar(client, marta, 11)
    assert client.put(f"/api/reservas/{rid}", json={"estado": "CANCELADA"}, headers=javier).status_code == 403
    assert client.put(f"/api/reservas/{rid}", json={"estado": "ACTIVA"}, headers=marta).status_code == 400
    client.put(f"/api/reservas/{rid}", json={"estado": "CANCELADA"}, headers=marta)
    assert client.put(f"/api/reservas/{rid}", json={"estado": "CANCELADA"}, headers=marta).status_code == 409


def test_plazo_de_24_horas(client, marta, admin, bd):
    sid = crear_sesion(client, admin, bd, minutos=120)  # empieza en 2 horas
    rid = reservar(client, marta, sid)
    r = client.put(f"/api/reservas/{rid}", json={"estado": "CANCELADA"}, headers=marta)
    assert r.status_code == 422 and error(r) == "REGLA_NEGOCIO"
    # El administrador no tiene el límite de 24 h
    assert client.put(f"/api/reservas/{rid}", json={"estado": "CANCELADA"}, headers=admin).status_code == 200


# ----- Resultados -----

def test_resultados_solo_admin(client, marta, admin):
    assert client.get("/api/resultados", headers=marta).status_code == 403
    datos = client.get("/api/resultados", headers=admin).get_json()
    assert len(datos) == 6
    assert set(datos[0]) == {"id", "sesion_id", "nombre_equipo", "tiempo_minutos", "superada"}


def test_registrar_resultado(client, admin):
    datos = {"sesion_id": 8, "nombre_equipo": "Los Detectives", "tiempo_minutos": 70, "superada": True}
    r = client.post("/api/resultados", json=datos, headers=admin)
    assert r.status_code == 201 and r.get_json()["tiempo_minutos"] == 70
    assert client.post("/api/resultados", json=datos, headers=admin).status_code == 409


def test_resultado_invalido(client, admin):
    r = client.post("/api/resultados", json={"sesion_id": 8, "nombre_equipo": "X", "superada": True}, headers=admin)
    assert r.status_code == 400
    r = client.post("/api/resultados", json={"sesion_id": 999, "nombre_equipo": "X", "superada": False}, headers=admin)
    assert r.status_code == 422
