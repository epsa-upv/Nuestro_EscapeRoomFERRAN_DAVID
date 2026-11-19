# Revisión cruzada: esquema real · `api_rest.md` · `api.js`

**Sprint 3 · EscapeHub** — Revisión de David antes de implementar Flask.
Objetivo: acordar lo que falta **antes** de programar, para que el backend encaje con el frontend sin rehacer código.

---

## 1. Qué se ha comprobado

Prueba realizada en PostgreSQL con los archivos definitivos del Sprint 2:

| Paso | Resultado |
|---|---|
| `schema.sql` + `seed.sql` del Sprint 2 (10 usuarios, 5 salas, 14 sesiones, 10 reservas, 6 resultados) | Correcto |
| `ampliacion_sprint3.sql` encima | Correcto, sin errores |
| `ampliacion_sprint3.sql` ejecutado una 2.ª vez | Correcto (no rompe nada) |
| `verificacion_sprint3.sql` | 9 tablas encontradas; 0 partidas incoherentes |

**Conclusión:** la ampliación es compatible con el esquema real. Faltan algunas piezas (sección 3) para que el contrato se pueda implementar entero.

---

## 2. Avisos sobre la base de datos de trabajo

### 2.1 Comprobar si la ampliación está instalada en la BD de David
`ampliacion_sprint3.sql` no consta como ejecutado en la BD de David. Antes de programar hay que ejecutar `verificacion_sprint3.sql` en su pgAdmin. Si no salen 9 filas, hay que ejecutar la ampliación (con copia de seguridad previa).

### 2.2 Permisos de `escapeuser`
Si la ampliación se ejecuta como `postgres`, las 9 tablas nuevas quedan a nombre de `postgres` y Flask (que se conecta como `escapeuser`) **no podrá usarlas**. Después de la ampliación hay que ejecutar:

```sql
ALTER TABLE retos              OWNER TO escapeuser;
ALTER TABLE dependencias_reto  OWNER TO escapeuser;
ALTER TABLE pistas             OWNER TO escapeuser;
ALTER TABLE objetos            OWNER TO escapeuser;
ALTER TABLE partidas           OWNER TO escapeuser;
ALTER TABLE progreso_retos     OWNER TO escapeuser;
ALTER TABLE intentos_reto      OWNER TO escapeuser;
ALTER TABLE pistas_utilizadas  OWNER TO escapeuser;
ALTER TABLE inventario_partida OWNER TO escapeuser;
ALTER VIEW vista_progreso_partida OWNER TO escapeuser;
```

### 2.3 No volver a ejecutar `seed.sql`
`seed.sql` empieza con `TRUNCATE … CASCADE`. Con las 14 tablas, **borra también partidas, progreso, intentos e inventario** (comprobado). Los datos de prueba del Sprint 3 irán en un archivo aparte.

---

## 3. Decisiones necesarias (bloquean la implementación)

### A. Re-reservar una sesión cancelada
**Problema:** `reservas.sesion_id` sigue siendo `UNIQUE` (`reservas_sesion_id_key`). Si se cancela una reserva, nadie más puede reservar esa sesión.
**Propuesta (migración):**

```sql
ALTER TABLE reservas DROP CONSTRAINT reservas_sesion_id_key;
CREATE UNIQUE INDEX uq_reserva_activa_por_sesion
    ON reservas (sesion_id) WHERE estado = 'ACTIVA';
```

El índice `ux_reservas_id_sesion` de la ampliación sigue siendo válido. No afecta a `api.js`.

### B. Retos de tipo `OPCION`
**Problema:** no hay dónde guardar las alternativas.
**Propuesta:** tabla `opciones_reto (id, reto_id, orden, texto)`. El jugador ve las opciones en `GET /api/partidas/{id}` y responde con el **texto** de la opción por el endpoint de intentos de siempre. **No cambia `api.js`.**
**Alternativa:** dejar `OPCION` fuera de este sprint (la API respondería `422`).

### C. Retos de tipo `OBJETO` y recoger objetos
**Problema:** no se sabe **qué objeto** resuelve cada reto ni **cuándo** se puede recoger un objeto (`objetos_disponibles`).
**Propuesta (2 columnas):**

