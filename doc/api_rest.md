# Contrato de API REST — EscapeHub

**Versión:** 2.0 · **Sprint:** 3 · **Responsables del contrato:** Ferran (interfaz y documentación) y David (implementación y persistencia).  
**Estado:** contrato propuesto, pendiente de aceptación e implementación por David.

## 1. Finalidad y arquitectura

La aplicación expone recursos `usuarios`, `salas`, `sesiones`, `reservas`, `resultados`, `retos`, `dependencias_reto`, `pistas`, `objetos`, `partidas`, `progreso_retos`, `intentos_reto`, `pistas_utilizadas` e `inventario_partida` mediante un servicio REST en Flask. El cliente web usa `fetch` y JSON; el servidor valida el acceso y las reglas de negocio y consulta PostgreSQL mediante SQLAlchemy. Las tablas corresponden a las cinco tablas originales y a las nueve tablas adicionales del modelo ampliado al finalizar Sprint 2. La interfaz **nunca** accede directamente a PostgreSQL.

- **Base local de API:** `http://127.0.0.1:5000/api` (modificable en `src/js/api.js`).
- **Representación:** `application/json; charset=utf-8`.
- **Autenticación:** `Authorization: Bearer <token>` en rutas privadas. El servidor genera el token al iniciar sesión y verifica su firma, caducidad y rol en cada solicitud. Nunca se confía en el rol enviado por el cliente.
- **Fechas:** `YYYY-MM-DD`; **horas:** `HH:mm` (hora local del negocio, Europe/Madrid); **fechas-hora** de eventos: ISO 8601.
- **Identificadores:** enteros positivos; las tablas SQL usan nombres españoles (`usuarios`, `salas`, etc.).
- **Cuerpo de error:** `{ "error": { "codigo": "VALIDACION", "mensaje": "Texto comprensible" } }`.
- **Sin cambios silenciosos:** los nombres de claves y rutas deben acordarse antes de desarrollar el frontend y el backend.

### Tabla general de códigos

| Código | Significado |
|---|---|
| 200 | Consulta o actualización correcta |
| 201 | Recurso creado; incluir `Location` |
| 204 | Eliminación correcta, sin cuerpo |
| 400 | Formato incorrecto o campo inválido |
| 401 | No autenticado, token ausente o expirado |
| 403 | No autorizado por rol o propiedad |
| 404 | Recurso inexistente |
| 409 | Conflicto: sesión ocupada, nombre/email duplicado, sala con sesiones, etc. |
| 422 | Datos bien formados pero que incumplen regla de negocio |
| 500 | Fallo interno; no exponer contraseñas ni trazas al cliente |

## 2. Usuarios y autenticación

### `POST /api/auth/registro` — Público

```json
{ "nombre": "Marta García", "email": "marta@example.com", "password": "ClaveSegura123!" }
```

Respuesta `201`:

```json
{ "id": 11, "nombre": "Marta García", "email": "marta@example.com", "rol": "JUGADOR" }
```

- No devolver `password_hash` ni la contraseña.
- Validar correo único, longitud de contraseña y campos obligatorios.
- Guardar hash adecuado con sal única (p. ej. Werkzeug `generate_password_hash`).

### `POST /api/auth/login` — Público

```json
{ "email": "marta@example.com", "password": "ClaveSegura123!" }
```

Respuesta `200`:

```json
{
  "access_token": "TOKEN_EMITIDO_POR_EL_SERVIDOR",
  "usuario": { "id": 11, "nombre": "Marta García", "email": "marta@example.com", "rol": "JUGADOR" }
}
```

- Respuesta `401` para credenciales incorrectas; `403` para una cuenta bloqueada.
- La lógica de intentos fallidos debe estar en servidor, usando `intentos_fallidos` y `bloqueado`.
- Los hashes ficticios del `seed.sql` del Sprint 2 **no** sirven para iniciar sesión. Preparar usuarios demo con hashes reales en un seed de desarrollo y documentar sus credenciales localmente; no subir contraseñas reales.
- El frontend conserva temporalmente el token **en memoria**, así que la sesión se pierde al recargar la página (decisión de prototipo, más prudente que persistir tokens en `localStorage`).

## 3. Salas

**Objeto de salida `Sala`:**

```json
{ "id": 1, "nombre": "La Cripta del Conde", "tematica": "Terror", "dificultad": "ALTA", "duracion_minutos": 75, "capacidad": 6, "activa": true }
```

