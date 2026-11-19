"""Retos/pistas/objetos/dependencias (contrato §7) y partidas (§8).

Datos demo de la sala 1 (con migración):
  reto 1 TEXTO  "azul-rojo-verde"            pistas 1 (30 s) y 2 (60 s)
  reto 2 CODIGO "4721"     requiere reto 1     pista 3 (30 s)
  reto 3 OPCION "GENOMA"   requiere reto 2     pista 4
  reto 4 OBJETO (Tarjeta)  requiere reto 3
  objeto 1 "Tarjeta de acceso": se puede recoger al completar el reto 2
"""
import json

from conftest import crear_sesion, error, login, partida_en_curso, reservar

RETO = {"titulo": "Código nuevo", "descripcion": "Cuatro cifras", "tipo": "CODIGO", "orden": 9,
        "activo": True, "respuesta": "1234"}


def intento(client, h, pid, reto, respuesta):
    return client.post(f"/api/partidas/{pid}/retos/{reto}/intentos", json={"respuesta": respuesta}, headers=h)


# ----- Administración -----

def test_listado_de_retos_sin_soluciones(client, admin, marta):
    assert client.get("/api/salas/1/retos", headers=marta).status_code == 403
    r = client.get("/api/salas/1/retos", headers=admin)
    texto = r.get_data(as_text=True)
    assert "respuesta_hash" not in texto and "4721" not in texto and "azul-rojo-verde" not in texto
    retos = r.get_json()
    assert [x["orden"] for x in retos] == [1, 2, 3, 4]
    assert retos[1]["prerequisitos"] == [1] and len(retos[0]["pistas"]) == 2
    assert retos[2]["opciones"] == ["GENOMA", "PROTEINA", "CELULA"]


def test_crear_reto_guarda_solo_hmac(client, admin, bd):
    r = client.post("/api/salas/3/retos", json=RETO, headers=admin)
    assert r.status_code == 201
    x = r.get_json()
    assert "respuesta" not in x and "respuesta_hash" not in x
    (h,), = bd("SELECT respuesta_hash FROM retos WHERE id = %s", (x["id"],))
    assert len(h) == 64 and h != "1234"


def test_crear_reto_validaciones(client, admin):
    sin_respuesta = {k: v for k, v in RETO.items() if k != "respuesta"}
    assert client.post("/api/salas/3/retos", json=sin_respuesta, headers=admin).status_code == 400
    assert client.post("/api/salas/1/retos", json=dict(RETO, orden=1), headers=admin).status_code == 409
    assert client.post("/api/salas/3/retos", json=dict(RETO, tipo="RARO"), headers=admin).status_code == 400


def test_reto_opcion(client, admin):
    base = dict(RETO, tipo="OPCION", opciones=["Rojo", "Verde"], respuesta="verde")
    assert client.post("/api/salas/3/retos", json=base, headers=admin).status_code == 201
    r = client.post("/api/salas/3/retos", json=dict(base, orden=10, respuesta="Azul"), headers=admin)
    assert r.status_code == 422


def test_reto_objeto(client, admin):
    obj = client.post("/api/salas/3/objetos", json={"nombre": "Ganzúa", "descripcion": "", "activo": True},
                      headers=admin).get_json()
    datos = {"titulo": "Cerradura", "descripcion": "Ábrela", "tipo": "OBJETO", "orden": 9, "activo": True,
             "objeto_requerido_id": obj["id"]}
    assert client.post("/api/salas/3/retos", json=datos, headers=admin).status_code == 201
    # Un objeto de otra sala no vale
    r = client.post("/api/salas/3/retos", json=dict(datos, orden=10, objeto_requerido_id=1), headers=admin)
    assert r.status_code == 422


def test_put_reto_conserva_o_cambia_la_solucion(client, admin, bd):
    (antes,), = bd("SELECT respuesta_hash FROM retos WHERE id = 2")
    cambios = {"titulo": "Microscopio", "descripcion": "Nuevo texto", "tipo": "CODIGO", "orden": 2, "activo": True}
    assert client.put("/api/retos/2", json=cambios, headers=admin).status_code == 200
    assert bd("SELECT respuesta_hash, titulo FROM retos WHERE id = 2") == [(antes, "Microscopio")]
    client.put("/api/retos/2", json=dict(cambios, respuesta="9999"), headers=admin)
    assert bd("SELECT respuesta_hash FROM retos WHERE id = 2")[0][0] != antes