| Columna nueva | Significado |
|---|---|
| `retos.objeto_requerido_id` | Objeto que hay que usar para resolver un reto `OBJETO` (obligatorio si `tipo = 'OBJETO'`, vacío en los demás) |
| `objetos.reto_desbloqueo_id` | Reto que hay que completar para que el objeto aparezca. Vacío = disponible desde el inicio |

Reglas: usar un objeto correcto completa el reto y lo marca `consumido`; un objeto que no está en el inventario → `422`. Ambas columnas con FK compuesta `(…, sala_id)` para no cruzar salas. **No cambia `api.js`** (solo se añaden campos opcionales en el alta de retos y objetos).
**Alternativa:** dejar `OBJETO` fuera de este sprint.

### D. Nombre del equipo en `resultados`
**Problema:** `resultados.nombre_equipo` es obligatorio, pero `partidas` no tiene ese dato y `POST /api/partidas` solo recibe `reserva_id`.
**Propuesta:** al terminar la partida, usar el **nombre del titular de la reserva**. Sin cambios de SQL ni de `api.js`.
**Alternativa:** campo opcional `nombre_equipo` en `POST /api/partidas` + columna en `partidas`.

### E. Reglas de tiempo, pistas y victoria
Propuesta para cerrar las reglas que el contrato deja abiertas:

| Regla | Propuesta |
|---|---|
| Iniciar partida | Solo entre **15 min antes** de la sesión y su **hora de fin prevista** (acordado) |
| Límite de juego | `inicio + duracion_minutos` de la sala; si se supera → `AGOTADA` |
| Penalización por pistas | Se suma al tiempo final (no reduce el tiempo de juego) |
| `tiempo_minutos` del resultado | `ceil((fin − inicio + penalizaciones) / 60)` |
| Victoria | Todos los retos **activos** de la sala `COMPLETADO` → `SUPERADA` |
| Retos al iniciar | Se crea `progreso_retos` para cada reto activo: `DISPONIBLE` si no tiene prerrequisitos, `BLOQUEADO` si los tiene |
| Reto bloqueado en `GET` | Título genérico "Reto bloqueado", sin descripción ni pistas |
| Pistas | Solo de retos `DISPONIBLE`; cada pista una vez; su `contenido` solo se devuelve después de usarla |
| Límite de intentos | Sin límite en el prototipo (se guardan todos en `intentos_reto`) |
| Cambios de retos | No se puede crear, editar ni borrar retos o dependencias de una sala con partidas `EN_CURSO` → `409` |

### F. `API_BASE` en `api.js` (importante para la integración)
**Problema:** `api.js` usa `http://127.0.0.1:5000/api`. Si Flask sirve el HTML y se abre como `http://localhost:5000`, el navegador lo trata como **otro origen** (`localhost` ≠ `127.0.0.1`) y bloquea las peticiones por CORS.
**Propuesta:** como Flask sirve el HTML, usar ruta relativa. Ferran solo cambia una línea:

```js
const API_BASE = window.ESCAPEHUB_API_BASE || '/api';
```

---

## 4. Diferencias menores (propuesta de cómo resolverlas)

| # | Tema | Contrato / api.js | Propuesta |
|---|---|---|---|
| 1 | Hash de contraseñas | Contrato: Werkzeug. Guía SQL: Argon2id/bcrypt | Werkzeug `generate_password_hash` (scrypt, con sal); es lo que dice el contrato |
| 2 | Usuarios demo | No subir contraseñas reales | Comando `flask crear-demo` que pone la contraseña leída del `.env` local; nada sensible en GitHub |
| 3 | Datos del juego para probar | No existen | Nuevo `seed_juego_dev.sql` (retos, pistas, objetos de ejemplo) **sin `TRUNCATE`**; los hashes de las respuestas los genera Flask con el secreto del `.env` |
| 4 | Secreto HMAC | Debe sobrevivir a reinicios | Variable `RESPUESTA_SECRET` en `.env`, distinta de `SECRET_KEY` |
| 5 | Fechas-hora con zona (`+01:00`) | `reservas.fecha_reserva` es `TIMESTAMP` sin zona | La conexión usa la zona `Europe/Madrid` y la API devuelve ISO 8601 con desfase |
| 6 | Ver pistas, dependencias y objetos (admin) | No hay `GET` de objetos | `GET /api/salas/{id}/retos` incluye pistas y prerrequisitos de cada reto; **añadir** `GET /api/salas/{id}/objetos` (ruta nueva, no rompe nada) |
| 7 | `PUT` de salas y sesiones | "Representación completa" | Se exigen todos los campos (si falta alguno → `400`) |
| 8 | Mínimo de jugadores | Contrato: 2 | `numero_jugadores` entre 2 y la capacidad de la sala → si no, `422` |
| 9 | `201` con cabecera `Location` | Contrato lo pide | Se incluye en todas las creaciones |
| 10 | Ranking público | `GET /api/resultados` solo ADMIN | Se respeta (solo ADMIN) |
| 11 | Editar o borrar sesiones | En el contrato, no en `api.js` | Se implementan igualmente (el frontend puede usarlos más adelante) |

