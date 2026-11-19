# Backend Sprint 3 — Implementación del contrato REST

**Responsable:** David · **Contrato:** `doc/api_rest.md` (v2.0) · **Cliente:** `src/js/api.js`
**Tecnología:** Flask + SQLAlchemy + PostgreSQL · Código en `src/backend/`

---

## 1. Estado

| Sección del contrato | Estado |
|---|---|
| §2 Registro y login (token, bloqueo tras 3 fallos, hash con sal) | ✅ Implementado |
| §3 Salas | ✅ Implementado |
| §4 Sesiones | ✅ Implementado |
| §5 Reservas (transacción con bloqueo, 2 ≤ jugadores ≤ capacidad, plazo 24 h) | ✅ Implementado |
| §6 Resultados | ✅ Implementado |
| §7 Retos, pistas, objetos y dependencias (HMAC, sin ciclos) | ✅ Implementado |
| §8 Partidas, intentos, pistas, objetos, progreso | ✅ Implementado |
| Retos `OPCION` y `OBJETO` | ✅ Implementado **si se aplica `migracion_sprint3.sql`** (pendiente de aprobar) |
| Flask sirve la web (`src/`) | ✅ Implementado |

**Pruebas:** 73 pruebas automáticas (`src/backend/tests/`) contra PostgreSQL real, con y sin la migración, más una prueba de dos reservas simultáneas por HTTP (una entra y la otra recibe 409).

### Criterios de aceptación del contrato (§10)

| # | Criterio | Cómo se cumple |
|---|---|---|
| 1 | JSON válido y códigos HTTP | Todas las respuestas son JSON; errores `{error: {codigo, mensaje}}` |
| 2 | GET no modifica; POST → 201 identificable | 201 con cabecera `Location`; ningún GET escribe (ni siquiera al agotarse el tiempo) |
| 3 | Persistencia tras reiniciar | Prueba `test_progreso_persiste_entre_reinicios` |
| 4 | Jugador sin acciones de admin ni reservas ajenas | 403 comprobado en todas las rutas de administración y recursos ajenos |
| 5 | Sin doble reserva simultánea | `SELECT … FOR UPDATE` + índice único; probado con dos peticiones a la vez |
| 6 | Capacidad y plazo de cancelación | 422 `REGLA_NEGOCIO` |
| 7 | Datos en las 9 tablas | Retos, pistas, objetos, progreso, intentos, pistas usadas e inventario |
| 8 | Sin soluciones, hashes ni pistas no usadas | Comprobado buscando los textos en las respuestas |
| 9 | Partidas ajenas inaccesibles | 403 |
| 10 | Progreso e inventario recuperables | `GET /api/partidas/{id}` reconstruye todo desde la BD |
| 11 | Nombres de campos = contrato | Comprobado en las pruebas (claves exactas) |
| 12 | Errores útiles y sin datos sensibles | Mensajes en español; nunca trazas ni SQL |

---

## 2. Reglas de negocio aplicadas

| Regla | Implementación |
|---|---|
| Iniciar partida | Desde 15 min antes de la sesión hasta su hora de fin prevista |
| Límite de juego | `inicio + duracion_minutos`; al superarse, la siguiente acción cierra la partida como `AGOTADA` (409) |
| Progreso inicial | Reto sin prerrequisitos activos → `DISPONIBLE`; con prerrequisitos → `BLOQUEADO` |
| Desbloqueo | Al completar un reto, pasan a `DISPONIBLE` los que tienen todos sus prerrequisitos completados |
| Victoria | Todos los retos de la partida `COMPLETADO` → `SUPERADA` |
| Reto bloqueado en `GET` | Título "Reto bloqueado", sin descripción ni pistas |
| Pistas | Una vez por partida; su `contenido` solo aparece después de usarla |
| Tiempo del resultado | `ceil((fin − inicio + penalizaciones) / 60)` minutos |
| Nombre del equipo | Nombre del titular de la reserva |
| Respuestas | Normalizadas (sin mayúsculas, tildes ni espacios sobrantes) + HMAC-SHA256 con `RESPUESTA_SECRET`; comparación en tiempo constante |
| Cancelar reserva | Jugador: hasta 24 h antes. Admin: hasta que empiece la sesión. Si la partida ya ha empezado → 409; si está `PENDIENTE`, se elimina |
| Cambios de retos | No se pueden crear, editar o borrar retos ni dependencias de una sala con partidas `EN_CURSO` (409) |

