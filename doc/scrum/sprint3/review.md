# Sprint Review — Sprint 3 · EscapeHub

**Proyecto:** EscapeHub — Sistema de creación y gestión de Escape Rooms  
**Equipo:** Ferran y David  
**Sprint:** 3 — Modelo petición-respuesta y servicios REST  
**Fecha de review:** 11/11/26 
**Asistentes:** David, Ferran 

## 1. Objetivo y alcance

De acuerdo con la sesión 5 de Ingeniería del Software, el Sprint 3 busca identificar los recursos necesarios para el juego, documentar su comportamiento mediante diagramas UML (secuencia, actividad y estados) e implementar servicios que permitan utilizar esos recursos. La arquitectura propuesta separa HTML/JavaScript, API REST en Flask y PostgreSQL.

## 2. Incremento preparado para mostrar

### Diseño y documentación

- `doc/api_rest.md`: contrato de endpoints HTTP, esquemas de entrada/salida, códigos de respuesta y seguridad.
- `doc/uml_sprint3.md`: diagramas de interacción, actividades, estados y arquitectura.
- Modelo SQL del Sprint 2 ampliado: entidades de salas, sesiones, reservas, retos, pistas, objetos, partidas y progreso.

### Interfaz del jugador (Ferran)

- Catálogo de salas y sesiones mediante peticiones HTTP.
- Autenticación y consulta/creación/cancelación de reservas.
- Partidas: iniciar, visualizar retos disponibles, enviar respuestas, consultar pistas e inventario y recuperar progreso.

### Interfaz de administración (Ferran)

- Gestión de salas y sesiones.
- Alta/edición de retos y creación de pistas, objetos y dependencias mediante API.

### API y base de datos (David)

- [COMPLETAR CON LOS ENDPOINTS REALMENTE IMPLEMENTADOS].
- [COMPLETAR CON EL ESTADO REAL DE LAS PRUEBAS Y PERSISTENCIA].

**Estado conocido en el momento de preparar esta plantilla:** el frontend y la documentación están redactados, pero no consta aquí una prueba final contra la API Flask de David. La interfaz se ha comprobado con una API simulada; eso **no** acredita persistencia real en PostgreSQL.

## 3. Demostración propuesta (8–10 minutos)

1. **Arquitectura (1 min, Ferran).** Mostrar navegador → Flask REST → PostgreSQL y explicar por qué las soluciones se comprueban en servidor.
2. **Modelo UML y recursos (1–2 min, Ferran).** Explicar salas, reservas, retos, partidas y progreso; señalar diagrama de secuencia y de estados.
3. **Consulta de salas (1 min, David).** Ejecutar `GET /api/salas`; enseñar JSON y contenido de la tabla correspondiente.
4. **Reserva real (1–2 min, ambos).** Iniciar sesión, seleccionar sesión disponible, crear reserva y comprobar su persistencia.
5. **Juego (2 min, ambos).** Crear/iniciar partida, resolver reto, guardar intento, utilizar pista y recargar la página para verificar progreso.
6. **Caso negativo (1 min, David).** Mostrar denegación 403 de operación administrativa para jugador o conflicto 409 de doble reserva.
7. **Cierre (1 min, ambos).** Enseñar issues, commits, pendientes y decisiones.

**Adaptar la demostración a las funciones efectivamente implementadas.** No simular como reales operaciones que aún no persisten en la base de datos.

## 4. Criterios y evidencias

| Criterio | Evidencia a presentar | Resultado real |
|---|---|---|
| Recursos y endpoints documentados | `doc/api_rest.md` y ejemplos JSON | [POR VALIDAR] |
| Diagramas UML consistentes | `doc/uml_sprint3.md` | [POR VALIDAR] |
| API levantada y conectada a PostgreSQL | Captura de servidor y consulta HTTP | [POR VALIDAR] |
| GET de recursos reales | `GET /api/salas` + consulta SQL | [POR VALIDAR] |
| Operación de escritura persistente | POST/PUT y consulta SQL posterior | [POR VALIDAR] |
| Progreso de retos recuperable | Intento + recarga + consulta de partida | [POR VALIDAR] |
| Seguridad por roles | 401/403 reproducibles | [POR VALIDAR] |
| Pruebas de regresión | Resultado de tests UI/API | [POR VALIDAR] |

## 5. Problemas conocidos y riesgos a discutir

- El frontend necesita que la API de David respete los nombres de rutas, claves JSON y estados del contrato.
- En el SQL inicial la unicidad de `reservas.sesion_id` puede impedir reutilizar una sesión tras cancelar una reserva; requiere solución coherente y pruebas.
- Las contraseñas ficticias del seed no permiten autenticación real sin sustituirlas por hashes adecuados.
- El servidor debe validar autorización, concurrencia de reservas, dependencias de retos y confidencialidad de soluciones; no basta con ocultar controles en el HTML.

**Incidencias nuevas detectadas durante la review:** [RELLENAR].

## 6. Feedback del profesor o stakeholders

- **Aspectos bien valorados:** [RELLENAR CON FEEDBACK REAL].
- **Observaciones y cambios solicitados:** [RELLENAR CON FEEDBACK REAL].
- **Decisiones tras la review:** [RELLENAR].

## 7. Resultado del sprint

**Objetivo cumplido:** [SÍ / PARCIALMENTE / NO — JUSTIFICAR CON EVIDENCIAS].

**Tareas completadas (issues cerrados):** [AÑADIR ENLACES O IDENTIFICADORES].  
**Tareas trasladadas al siguiente sprint:** [AÑADIR].  
**Responsables y plazos posteriores:** [CONFIRMAR].

## 8. Lecciones y mejora continua

- El contrato de API evita incompatibilidades entre interfaz y backend solo si ambos miembros lo validan antes de la implementación.
- La persistencia del progreso es esencial para que el juego funcione al cerrar y reabrir la web.
- Conviene preparar demostraciones que incluyan tanto operaciones correctas como casos de error.

**Conclusiones realmente acordadas en la review:** [COMPLETAR TRAS CELEBRARLA].
