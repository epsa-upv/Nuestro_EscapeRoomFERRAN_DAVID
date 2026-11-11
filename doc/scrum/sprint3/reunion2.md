# Acta de reunión 2 — Seguimiento del Sprint 3

**Proyecto:** EscapeHub — Sistema de creación y gestión de Escape Rooms  
**Sprint:** 3 — Servicios REST y recursos del juego  
**Equipo:** Ferran y David  
**Fecha:** [INDICAR FECHA REAL]  
**Hora y duración:** [INDICAR]  
**Asistentes efectivos:** [CONFIRMAR]  
**Tipo de reunión:** Seguimiento y coordinación del sprint

> **Documento redactado para utilizarlo en la reunión.** No constituye prueba de que la reunión haya ocurrido. Antes de entregarlo, confirmar los asistentes, la fecha, los acuerdos y las tareas realizadas.

## 1. Orden del día

1. Revisar el objetivo oficial: identificar recursos, describirlos mediante UML e implementar servicios REST.
2. Revisar el modelo PostgreSQL ampliado al final del Sprint 2 (14 tablas).
3. Verificar la correspondencia entre `doc/api_rest.md`, el frontend y las rutas de Flask.
4. Identificar incidencias de integración y definir prioridades para la demo.
5. Actualizar el tablero GitHub y asignar acciones de cierre.

## 2. Estado de los entregables que se revisarán

| Entregable | Responsable | Estado de preparación conocido | Comprobación pendiente |
|---|---|---|---|
| Contrato REST (`doc/api_rest.md`) | Ferran | Redactado como propuesta | Aprobación conjunta de rutas y JSON |
| UML (`doc/uml_sprint3.md`) | Ferran | Diagramas preparados | Revisión frente a implementación |
| Interfaz (`src/`) | Ferran | Programada para consumir la API | Prueba con Flask real |
| Backend Flask (`backend/`) | David | No verificado en este documento | Arranque, conexión y endpoints |
| Pruebas de backend | David | No verificadas | Casos de permisos, reservas y partidas |
| Scrum y demostración | Ambos | Documentación en preparación | Incorporar evidencias reales |

## 3. Puntos técnicos a resolver

**Contrato y configuración.** Comprobar que el servidor utiliza el prefijo `/api`, el formato de errores `{ "error": { "codigo": "...", "mensaje": "..." } }` y la autenticación `Bearer`, tal como figuran en el contrato; confirmar el origen permitido para CORS o servir web y API desde un mismo origen.

**Reservas canceladas.** Revisar el `UNIQUE(sesion_id)` del modelo inicial: si continúa vigente, una reserva cancelada puede impedir reservar la misma sesión de nuevo. Definir la migración con copia de seguridad y pruebas.

**Datos de prueba.** Confirmar que los usuarios tienen contraseñas de prueba verificables mediante hashes reales; los valores ficticios del `seed.sql` anterior no permiten probar un login efectivo.

**Reglas de juego.** El backend debe comprobar propiedad de la partida, desbloqueo por dependencias, tiempo permitido, corrección de respuestas, persistencia de intentos y privacidad de soluciones y pistas.

## 4. Plan de verificación propuesto

| Prueba | Resultado esperado | Resultado observado |
|---|---|---|
| `GET /api/salas` | Responde 200 con un array JSON de PostgreSQL | [PENDIENTE] |
| `POST /api/auth/login` | Devuelve token y usuario sin hash | [PENDIENTE] |
| `POST /api/reservas` | Crea reserva válida; rechaza doble reserva | [PENDIENTE] |
| `POST /api/partidas` y `/iniciar` | Crea e inicia partida del titular | [PENDIENTE] |
| Envío de respuesta | Registra intento y desbloquea reto al acertar | [PENDIENTE] |
| Recarga y recuperación | Se conserva el progreso en PostgreSQL | [PENDIENTE] |
| Acceso ajeno/admin | Responde 403/401 cuando corresponde | [PENDIENTE] |

## 5. Acciones propuestas para cierre

| Acción | Responsable propuesto | Evidencia esperada |
|---|---|---|
| Revisar contrato y resolver diferencias de campos | Ferran + David | `doc/api_rest.md` aceptado |
| Probar toda la navegación contra la API real | Ferran | Capturas, pasos y resultados |
| Corregir reglas de negocio y persistencia | David | Commits y pruebas de servidor |
| Revisar UML final frente a flujos implementados | Ferran | Diagramas actualizados |
| Registrar resultados de pruebas y preparar demo | Ambos | README, acta de review y evidencias |

## 6. Acuerdos realmente adoptados

- [RELLENAR DESPUÉS DE LA REUNIÓN: decisión, responsable y fecha de cumplimiento].
- [RELLENAR DESPUÉS DE LA REUNIÓN].

**Próxima revisión / fecha acordada:** [CONFIRMAR].