### Códigos de error (`error.codigo`)

| HTTP | `codigo` |
|---|---|
| 400 | `VALIDACION` |
| 401 | `NO_AUTENTICADO` |
| 403 | `PROHIBIDO`, `CUENTA_BLOQUEADA` |
| 404 | `NO_ENCONTRADO` |
| 409 | `CONFLICTO` |
| 422 | `REGLA_NEGOCIO` |
| 500 | `ERROR_INTERNO` |
| 503 | `SIN_BASE_DE_DATOS` |

---

## 3. Añadidos respecto al contrato (no rompen `api.js`)

Son campos y rutas **nuevos**; ninguno cambia ni quita lo acordado.

| Dónde | Añadido | Para qué |
|---|---|---|
| `GET /api/salas/{id}/retos` | En cada reto: `pistas` (con contenido), `prerequisitos` (ids) y, si es OPCION, `opciones` | Que el panel de administración vea la configuración completa |
| `GET /api/partidas` y `/{id}` | `sesion_id`, `sala: {id, nombre}` | Mostrar el nombre de la sala |
| `GET /api/partidas/{id}` | `retos_totales`, `retos_completados`, `penalizacion_segundos`, `segundos_restantes` | Barra de progreso y cronómetro (el tiempo lo decide el servidor) |
| `GET /api/partidas/{id}` | En retos OPCION disponibles: `opciones` | Mostrar las alternativas al jugador |
| Retos (alta/edición) | `opciones` (OPCION) y `objeto_requerido_id` (OBJETO) | Decisiones B y C |
| Objetos (alta) | `reto_desbloqueo_id` (opcional) | Decisión C |
| `GET /api/reservas/{id}` | Ruta nueva | Ver una reserva |
| `GET /api/salas/{id}/objetos` | Ruta nueva (ADMIN) | Listar los objetos de una sala |
| `POST /api/partidas/{id}/abandonar` | Ruta nueva | El estado `ABANDONADA` existe en el SQL pero no tenía ruta |
| `GET /api/health` | Ruta nueva | Comprobar servidor y base de datos |

### Límites declarados (como permite el contrato §7)
- No hay edición ni borrado de **pistas** y **objetos** (solo alta).
- No hay límite de intentos por reto (todos se guardan en `intentos_reto`).

---

## 4. Base de datos

| Archivo | Qué es | Estado |
|---|---|---|
| `src/db/schema.sql`, `seed.sql` | Sprint 2 (definitivos) | Sin cambios |
| `src/db/usuario.sql` | Usuario `escapeuser` | Sin cambios |
| `src/db/ampliacion_sprint3.sql`, `verificacion_sprint3.sql` | 9 tablas de Ferran | Sin cambios |
| `src/db/migracion_sprint3.sql` | Decisiones A, B y C + propietario `escapeuser` | **Propuesta, pendiente de aprobar** |

`migracion_sprint3.sql`:
- **A.** Cambia `reservas.sesion_id UNIQUE` por "una sola reserva ACTIVA por sesión" (índice único parcial).
- **B.** Tabla `opciones_reto (id, reto_id, orden, texto)`.
- **C.** `retos.objeto_requerido_id` y `objetos.reto_desbloqueo_id`, con FK compuestas para no mezclar salas.

El backend detecta si la migración está aplicada: sin ella todo funciona salvo la re-reserva (409) y los tipos OPCION/OBJETO (422).

---

## 5. Integración con el frontend

1. Flask sirve `src/`: la web se abre en `http://127.0.0.1:5000` y la API está en `/api` (mismo origen, sin CORS).
2. En `api.js`, `API_BASE` debería ser **`'/api'`**. Con `http://127.0.0.1:5000/api` funciona si se abre la web con `127.0.0.1`, pero falla si se abre con `localhost` (otro origen).
3. Flask nunca sirve `src/db/` ni `src/backend/`, ni archivos que no sean de web (`.sql`, `.py`, `.env`…).
4. Token: el login devuelve `access_token`; el frontend lo guarda en memoria y lo envía como `Authorization: Bearer …`.