def test_pistas_objetos_y_dependencias(client, admin):
    r = client.post("/api/retos/5/pistas", json={"orden": 2, "contenido": "Mira el reloj", "penalizacion_segundos": 45},
                    headers=admin)
    assert r.status_code == 201 and r.get_json()["penalizacion_segundos"] == 45
    assert client.post("/api/retos/5/pistas", json={"orden": 2, "contenido": "Otra"}, headers=admin).status_code == 409
    r = client.post("/api/salas/2/objetos", json={"nombre": "Vela", "descripcion": "Encendida", "activo": True},
                    headers=admin)
    assert r.status_code == 201
    assert client.post("/api/salas/2/objetos", json={"nombre": "vela"}, headers=admin).status_code == 409
    assert len(client.get("/api/salas/2/objetos", headers=admin).get_json()) == 1


def test_dependencias_reglas(client, admin):
    assert error(client.post("/api/retos/1/dependencias", json={"prerequisito_id": 3}, headers=admin)) == "REGLA_NEGOCIO"  # ciclo
    assert client.post("/api/retos/1/dependencias", json={"prerequisito_id": 1}, headers=admin).status_code == 422
    assert client.post("/api/retos/1/dependencias", json={"prerequisito_id": 5}, headers=admin).status_code == 422
    assert client.post("/api/retos/2/dependencias", json={"prerequisito_id": 1}, headers=admin).status_code == 409
    assert client.post("/api/retos/6/dependencias", json={"prerequisito_id": 5}, headers=admin).status_code == 409
    nuevo = client.post("/api/salas/2/retos", json=dict(RETO, orden=3), headers=admin).get_json()
    assert client.post(f"/api/retos/{nuevo['id']}/dependencias", json={"prerequisito_id": 6},
                       headers=admin).status_code == 201


def test_borrar_reto(client, admin, marta, bd):
    nuevo = client.post("/api/salas/3/retos", json=RETO, headers=admin).get_json()
    assert client.delete(f"/api/retos/{nuevo['id']}", headers=admin).status_code == 204
    partida_en_curso(client, admin, marta, bd)
    r = client.delete("/api/retos/1", headers=admin)
    assert r.status_code == 409  # hay una partida en curso que lo usa


def test_sin_migracion_opcion_y_objeto_422(client_sin_migracion):
    c = client_sin_migracion
    admin = login(c, "ferran@escapehub.es")
    r = c.post("/api/salas/3/retos", json=dict(RETO, tipo="OPCION", opciones=["a", "b"], respuesta="a"), headers=admin)
    assert r.status_code == 422
    r = c.post("/api/salas/3/retos", json=dict(RETO, tipo="OBJETO", objeto_requerido_id=1), headers=admin)
    assert r.status_code == 422
    assert c.post("/api/salas/3/retos", json=RETO, headers=admin).status_code == 201


# ----- Partidas -----

def test_crear_partida_pendiente(client, admin, marta, bd):
    sid = crear_sesion(client, admin, bd)
    rid = reservar(client, marta, sid)
    r = client.post("/api/partidas", json={"reserva_id": rid, "sala_id": 3, "estado": "SUPERADA"}, headers=marta)
    assert r.status_code == 201
    p = r.get_json()
    assert p["estado"] == "PENDIENTE" and p["sala_id"] == 1 and p["retos"] == []  # se ignora lo enviado
    assert client.post("/api/partidas", json={"reserva_id": rid}, headers=marta).status_code == 409


def test_crear_partida_reglas(client, admin, marta, javier, bd):
    sid = crear_sesion(client, admin, bd)
    rid = reservar(client, marta, sid)
    assert client.post("/api/partidas", json={"reserva_id": rid}, headers=javier).status_code == 403
    assert client.post("/api/partidas", json={"reserva_id": rid}, headers=admin).status_code == 403  # solo JUGADOR
    assert client.post("/api/partidas", json={"reserva_id": 999}, headers=marta).status_code == 404
    client.put(f"/api/reservas/{rid}", json={"estado": "CANCELADA"}, headers=admin)
    r = client.post("/api/partidas", json={"reserva_id": rid}, headers=marta)
    assert r.status_code == 409 and error(r) == "CONFLICTO"  # reserva cancelada


def test_no_se_inicia_antes_de_hora(client, admin, marta, bd):
    sid = crear_sesion(client, admin, bd, minutos=60 * 48)
    rid = reservar(client, marta, sid)
    p = client.post("/api/partidas", json={"reserva_id": rid}, headers=marta).get_json()
    r = client.post(f"/api/partidas/{p['id']}/iniciar", json={}, headers=marta)
    assert r.status_code == 422 and error(r) == "REGLA_NEGOCIO"