| Método y URI | Permiso | Entrada | Salida |
|---|---|---|---|
| `GET /api/salas` | Público | `?activa=true` opcional | `200`, array de `Sala` |
| `GET /api/salas/{id}` | Público | Identificador | `200`, `Sala`; `404` |
| `POST /api/salas` | ADMIN | `nombre`, `tematica`, `dificultad`, `duracion_minutos`, `capacidad`, `activa` | `201`, `Sala`; `409` por nombre repetido |
| `PUT /api/salas/{id}` | ADMIN | Representación completa | `200`, `Sala`; `404`, `409`, `422` |
| `DELETE /api/salas/{id}` | ADMIN | Identificador | `204`; `409` si existen sesiones vinculadas |

Validaciones: nombre y temática no vacíos; `dificultad` ∈ `BAJA|MEDIA|ALTA`; duración positiva; capacidad entera ≥2. No usar borrado en cascada de sesiones por defecto, coherente con `ON DELETE RESTRICT` del Sprint 2.

## 4. Sesiones

**Objeto de salida `Sesion`:**

```json
{
  "id": 8, "sala_id": 1, "fecha": "2026-11-06", "hora_inicio": "17:00", "estado": "RESERVADA",
  "sala": { "id": 1, "nombre": "El Laboratorio Perdido", "capacidad": 5, "duracion_minutos": 60 }
}
```

| Método y URI | Permiso | Entrada | Salida |
|---|---|---|---|
| `GET /api/sesiones` | Público | `?sala_id=1&fecha=2026-11-06&estado=DISPONIBLE` opcionales | `200`, array de `Sesion` |
| `GET /api/sesiones/{id}` | Público | ID | `200`, `Sesion`; `404` |
| `POST /api/sesiones` | ADMIN | `sala_id`, `fecha`, `hora_inicio` | `201`, `Sesion` |
| `PUT /api/sesiones/{id}` | ADMIN | Representación completa | `200`, `Sesion`; `409`, `422` |
| `DELETE /api/sesiones/{id}` | ADMIN | ID | `204` si se permite; `409` con reservas |

`estado` ∈ `DISPONIBLE|RESERVADA|CANCELADA`. Validar que no exista ya otra sesión con la misma combinación `(sala_id, fecha, hora_inicio)` y que la sala esté activa. La disponibilidad real se decide en servidor.

## 5. Reservas

**Objeto de salida `Reserva`:**

```json
{
  "id": 20, "usuario_id": 11, "sesion_id": 12, "numero_jugadores": 4,
  "estado": "ACTIVA", "fecha_reserva": "2026-11-04T12:00:00+01:00",
  "sesion": { "id": 12, "sala_id": 1, "fecha": "2026-11-08", "hora_inicio": "17:00", "sala": { "nombre": "El Laboratorio Perdido" } }
}
```

| Método y URI | Permiso | Entrada | Salida |
|---|---|---|---|
| `GET /api/reservas` | Autenticado | `?estado=ACTIVA` opcional | `200`, array de `Reserva` (JUGADOR: solo propias; ADMIN: todas) |
| `POST /api/reservas` | JUGADOR | `{ "sesion_id": 12, "numero_jugadores": 4 }` | `201`, `Reserva`; `409` ocupada; `422` capacidad/fecha |
| `PUT /api/reservas/{id}` | Titular o ADMIN | `{ "estado": "CANCELADA" }` | `200`, `Reserva`; `403` ajena; `422` fuera del plazo |

La reserva debe bloquear/validar la sesión dentro de **una transacción** para impedir doble reserva concurrente. El usuario se obtiene del token, **nunca** de un `usuario_id` recibido del navegador. Máximo de jugadores según `salas.capacidad` y mínimo 2 según negocio. Cancelación únicamente hasta 24 h antes de inicio (regla RF-08).

**IMPORTANTE: cambio necesario en Sprint 2:** `reservas.sesion_id UNIQUE` impediría re-reservar tras una cancelación. Se recomienda sustituirlo por un índice parcial único sobre `sesion_id` cuando `estado = 'ACTIVA'`, y separar el estado de sesión del historial de reservas. Documentar una migración; no cambiar la tabla directamente en producción sin respaldos.

## 6. Resultados

| Método y URI | Permiso | Entrada | Salida |
|---|---|---|---|
| `GET /api/resultados` | ADMIN | Sin cuerpo | `200`, array de resultados |
| `POST /api/resultados` | ADMIN | `sesion_id`, `nombre_equipo`, `tiempo_minutos`, `superada` | `201`, resultado; `409` si ya existe |

Resultado de ejemplo:

```json
{ "id": 3, "sesion_id": 1, "nombre_equipo": "Los Científicos Locos", "tiempo_minutos": 52, "superada": true }
```


## 7. Retos, pistas, dependencias y objetos (administración)

