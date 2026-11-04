# Acta de Sprint Planning — Sprint 3

**Proyecto:** EscapeHub — Sistema de gestión de Escape Rooms  
**Equipo:** Ferran y David  
**Periodo de referencia:** 04/11/2026 – 18/11/2026  
**Fecha real de reunión:** [COMPLETAR CUANDO SE CELEBRE]  
**Asistentes:** [CONFIRMAR]  
**Duración:** [CONFIRMAR]

> **Plantilla preparada para el acta real.** La planificación de trabajo que sigue es una propuesta; no se presenta como una reunión ya celebrada.

## 1. Objetivo de la reunión

Planificar la implementación del modelo petición-respuesta utilizando una API REST entre el prototipo web y la base de datos PostgreSQL definida en el Sprint 2. Acordar recursos, endpoints, responsabilidades, entregables y criterios de aceptación.

## 2. Objetivo del sprint

Analizar y documentar los recursos necesarios para la aplicación, representarlos mediante diagramas UML (secuencia, actividad y estados) e implementar los servicios REST que permitan su utilización.

## 3. Decisiones técnicas propuestas

- Backend Python con Flask y Flask-SQLAlchemy, de acuerdo con el ejemplo alternativo de la sesión 5.
- PostgreSQL del Sprint 2 como fuente persistente de datos.
- Frontend HTML, CSS y JavaScript; comunicación por HTTP/JSON mediante `fetch`.
- Modelo de 14 tablas: los cinco recursos iniciales más retos, dependencias, pistas, objetos, partidas, progreso, intentos, pistas utilizadas e inventario.
- El servidor controla autenticación, rol, capacidad, disponibilidad y cancelaciones.
- Contrato de API documentado antes de programar: `doc/api_rest.md`.

## 4. Asignación inicial

| Tarea | Responsable | Evidencia |
|---|---|---|
| Especificar recursos/endpoints REST | Ferran | `doc/api_rest.md` |
| Elaborar diagramas UML | Ferran | `doc/uml_sprint3.md` |
| Adaptar interfaz a peticiones HTTP | Ferran | `src/index.html`, `src/js/` y `src/css/` |
| Comprobar flujos del usuario y del administrador | Ferran | pruebas manuales/documentadas |
| Configurar Flask y conexión con PostgreSQL | David | `backend/` |
| Implementar endpoints y reglas de negocio | David | `backend/routes/` |
| Crear pruebas de API y resultados | David | `backend/tests/` |
| Documentación de ejecución y Sprint Review | David | `README.md`, `doc/scrum/sprint3/review.md` |
| Informe semanal y acta 1 | Ferran | `doc/scrum/sprint3/` |
| Acta de seguimiento | David | `doc/scrum/sprint3/reunion2.md` |

## 5. Riesgos y mitigaciones

1. **Contrato inconsistente:** validar nombres de campos, rutas, tokens y errores antes de integrar.
2. **Restricción del Sprint 2:** `UNIQUE(sesion_id)` impide re-reservar una sesión cancelada; diseñar migración segura.
3. **Doble reserva concurrente:** transacciones y restricciones en el servidor.
4. **Diferentes orígenes HTTP:** servir frontend desde Flask o configurar CORS limitado al origen de desarrollo.
5. **Credenciales demo inválidas:** los hashes ficticios del seed anterior no permiten login real.
6. **Tiempo:** entregar primero recursos y UML; integrar funcionalidades incrementales después.

## 6. Criterios de aceptación

- El contrato REST está documentado, con métodos, URIs, formatos y errores.
- Los diagramas muestran interacciones y reglas de estado consistentes.
- Al menos los recursos principales se pueden consultar y modificar a través del servicio.
- Los cambios persisten en PostgreSQL.
- La API rechaza operaciones sin permisos o que violen reglas.
- Los commits e issues reflejan el trabajo realmente terminado.

## 7. Acuerdos y acciones reales

[COMPLETAR tras la reunión: decisiones finales, asistentes, incidencias y responsables confirmados.]


## Actualización del alcance por la ampliación del Sprint 2

El modelo de datos se amplió al terminar Sprint 2 para almacenar pasos y progreso del juego. La planificación del Sprint 3 debe contemplar el contrato REST y los diagramas de retos, pistas, partidas, intentos e inventario. **Esta sección es una propuesta documental, no evidencia de un acuerdo celebrado ni de funcionalidades ya probadas.**