### Códigos de error propuestos (`error.codigo`)

| HTTP | `codigo` | Cuándo |
|---|---|---|
| 400 | `VALIDACION` | Falta un campo, tipo o formato incorrecto |
| 401 | `NO_AUTENTICADO` | Sin token, token caducado o credenciales incorrectas |
| 403 | `PROHIBIDO` / `CUENTA_BLOQUEADA` | Sin permiso, recurso ajeno o usuario bloqueado |
| 404 | `NO_ENCONTRADO` | No existe |
| 409 | `CONFLICTO` | Sesión ocupada, duplicado, partida ya existe, reto no disponible… |
| 422 | `REGLA_NEGOCIO` | Capacidad, fecha pasada, fuera de plazo (24 h), fuera de horario, ciclo de dependencias… |
| 500 | `ERROR_INTERNO` | Fallo inesperado (sin detalles internos) |

`api.js` ya sabe leer este formato (`error.mensaje` y `error.codigo`).

---

## 5. Comprobación `api_rest.md` ↔ `api.js`

Todas las llamadas de `api.js` coinciden con rutas, métodos y cuerpos del contrato:

| `api.js` | Ruta | ¿Coincide? |
|---|---|---|
| `register`, `login` | `POST /auth/registro`, `POST /auth/login` | Sí |
| `rooms`, `room`, `addRoom`, `updateRoom`, `deleteRoom` | `/salas` | Sí |
| `sessions`, `addSession` | `/sesiones` | Sí |
| `reservations`, `book`, `cancel` | `/reservas` (cancelar con `PUT {estado: "CANCELADA"}`) | Sí |
| `challenges`, `addChallenge`, `updateChallenge`, `deleteChallenge` | `/salas/{id}/retos`, `/retos/{id}` | Sí |
| `addHint`, `addObject`, `addDependency` | `/retos/{id}/pistas`, `/salas/{id}/objetos`, `/retos/{id}/dependencias` | Sí |
| `games`, `game`, `createGame`, `startGame` | `/partidas`, `/partidas/{id}`, `/partidas/{id}/iniciar` | Sí |
| `submitAnswer`, `useHint`, `useObject`, `collectObject` | rutas de partida | Sí |
| `results`, `addResult` | `/resultados` | Sí |

Único cambio necesario en `api.js`: `API_BASE` relativo (sección 3.F).

---

## 6. Resumen para decidir

| # | Decisión | Propuesta de David |
|---|---|---|
| A | Re-reserva tras cancelar | Índice único parcial (migración) |
| B | Retos `OPCION` | Tabla `opciones_reto` |
| C | Retos `OBJETO` | Columnas `objeto_requerido_id` y `reto_desbloqueo_id` |
| D | `nombre_equipo` | Nombre del titular de la reserva |
| E | Reglas de juego | Tabla de la sección 3.E |
| F | `API_BASE` | `'/api'` relativo |

Cuando Ferran confirme (o cambie) estas seis decisiones:
1. Se prepara **un único archivo de migración** `migracion_sprint3.sql` con A, B y C (y permisos).
2. Se implementa Flask + SQLAlchemy contra el esquema resultante y el contrato.
3. Pruebas de integración: endpoints, permisos, transacciones, persistencia y la web de Ferran servida desde Flask.