**Los nueve recursos complementarios existen en la BD; la API los agrupa por responsabilidad.** Las rutas siguientes son un contrato propuesto para implementar junto con David. Las soluciones **nunca** se devuelven por GET ni en respuestas de POST/PUT. La opción `OBJETO` no tiene una respuesta textual: su resolución exige una acción validada por el servidor, cuya lógica debe definirse por cada tipo de acertijo.

| Método | Ruta | Rol | Cuerpo de entrada | Respuesta |
|---|---|---|---|---|
| GET | `/api/salas/{sala_id}/retos` | ADMIN | ninguno | `200` array de retos **sin hash ni solución** |
| POST | `/api/salas/{sala_id}/retos` | ADMIN | `{titulo,descripcion,tipo,orden,activo,respuesta?}` | `201` reto público |
| PUT | `/api/retos/{id}` | ADMIN | representación editable completa; `respuesta` opcional para sustituir solución | `200` reto público |
| DELETE | `/api/retos/{id}` | ADMIN | ninguno | `204`; `409` si existen partidas históricas relacionadas |
| POST | `/api/retos/{id}/pistas` | ADMIN | `{orden,contenido,penalizacion_segundos}` | `201` pista |
| POST | `/api/salas/{sala_id}/objetos` | ADMIN | `{nombre,descripcion,activo}` | `201` objeto |
| POST | `/api/retos/{id}/dependencias` | ADMIN | `{prerequisito_id}` | `201` dependencia |

**Ejemplo de creación de reto:**

```json
{"titulo":"Código de la cripta","descripcion":"Descifra los cuatro dígitos","tipo":"CODIGO","orden":1,"activo":true,"respuesta":"4729"}
```

**Respuesta `201`:**

```json
{"id":15,"sala_id":1,"titulo":"Código de la cripta","descripcion":"Descifra los cuatro dígitos","tipo":"CODIGO","orden":1,"activo":true}
```

El backend normaliza la solución, calcula HMAC con una clave secreta de servidor y guarda únicamente `respuesta_hash`. No envía `respuesta` ni `respuesta_hash` de vuelta. Para editar un reto, el cliente puede omitir `respuesta` y conservar su hash actual; si la envía, el backend lo actualiza. Las soluciones no deben aparecer en logs ni en ejemplos con datos privados. Los valores de `tipo` admitidos por el SQL son `CODIGO|TEXTO|OPCION|OBJETO`. `orden` es único por sala. Las dependencias deben conectar retos de la **misma sala** y el backend debe rechazar ciclos (`422`). El frontend permite crear y editar retos, añadir pistas, dependencias y objetos; la edición/borrado de pistas y objetos puede quedar para una iteración posterior, siempre que se declare ese límite.

## 8. Partidas, respuestas y progreso (jugador)

| Método | Ruta | Rol | Entrada | Respuesta |
|---|---|---|---|---|
| GET | `/api/partidas` | JUGADOR/ADMIN | ninguno | `200` array de partidas; jugador solo propias |
| POST | `/api/partidas` | JUGADOR | `{ "reserva_id": 24 }` | `201` partida `PENDIENTE`; `409` si ya existe |
| GET | `/api/partidas/{id}` | Titular/ADMIN | ninguno | `200` detalle y progreso, ver ejemplo |
| POST | `/api/partidas/{id}/iniciar` | Titular/ADMIN | `{}` | `200` partida `EN_CURSO` |
| POST | `/api/partidas/{id}/retos/{reto_id}/intentos` | Titular | `{ "respuesta": "4729" }` | `200` `{correcta,reto_estado,partida_estado}` |
| POST | `/api/partidas/{id}/retos/{reto_id}/pistas/{pista_id}/usar` | Titular | `{}` | `200` `{id,contenido,penalizacion_segundos}` |
| POST | `/api/partidas/{id}/retos/{reto_id}/usar-objeto` | Titular | `{ "objeto_id": 2 }` | `200` `{correcta,reto_estado,partida_estado}` |
| POST | `/api/partidas/{id}/objetos/{objeto_id}/recoger` | Titular | `{}` | `200` `{objeto_id,consumido:false}` |

**Ejemplo de GET `/api/partidas/8`** (la información se filtra según el progreso real):

```json
{
  "id": 8, "reserva_id": 24, "sala_id": 1,
  "estado": "EN_CURSO", "inicio": "2026-11-12T17:00:00+01:00", "fin": null,
  "retos": [
    {"id": 15,"orden":1,"titulo":"Código de la cripta","descripcion":"Descifra los cuatro dígitos","tipo":"CODIGO","estado":"DISPONIBLE",
      "pistas":[{"id":9,"orden":1,"penalizacion_segundos":30,"usada":false}]},
    {"id":16,"orden":2,"titulo":"Abrir puerta","descripcion":"Usa la llave","tipo":"OBJETO","estado":"BLOQUEADO","pistas":[]}
  ],
  "inventario": [{"id":2,"nombre":"Llave oxidada","consumido":false}],
  "objetos_disponibles": []
}
```

