# Acta de reunión – Seguimiento del Sprint 1

**Proyecto:** Sistema de creación y gestión de Escape Rooms  
**Sprint:** Sprint 1  
**Tipo de reunión:** Reunión de seguimiento (segunda reunión del sprint)  
**Fecha:** [dd/mm/2026]  
**Asistentes:** Ferran y David  
**Duración aproximada:** [30 minutos]  

---

## 1. Objetivo de la reunión

Revisar el estado de las tareas definidas en el Sprint Planning del 12/10/2026, dar por terminado el prototipo en HTML y preparar la entrega del Sprint 1.

---

## 2. Estado de las tareas

| Tarea | Responsable | Estado |
|---|---|---|
| Crear y configurar el repositorio | David | Hecha |
| Crear estructura del repositorio (`doc/`, `src/`, `lib/`) | David | Hecha |
| Crear milestone e issues | David | Hecha |
| Elaborar ERS | Ferran | [Hecha / En curso] |
| Definir requisitos RF/RNF | Ferran | [Hecha / En curso] |
| Elaborar diagrama y casos de uso | David | Hecha |
| Interfaz y funcionalidades del jugador | Ferran | Hecha |
| Funciones de administración | David | Hecha |
| Primera acta Scrum | Ferran | Hecha |
| Segunda acta Scrum | David | Hecha (este documento) |
| Informe semanal | Ferran | [Hecha / En curso] |
| Sprint Review | David | Hecha, pendiente de revisión conjunta |

---

## 3. Prototipo HTML finalizado

Se da por terminado el prototipo, que se encuentra en `src/index.html`. Es un único archivo HTML, CSS y JavaScript que se abre directamente en el navegador. Implementa:

- **Inicio de sesión** con los dos actores del sistema (jugador y administrador). La cuenta se bloquea tras 5 intentos fallidos.
- **Catálogo de salas** con temática, dificultad, duración y capacidad máxima. Se precargan tres salas (Terror, Ciencia ficción y Misterio) y cada una tiene tres sesiones (17:00, 19:00 y 21:00) con sus plazas libres.
- **Funciones del jugador:** reservar una sesión indicando el número de jugadores, con validación de capacidad y plazas libres, y consultar y cancelar sus reservas.
- **Funciones del administrador:** crear salas nuevas, que reciben sus tres sesiones automáticamente, y eliminar salas existentes.

Como se acordó en el planning, el prototipo no usa base de datos: los datos se guardan en memoria y se pierden al recargar la página. Tampoco incluye pagos, que se realizan en el establecimiento.

---

## 4. Problemas encontrados

- Al no haber base de datos, las reservas y las salas creadas no se conservan entre sesiones.
- Las credenciales de prueba están escritas en el código, por lo que el inicio de sesión no es seguro todavía.
- Hubo que coordinar el reparto del trabajo en el repositorio para evitar duplicar tareas.
- [Añadir otros problemas reales del equipo]

---

## 5. Decisiones tomadas

- Dar el prototipo por cerrado para el Sprint 1 con el alcance descrito en el punto 3.
- Mantener el prototipo como un único archivo, sin servidor ni base de datos, al ser solo un prototipo inicial.
- Dejar la persistencia de datos y la autenticación segura para sprints posteriores.
- Documentar el diagrama y las especificaciones de casos de uso (inicio de sesión y reserva de sesión) en el ERS.
- [Añadir otras decisiones acordadas]

---

## 6. Trabajo pendiente

- Revisar entre ambos la Sprint Review y las actas.
- Insertar el diagrama de casos de uso (`doc/ers/diagrama_casos_de_uso.png`) en el ERS.
- Completar y revisar el ERS y los requisitos RF/RNF.
- Preparar la demostración y la presentación del sprint.
- [Otras tareas pendientes, responsable y fecha prevista]

---

## 7. Preparación de la entrega

- Comprobar que todos los issues del milestone *Sprint 1* están cerrados.
- Verificar que el repositorio contiene `README.md`, `src/index.html` y la documentación en `doc/`.
- Ensayar la demostración: entrar como jugador y como administrador, reservar, cancelar, crear y eliminar una sala.
- **Fecha de entrega:** [dd/mm/2026]

---

## 8. Próxima reunión

- **Fecha:** [dd/mm/2026]
- **Temas:** cierre del Sprint 1 (Sprint Review) y planificación del Sprint 2.
