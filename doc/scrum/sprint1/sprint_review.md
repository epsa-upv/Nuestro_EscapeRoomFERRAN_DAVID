# Sprint Review – Sprint 1

**Proyecto:** Sistema de creación y gestión de Escape Rooms  
**Sprint:** Sprint 1  
**Fecha:** 21/10/2026  
**Equipo:** Ferran y David  

---

## 1. Objetivo del Sprint

El objetivo del Sprint 1 ha sido realizar el análisis inicial del sistema de gestión de Escape Rooms y desarrollar un primer prototipo funcional que permita validar las principales interacciones del sistema.

Durante este sprint se ha trabajado en:

- Definición del alcance del sistema.
- Identificación de actores.
- Definición de requisitos funcionales.
- Definición de requisitos no funcionales.
- Elaboración de casos de uso.
- Creación del diagrama de casos de uso.
- Desarrollo del primer prototipo funcional.
- Organización del trabajo mediante GitHub y Scrum.

---

## 2. Entregables del Sprint 1

Durante este sprint se han generado los siguientes entregables:

- Especificación de Requisitos Software v1.0.
- 13 requisitos funcionales.
- 5 requisitos no funcionales.
- 2 casos de uso detallados.
- Diagrama de casos de uso.
- Prototipo funcional inicial.
- Dos actas de reunión Scrum.
- Informe semanal.
- Repositorio GitHub organizado mediante issues y milestone.
- Presentación del Sprint Review.

---

## 3. Funcionalidades implementadas

El prototipo desarrollado durante el Sprint 1 permite realizar las siguientes acciones.

### Jugador

- Iniciar sesión con credenciales de demostración.
- Mostrar un mensaje de error si las credenciales son incorrectas.
- Consultar las salas disponibles.
- Visualizar información básica de cada sala.
- Seleccionar una sala.
- Seleccionar una sesión.
- Indicar el número de jugadores.
- Comprobar la capacidad máxima de la sala.
- Realizar una reserva.
- Evitar reservar una sesión ya ocupada.
- Consultar las reservas realizadas.
- Cancelar una reserva.
- Cerrar sesión.

### Administrador

- Iniciar sesión como administrador.
- Acceder al panel de administración.
- Consultar las salas registradas.
- Crear nuevas salas.
- Eliminar salas.
- Cerrar sesión.

---

## 4. Demostración realizada

Durante el Sprint Review se realizará la siguiente demostración:

1. Intento de inicio de sesión con credenciales incorrectas.
2. Inicio de sesión como jugador.
3. Consulta de las salas disponibles.
4. Selección de una sala y una sesión.
5. Realización de una reserva.
6. Visualización de la reserva.
7. Cancelación de la reserva.
8. Cierre de sesión.
9. Inicio de sesión como administrador.
10. Creación de una nueva sala.
11. Eliminación de una sala.

El objetivo de la demostración es comprobar que las principales interacciones definidas para el prototipo inicial funcionan correctamente.

---

## 5. Estado de los requisitos

La Especificación de Requisitos Software contiene requisitos que se desarrollarán progresivamente durante los siguientes sprints.

### Implementados total o parcialmente en el prototipo

- RF-02 – Inicio de sesión y validación básica de credenciales.
- RF-04 – Consulta de Escape Rooms.
- RF-06 – Reserva de una sesión.
- RF-07 – Comprobación básica de disponibilidad.
- RF-08 – Cancelación de reservas, de forma parcial.
- RF-09 – Consulta de reservas.
- RF-10 – Gestión de salas, de forma parcial.
- RNF-04 – Interfaz adaptable a distintos tamaños de pantalla.
- RNF-05 – Separación básica entre jugador y administrador.

### Pendientes de futuras versiones

- RF-01 – Registro real de usuarios.
- RF-03 – Bloqueo de cuenta tras cinco intentos fallidos.
- RF-05 – Gestión completa de sesiones disponibles.
- RF-08 – Restricción de cancelación según el plazo establecido.
- RF-10 – Edición completa de salas.
- RF-11 – Gestión completa de sesiones.
- RF-12 – Registro de resultados.
- RF-13 – Exportación de reservas a CSV.
- RNF-02 – Almacenamiento seguro de contraseñas.
- Persistencia de datos mediante base de datos.

---

## 6. Problemas y limitaciones detectadas

La principal limitación de la versión actual es la ausencia de persistencia de datos.

Actualmente los datos se almacenan únicamente en memoria mediante JavaScript, por lo que:

- Las reservas desaparecen al actualizar la página.
- Las salas creadas por el administrador desaparecen al actualizar la página.
- No existe todavía una base de datos.
- No existe un sistema real de registro de usuarios.
- Las credenciales utilizadas son únicamente datos de demostración.

También existen requisitos definidos en la ERS que todavía no han sido implementados, lo cual es coherente con el carácter inicial del prototipo desarrollado en el Sprint 1.

---

## 7. Resultado del Sprint

Se considera que el objetivo principal del Sprint 1 ha sido alcanzado.

Al finalizar el sprint se dispone de:

- Una primera Especificación de Requisitos Software.
- Una definición inicial de los actores y funcionalidades del sistema.
- Un conjunto de casos de uso.
- Un diagrama de casos de uso.
- Un primer prototipo funcional.
- Una estructura de trabajo organizada en GitHub.
- Documentación Scrum correspondiente al sprint.

---

## 8. Próximos pasos – Sprint 2

Como continuación del proyecto, se propone trabajar durante el Sprint 2 en:

- Incorporación de persistencia de datos.
- Diseño e implementación de una base de datos.
- Registro de usuarios.
- Mejora del sistema de autenticación.
- Gestión completa de sesiones.
- Registro de resultados.
- Exportación de reservas a CSV.

La planificación definitiva del Sprint 2 se realizará después del Sprint Review y de recibir el feedback correspondiente.

---

## 9. Feedback del Sprint Review

Este apartado se completará después de la presentación y de recibir las observaciones del profesor o cliente.

**Feedback recibido:**

- Pendiente.

**Cambios propuestos a partir del feedback:**

- Pendiente.