Los retos bloqueados pueden devolver un título genérico y **no** su descripción para evitar revelar puzles futuros; el ejemplo usa descripción solo como representación ilustrativa y la respuesta real debe respetar esa regla. Las pistas usadas pueden incluir `contenido` al recuperar el progreso; antes de usarse, no se devuelve el texto. El backend verifica pertenencia, reserva activa, horario permitido, estado `EN_CURSO`, disponibilidad por dependencias y límite de tiempo. Cada intento se guarda en `intentos_reto`, y un acierto cambia `progreso_retos` en la misma transacción. El servidor calcula desbloqueos y estado final de la partida y puede registrar en `resultados` el desenlace, sin duplicarlo de forma incoherente.

**Reglas de seguridad y consistencia:**

- Nunca aceptar `partida_id`, `usuario_id`, `sala_id` ni `estado` arbitrarios para asignar a un jugador desde el navegador.
- No revelar hashes, soluciones, respuestas de otros equipos, pistas aún no solicitadas ni inventario ajeno.
- No permitir iniciar una partida con una reserva cancelada o ajena, ni antes del horario autorizado; esos controles corresponden a Flask.
- Un estado `BLOQUEADO` o `COMPLETADO` no admite intentos nuevos; `409` en estado inválido, `403` en acceso ajeno.
- Pistas e inventario se consultan desde el backend. La base de datos tiene restricciones para impedir cruces de sala, pero Flask verifica todas las reglas del juego.
- Al completar una partida, persistir tiempo y resultado de forma coherente con la tabla `resultados` original, cuya referencia es la sesión.

## 9. Estados y correspondencia con PostgreSQL

| Recurso | Tabla(s) | Estados persistidos |
|---|---|---|
| Sesión | `sesiones` | DISPONIBLE, RESERVADA, CANCELADA |
| Reserva | `reservas` | ACTIVA, CANCELADA |
| Partida | `partidas` | PENDIENTE, EN_CURSO, SUPERADA, AGOTADA, ABANDONADA |
| Progreso | `progreso_retos` | BLOQUEADO, DISPONIBLE, COMPLETADO |
| Intentos | `intentos_reto` | `correcta` booleano y fecha |
| Pistas | `pistas`, `pistas_utilizadas` | Definición y uso por partida |
| Inventario | `objetos`, `inventario_partida` | Recogido o consumido |

Nota sobre la ampliación SQL: las claves foráneas compuestas ya previenen que una partida utilice retos u objetos de otra sala. El ciclo de dependencias, los tiempos y la resolución de objetos deben verificarse en el servidor.

## 10. Criterios mínimos de aceptación

1. Todas las rutas generan JSON válido y los códigos HTTP esperados.
2. Una consulta `GET` no modifica tablas; `POST` genera `201` y un recurso identificable.
3. Los datos creados siguen presentes tras reiniciar el servidor.
4. Un jugador no puede ejecutar operaciones de administrador ni consultar reservas ajenas.
5. No es posible reservar dos veces la misma sesión simultáneamente.
6. Se rechazan reservas fuera de capacidad y cancelaciones fuera de plazo.
7. Retos, pistas, objetos e intentos se guardan en las nueve tablas del modelo ampliado.
8. El backend nunca devuelve soluciones, hashes ni pistas no desbloqueadas.
9. Las partidas ajenas no pueden consultarse ni modificarse.
10. El progreso de retos y el inventario se recuperan tras recargar la web e iniciar sesión de nuevo.
11. El contrato coincide con los nombres de campos devueltos efectivamente por el backend.
12. Los mensajes de error son útiles para el cliente y no contienen información sensible.

## 11. Responsabilidades e integración

**Ferran** implementa las llamadas HTTP, presenta formularios, listas, estados y errores, y documenta los diagramas. **David** implementa los endpoints, la conexión con PostgreSQL y las reglas críticas de negocio.

**Acuerdo pendiente entre ambos:** confirmar antes de empezar la ruta base, las claves JSON, el esquema de tokens, los códigos de error y cómo se servirá el frontend. Si el frontend se abre desde otro puerto, David debe configurar CORS para ese origen explícito; no habilitar indiscriminadamente todos los orígenes con credenciales. La alternativa más simple es servir `src/` desde el mismo servidor Flask.
