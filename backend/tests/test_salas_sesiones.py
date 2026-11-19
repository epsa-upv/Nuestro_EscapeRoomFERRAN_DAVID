"""Salas (contrato §3) y sesiones (§4)."""
from conftest import crear_sesion, error, momento

SALA = {"nombre": "El Submarino", "tematica": "Aventura", "dificultad": "MEDIA",
        "duracion_minutos": 60, "capacidad": 5, "activa": True}
CLAVES_SALA = {"id", "nombre", "tematica", "dificultad", "duracion_minutos", "capacidad", "activa"}


def test_listar_salas_y_filtro_activa(client):
    salas = client.get("/api/salas").get_json()
    assert len(salas) == 5 and set(salas[0]) == CLAVES_SALA
    assert len(client.get("/api/salas?activa=true").get_json()) == 4
    assert len(client.get("/api/salas?activa=false").get_json()) == 1


def test_sala_inexistente_404(client):
    assert error(client.get("/api/salas/999")) == "NO_ENCONTRADO"


def test_crear_sala_permisos(client, marta):
    assert client.post("/api/salas", json=SALA).status_code == 401
    assert client.post("/api/salas", json=SALA, headers=marta).status_code == 403


def test_crear_sala_persiste(client, admin, bd):
    r = client.post("/api/salas", json=SALA, headers=admin)
    assert r.status_code == 201 and r.headers["Location"] == f"/api/salas/{r.get_json()['id']}"
    assert bd("SELECT nombre FROM salas WHERE id = %s", (r.get_json()["id"],)) == [("El Submarino",)]


def test_crear_sala_nombre_repetido_409(client, admin):
    assert client.post("/api/salas", json=dict(SALA, nombre="atraco al banco"), headers=admin).status_code == 409


def test_crear_sala_invalida_400(client, admin):
    for malo in (dict(SALA, dificultad="EXTREMA"), dict(SALA, capacidad=1), dict(SALA, nombre="")):
        r = client.post("/api/salas", json=malo, headers=admin)
        assert r.status_code == 400 and error(r) == "VALIDACION", malo


def test_put_sala_completa(client, admin):
    r = client.put("/api/salas/3", json=dict(SALA, nombre="Atraco al Banco", capacidad=7), headers=admin)
    assert r.status_code == 200 and r.get_json()["capacidad"] == 7


def test_put_sala_incompleta_400(client, admin):
    assert client.put("/api/salas/3", json={"capacidad": 7}, headers=admin).status_code == 400


def test_put_sala_capacidad_menor_que_reservas_422(client, admin):
    # La sala 2 tiene una reserva futura de 4 jugadores
    r = client.put("/api/salas/2", json=dict(SALA, nombre="La Cripta del Conde", capacidad=3), headers=admin)
    assert r.status_code == 422 and error(r) == "REGLA_NEGOCIO"


def test_borrar_sala(client, admin):
    assert error(client.delete("/api/salas/1", headers=admin)) == "CONFLICTO"
    nueva = client.post("/api/salas", json=SALA, headers=admin).get_json()
    r = client.delete(f"/api/salas/{nueva['id']}", headers=admin)
    assert r.status_code == 204 and r.data == b""


# ----- Sesiones -----

def test_sesion_incluye_sala(client):
    s = client.get("/api/sesiones/8").get_json()
    assert set(s) == {"id", "sala_id", "fecha", "hora_inicio", "estado", "sala"}
    assert s["sala"] == {"id": 1, "nombre": "El Laboratorio Perdido", "capacidad": 5, "duracion_minutos": 60}
    assert len(s["hora_inicio"]) == 5


def test_filtros_de_sesiones(client):
    disponibles = client.get("/api/sesiones?estado=DISPONIBLE").get_json()
    assert disponibles and all(s["estado"] == "DISPONIBLE" for s in disponibles)
    s8 = client.get("/api/sesiones/8").get_json()
    por_fecha = client.get(f"/api/sesiones?sala_id=1&fecha={s8['fecha']}").get_json()
    assert [s["id"] for s in por_fecha] == [8]
    assert client.get("/api/sesiones?estado=RARO").status_code == 400


def test_crear_sesion(client, admin, bd):
    sid = crear_sesion(client, admin, bd, sala_id=3, minutos=120)
    assert client.get(f"/api/sesiones/{sid}").get_json()["estado"] == "DISPONIBLE"


def test_crear_sesion_reglas(client, admin, bd):
    f, h = momento(bd, -60)
    r = client.post("/api/sesiones", json={"sala_id": 1, "fecha": f, "hora_inicio": h}, headers=admin)
    assert r.status_code == 422
    f, h = momento(bd, 600)
    r = client.post("/api/sesiones", json={"sala_id": 5, "fecha": f, "hora_inicio": h}, headers=admin)
    assert r.status_code == 422  # sala inactiva
    s8 = client.get("/api/sesiones/8").get_json()
    r = client.post("/api/sesiones", json={"sala_id": 1, "fecha": s8["fecha"], "hora_inicio": "17:00"}, headers=admin)
    assert r.status_code == 409
    r = client.post("/api/sesiones", json={"sala_id": 1, "fecha": "17/11/2026", "hora_inicio": "17:00"}, headers=admin)
    assert r.status_code == 400


def test_put_sesion_cancelar_cancela_reserva(client, admin, bd):
    s = client.get("/api/sesiones/8").get_json()
    r = client.put("/api/sesiones/8", json={"sala_id": 1, "fecha": s["fecha"], "hora_inicio": s["hora_inicio"],
                                             "estado": "CANCELADA"}, headers=admin)
    assert r.status_code == 200 and r.get_json()["estado"] == "CANCELADA"
    assert bd("SELECT estado FROM reservas WHERE id = 8") == [("CANCELADA",)]


def test_put_sesion_con_reserva_no_cambia_hora(client, admin):
    s = client.get("/api/sesiones/8").get_json()
    r = client.put("/api/sesiones/8", json={"sala_id": 1, "fecha": s["fecha"], "hora_inicio": "11:00",
                                             "estado": "RESERVADA"}, headers=admin)
    assert r.status_code == 409


def test_borrar_sesion(client, admin, bd):
    assert client.delete("/api/sesiones/8", headers=admin).status_code == 409
    sid = crear_sesion(client, admin, bd, minutos=300)
    assert client.delete(f"/api/sesiones/{sid}", headers=admin).status_code == 204