def test_iniciar_crea_progreso(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    assert p["estado"] == "EN_CURSO" and p["inicio"] and p["fin"] is None
    estados = [(r["id"], r["estado"]) for r in p["retos"]]
    assert estados == [(1, "DISPONIBLE"), (2, "BLOQUEADO"), (3, "BLOQUEADO"), (4, "BLOQUEADO")]
    bloqueado = p["retos"][1]
    assert bloqueado["titulo"] == "Reto bloqueado" and bloqueado["descripcion"] is None and bloqueado["pistas"] == []
    pistas = p["retos"][0]["pistas"]
    assert [x["usada"] for x in pistas] == [False, False] and all("contenido" not in x for x in pistas)
    assert bd("SELECT count(*) FROM progreso_retos WHERE partida_id = %s", (p["id"],)) == [(4,)]


def test_nunca_se_envian_soluciones_ni_hashes(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    texto = json.dumps(client.get(f"/api/partidas/{p['id']}", headers=marta).get_json())
    for secreto in ("respuesta_hash", "azul-rojo-verde", "4721", "Fíjate en el orden"):
        assert secreto not in texto


def test_respuesta_incorrecta_y_correcta(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    r = intento(client, marta, p["id"], 1, "rojo")
    assert r.get_json() == {"correcta": False, "reto_estado": "DISPONIBLE", "partida_estado": "EN_CURSO"}
    assert intento(client, marta, p["id"], 2, "4721").status_code == 409  # bloqueado
    r = intento(client, marta, p["id"], 1, "  AZUL-Rojo-Verde ")
    assert r.get_json() == {"correcta": True, "reto_estado": "COMPLETADO", "partida_estado": "EN_CURSO"}
    assert intento(client, marta, p["id"], 1, "azul-rojo-verde").status_code == 409  # ya completado
    detalle = client.get(f"/api/partidas/{p['id']}", headers=marta).get_json()
    assert [r["estado"] for r in detalle["retos"]][:2] == ["COMPLETADO", "DISPONIBLE"]
    assert bd("SELECT correcta FROM intentos_reto WHERE partida_id = %s ORDER BY id", (p["id"],)) == [(False,), (True,)]


def test_pistas_en_partida(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    url = f"/api/partidas/{p['id']}/retos/1/pistas/1/usar"
    r = client.post(url, json={}, headers=marta)
    assert r.status_code == 200
    assert r.get_json() == {"id": 1, "contenido": "Fíjate en el orden de la tabla periódica del armario.",
                            "penalizacion_segundos": 30}
    assert client.post(url, json={}, headers=marta).status_code == 409
    assert client.post(f"/api/partidas/{p['id']}/retos/1/pistas/3/usar", json={}, headers=marta).status_code == 404
    assert client.post(f"/api/partidas/{p['id']}/retos/2/pistas/3/usar", json={}, headers=marta).status_code == 409
    pistas = client.get(f"/api/partidas/{p['id']}", headers=marta).get_json()["retos"][0]["pistas"]
    assert pistas[0]["usada"] and "contenido" in pistas[0] and "contenido" not in pistas[1]


def test_partida_completa_con_objeto(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    pid = p["id"]
    client.post(f"/api/partidas/{pid}/retos/1/pistas/1/usar", json={}, headers=marta)  # +30 s
    intento(client, marta, pid, 1, "azul-rojo-verde")
    # La tarjeta aún no se puede recoger (se desbloquea con el reto 2)
    assert client.post(f"/api/partidas/{pid}/objetos/1/recoger", json={}, headers=marta).status_code == 422
    intento(client, marta, pid, 2, "4721")
    detalle = client.get(f"/api/partidas/{pid}", headers=marta).get_json()
    assert detalle["objetos_disponibles"] == [{"id": 1, "nombre": "Tarjeta de acceso",
                                               "descripcion": "Aparece al resolver el microscopio"}]
    assert detalle["retos"][2]["opciones"] == ["GENOMA", "PROTEINA", "CELULA"]
    r = client.post(f"/api/partidas/{pid}/objetos/1/recoger", json={}, headers=marta)
    assert r.get_json() == {"objeto_id": 1, "consumido": False}
    assert client.post(f"/api/partidas/{pid}/objetos/1/recoger", json={}, headers=marta).status_code == 409
    assert intento(client, marta, pid, 3, "génoma").get_json()["correcta"] is True
    assert intento(client, marta, pid, 4, "x").status_code == 422  # el reto 4 se resuelve con un objeto
    r = client.post(f"/api/partidas/{pid}/retos/4/usar-objeto", json={"objeto_id": 1}, headers=marta)
    assert r.get_json() == {"correcta": True, "reto_estado": "COMPLETADO", "partida_estado": "SUPERADA"}

    final = client.get(f"/api/partidas/{pid}", headers=marta).get_json()
    assert final["estado"] == "SUPERADA" and final["fin"] and final["inventario"][0]["consumido"] is True
    (equipo, tiempo, superada), = bd("""SELECT nombre_equipo, tiempo_minutos, superada FROM resultados
                                        WHERE sesion_id = %s""", (p["sesion_id"],))
    assert equipo == "Marta García" and superada is True and tiempo == 1  # ~0 s + 30 s de pista -> 1 min
    assert intento(client, marta, pid, 1, "x").status_code == 409  # partida terminada


def test_usar_objeto_que_no_tienes(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    bd("UPDATE progreso_retos SET estado = 'DISPONIBLE' WHERE partida_id = %s AND reto_id = 4", (p["id"],))
    r = client.post(f"/api/partidas/{p['id']}/retos/4/usar-objeto", json={"objeto_id": 1}, headers=marta)
    assert r.status_code == 422


def test_tiempo_agotado(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    bd("UPDATE partidas SET inicio = now() - interval '2 hours' WHERE id = %s", (p["id"],))
    # Un GET no modifica la base de datos
    detalle = client.get(f"/api/partidas/{p['id']}", headers=marta).get_json()
    assert detalle["estado"] == "EN_CURSO" and detalle["segundos_restantes"] == 0
    assert bd("SELECT estado FROM partidas WHERE id = %s", (p["id"],)) == [("EN_CURSO",)]
    # La siguiente acción la cierra como AGOTADA
    assert intento(client, marta, p["id"], 1, "azul-rojo-verde").status_code == 409
    assert bd("SELECT estado FROM partidas WHERE id = %s", (p["id"],)) == [("AGOTADA",)]
    assert bd("SELECT superada, tiempo_minutos FROM resultados WHERE sesion_id = %s",
              (p["sesion_id"],)) == [(False, None)]


def test_permisos_de_partida(client, admin, marta, javier, bd):
    p = partida_en_curso(client, admin, marta, bd)
    assert client.get(f"/api/partidas/{p['id']}", headers=javier).status_code == 403
    assert client.get(f"/api/partidas/{p['id']}", headers=admin).status_code == 200
    assert intento(client, javier, p["id"], 1, "x").status_code == 403
    assert intento(client, admin, p["id"], 1, "x").status_code == 403  # solo el titular juega
    assert [x["id"] for x in client.get("/api/partidas", headers=marta).get_json()] == [p["id"]]
    assert client.get("/api/partidas", headers=javier).get_json() == []


def test_abandonar(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    r = client.post(f"/api/partidas/{p['id']}/abandonar", json={}, headers=marta)
    assert r.get_json()["estado"] == "ABANDONADA"
    assert bd("SELECT superada FROM resultados WHERE sesion_id = %s", (p["sesion_id"],)) == [(False,)]


def test_reserva_con_partida_empezada_no_se_cancela(client, admin, marta, bd):
    p = partida_en_curso(client, admin, marta, bd)
    assert client.put(f"/api/reservas/{p['reserva_id']}", json={"estado": "CANCELADA"},
                      headers=admin).status_code == 409


def test_progreso_persiste_entre_reinicios(app, admin, marta, bd):
    client = app.test_client()
    p = partida_en_curso(client, admin, marta, bd)
    intento(client, marta, p["id"], 1, "azul-rojo-verde")
    from app import create_app
    nuevo = create_app({"DATABASE_URL": app.config["DATABASE_URL"], "SECRET_KEY": "clave-pruebas",
                        "RESPUESTA_SECRET": "secreto-pruebas"}).test_client()
    h = login(nuevo, "marta.garcia@mail.com")
    retos = nuevo.get(f"/api/partidas/{p['id']}", headers=h).get_json()["retos"]
    assert retos[0]["estado"] == "COMPLETADO" and retos[1]["estado"] == "DISPONIBLE"


def test_sin_migracion_se_puede_jugar(client_sin_migracion, bd):
    c = client_sin_migracion
    admin, marta = login(c, "ferran@escapehub.es"), login(c, "marta.garcia@mail.com")
    p = partida_en_curso(c, admin, marta, bd)
    for reto, resp in ((1, "azul-rojo-verde"), (2, "4721")):
        assert intento(c, marta, p["id"], reto, resp).get_json()["correcta"]
    r = intento(c, marta, p["id"], 3, "genoma")  # sin migración, el reto 3 es TEXTO
    assert r.get_json()["partida_estado"] == "SUPERADA"
