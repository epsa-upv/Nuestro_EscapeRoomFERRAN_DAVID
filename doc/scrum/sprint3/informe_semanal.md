# Informe semanal — Sprint 3

**Proyecto:** EscapeHub — Sistema de creación y gestión de Escape Rooms  
**Equipo:** Ferran y David  
**Periodo:** 04/11/2026 – 18/11/2026  
**Fecha de cierre:** [COMPLETAR]

> Documento de seguimiento preparado por Ferran. Actualizar los estados con evidencias de GitHub y pruebas antes de la entrega. **No marcar trabajo futuro como completado.**

## 1. Objetivo

Identificar los recursos de la aplicación, documentar sus interfaces REST y sus interacciones mediante UML e implementar servicios capaces de trabajar con PostgreSQL.

## 2. Trabajo planificado y seguimiento

| Trabajo | Responsable | Estado | Evidencia |
|---|---|---|---|
| Contrato REST de la API | Ferran | Documento redactado; pendiente de pactar con David | `doc/api_rest.md` |
| Diagramas UML de recursos | Ferran | Diagramas redactados; pendientes de revisión conjunta | `doc/uml_sprint3.md` |
| Frontend con `fetch` | Ferran | Implementación preparada; pendiente de integrar y probar con API real | `src/` |
| Pruebas de flujos UI | Ferran | Pendiente de backend operativo | Lista de pruebas de la entrega |
| Flask + conexión SQLAlchemy | David | Pendiente de confirmación | `backend/` |
| Endpoints REST y validaciones | David | Pendiente de confirmación | `backend/routes/` |
| Pruebas de API | David | Pendiente de confirmación | `backend/tests/` |
| 2 actas y Sprint Review | Ambos | Pendiente de realizar/confirmar | `doc/scrum/sprint3/` |

## 3. Actividad de Ferran

- Definición de contrato REST: rutas, recursos, cuerpos JSON, respuestas y errores.
- Elaboración de diagramas de secuencia, actividad, estados y componentes.
- Preparación de la interfaz HTTP y de los flujos de jugador/administrador.
- Preparación de acta de planificación y de este seguimiento.

**Commits/horas reales:** [COMPLETAR A PARTIR DE GITHUB].

## 4. Actividad de David

[COMPLETAR con sus cambios reales: endpoints, conexión a PostgreSQL, validaciones, pruebas y commits].

## 5. Reuniones

- Primera reunión: [FECHA, ASISTENTES Y ACUERDOS REALES].
- Segunda reunión: [FECHA, ASISTENTES Y ACUERDOS REALES].

## 6. Problemas y riesgos

- La integración frontend/backend depende de que ambos respeten el mismo contrato.
- Se ha identificado la necesidad de modificar la unicidad de las reservas activas para conservar cancelaciones sin impedir nuevas reservas.
- El seed del Sprint 2 contiene hashes de demostración no autenticables.
- Es necesario validar roles y evitar condiciones de carrera en las reservas.

**Incidencias realmente observadas:** [COMPLETAR].

## 7. Resultado y pruebas

**Endpoints probados:** [COMPLETAR].  
**Flujos completos probados:** [COMPLETAR].  
**Limitaciones al cierre:** [COMPLETAR].

## 8. Próximas acciones

- Cerrar integración y corregir errores reproducibles.
- Completar la revisión con David y actualizar diagramas si cambian endpoints.
- Preparar demo y Sprint Review conforme a los resultados reales.


## Actualización del alcance por la ampliación del Sprint 2

El modelo de datos se amplió al terminar Sprint 2 para almacenar pasos y progreso del juego. La planificación del Sprint 3 debe contemplar el contrato REST y los diagramas de retos, pistas, partidas, intentos e inventario. **Esta sección es una propuesta documental, no evidencia de un acuerdo celebrado ni de funcionalidades ya probadas.**
