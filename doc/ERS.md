# ERS – Especificación de Requisitos Software

**Proyecto:** Sistema de creación y gestión de Escape Rooms  
**Versión:** 1.0  
**Sprint:** Sprint 1  
**Equipo:** Ferran y David  

---

## 1. Introducción

### 1.1 Propósito

El objetivo de este documento es definir los requisitos iniciales del sistema de creación y gestión de Escape Rooms desarrollado durante el proyecto de la asignatura Ingeniería del Software.

La especificación servirá como base para el desarrollo de las distintas versiones del software a lo largo de los siguientes sprints.

Durante el Sprint 1 se realizará un primer análisis de los requisitos y se desarrollará un prototipo inicial que permita validar la estructura y funcionamiento básico del sistema.

### 1.2 Alcance

El sistema permitirá gestionar un negocio de Escape Rooms presenciales.

Los jugadores podrán consultar las salas disponibles, visualizar información sobre ellas, consultar sesiones, realizar reservas y gestionar sus propias reservas.

Por otra parte, los administradores podrán gestionar las salas y, en futuras versiones, gestionar las sesiones, disponibilidad, resultados y demás información relacionada con la actividad del negocio.

### 1.3 Tipo de Escape Room

Se ha decidido desarrollar un sistema orientado a Escape Rooms temáticos presenciales.

Las salas podrán pertenecer a diferentes temáticas, como:

- Terror.
- Misterio.
- Ciencia ficción.
- Aventura.

Cada sala tendrá unas características determinadas, entre ellas:

- Nombre.
- Temática.
- Dificultad.
- Duración.
- Capacidad máxima de jugadores.

Las sesiones tendrán una duración aproximada de 60 minutos y estarán destinadas a grupos de jugadores.

### 1.4 Definiciones y abreviaturas

- **RF:** Requisito funcional.
- **RNF:** Requisito no funcional.
- **Jugador:** usuario que consulta y reserva sesiones de Escape Room.
- **Administrador:** usuario encargado de gestionar el sistema.
- **Sala:** Escape Room disponible para los jugadores.
- **Sesión:** franja de fecha y hora en la que una sala puede ser reservada.
- **Reserva:** asignación de un jugador o grupo a una sesión determinada.
- **ERS:** Especificación de Requisitos Software.

---

# 2. Descripción general

## 2.1 Perspectiva del producto

El sistema será una aplicación accesible mediante navegador web.

En esta primera versión se desarrollará un prototipo funcional utilizando HTML, CSS y JavaScript.

El prototipo permitirá validar la interacción básica entre los usuarios y el sistema antes de desarrollar funcionalidades más avanzadas y mecanismos de persistencia de datos.

## 2.2 Actores

El sistema tendrá inicialmente dos actores principales:

### Jugador

Usuario que utiliza el sistema para consultar Escape Rooms y realizar reservas.

Entre sus principales acciones se encuentran:

- Iniciar sesión.
- Consultar salas.
- Consultar sesiones.
- Realizar reservas.
- Cancelar reservas.
- Consultar el historial de reservas.

### Administrador

Usuario encargado de gestionar el negocio y la información disponible en el sistema.

Entre sus funciones se encuentran:

- Iniciar sesión.
- Gestionar salas.
- Gestionar sesiones.
- Consultar reservas.
- Registrar resultados.
- Exportar información.

## 2.3 Suposiciones y restricciones

- El sistema será utilizado desde un navegador web.
- Las reservas estarán asociadas a sesiones concretas.
- Cada sala tendrá una capacidad máxima.
- Una sesión no podrá reservarse simultáneamente por dos grupos distintos.
- Los pagos se realizarán físicamente en el establecimiento y quedan fuera del alcance del sistema.
- Durante el Sprint 1 los datos del prototipo se almacenarán únicamente en memoria y se perderán al recargar la aplicación.
- La persistencia mediante base de datos se desarrollará en un sprint posterior.

---

# 3. Requisitos funcionales

| ID | Requisito |
|---|---|
| **RF-01** | El sistema permitirá a un visitante registrarse indicando nombre, correo electrónico y contraseña. |
| **RF-02** | El sistema permitirá iniciar sesión mediante usuario y contraseña y mostrará un mensaje de error cuando las credenciales sean incorrectas. |
| **RF-03** | El sistema bloqueará temporalmente la cuenta después de cinco intentos consecutivos de inicio de sesión fallidos. |
| **RF-04** | El jugador podrá consultar el listado de Escape Rooms disponibles, mostrando como mínimo nombre, temática, dificultad, duración y capacidad. |
| **RF-05** | El jugador podrá consultar las sesiones disponibles para cada sala. |
| **RF-06** | El jugador podrá realizar una reserva seleccionando una sala, una sesión y el número de jugadores. |
| **RF-07** | El sistema comprobará la disponibilidad de la sesión y evitará reservar una sesión que ya se encuentre ocupada. |
| **RF-08** | El jugador podrá cancelar una reserva propia siempre que se encuentre dentro del plazo de cancelación permitido. |
| **RF-09** | El jugador podrá consultar sus reservas realizadas. |
| **RF-10** | El administrador podrá crear, modificar y eliminar Escape Rooms indicando sus principales características. |
| **RF-11** | El administrador podrá crear y gestionar sesiones indicando sala, fecha y hora. |
| **RF-12** | El administrador podrá registrar el resultado de una sesión, incluyendo el equipo participante, el tiempo empleado y si el Escape Room ha sido superado. |
| **RF-13** | El administrador podrá exportar la información de las reservas en formato CSV utilizando un rango de fechas. |

---

# 4. Requisitos no funcionales

| ID | Requisito |
|---|---|
| **RNF-01** | La aplicación deberá funcionar correctamente en navegadores web modernos, incluyendo Google Chrome, Mozilla Firefox y Safari. |
| **RNF-02** | En la versión final, las contraseñas de los usuarios deberán almacenarse utilizando mecanismos seguros de hash y sal. |
| **RNF-03** | Las operaciones habituales de consulta y reserva deberán ofrecer un tiempo de respuesta inferior a 2 segundos en condiciones normales. |
| **RNF-04** | La interfaz deberá adaptarse correctamente a dispositivos de escritorio y dispositivos móviles. |
| **RNF-05** | Las funciones de administración únicamente podrán ser utilizadas por usuarios con rol de administrador. |

---

# 5. Casos de uso

Los principales casos de uso identificados son:

## Jugador

- Registrarse.
- Iniciar sesión.
- Consultar salas.
- Consultar sesiones disponibles.
- Reservar una sesión.
- Cancelar una reserva.
- Consultar historial de reservas.

## Administrador

- Iniciar sesión.
- Gestionar salas.
- Gestionar sesiones.
- Registrar resultados.
- Exportar reservas.

El caso de uso **Reservar sesión** incluye la comprobación de disponibilidad de la sesión antes de confirmar la reserva.

---

# 6. Especificación de casos de uso

## CU-01 – Reservar sesión

**Actor principal:** Jugador  

**Objetivo:** permitir al jugador reservar una sesión de un Escape Room.

### Precondiciones

- El jugador ha accedido al sistema.
- Existe al menos una sala disponible.
- Existe al menos una sesión disponible para la sala seleccionada.

### Flujo principal

1. El jugador consulta las salas disponibles.
2. El jugador selecciona una sala.
3. El sistema muestra las sesiones disponibles.
4. El jugador selecciona una sesión.
5. El jugador indica el número de participantes.
6. El sistema comprueba la capacidad máxima de la sala.
7. El sistema comprueba que la sesión continúa disponible.
8. El sistema registra la reserva.
9. El sistema muestra un mensaje de confirmación.

### Flujos alternativos

**A1 – Capacidad superada**

Si el número de jugadores supera la capacidad de la sala:

1. El sistema rechaza la reserva.
2. El sistema informa de la capacidad máxima permitida.
3. El jugador puede modificar el número de participantes.

**A2 – Sesión ocupada**

Si la sesión ya ha sido reservada:

1. El sistema rechaza la reserva.
2. El sistema informa de que la sesión no está disponible.
3. El jugador deberá seleccionar otra sesión.

### Postcondición

La reserva queda registrada en el sistema y asociada a la sesión seleccionada.

---

## CU-02 – Iniciar sesión

**Actor principal:** Jugador / Administrador  

**Objetivo:** autenticar a un usuario y permitirle acceder a las funciones correspondientes a su rol.

### Precondiciones

- El usuario dispone de unas credenciales válidas.
- El sistema está disponible.

### Flujo principal

1. El sistema solicita el nombre de usuario.
2. El sistema solicita la contraseña.
3. El usuario introduce sus credenciales.
4. El sistema comprueba las credenciales.
5. Si son correctas, el sistema identifica el rol del usuario.
6. El sistema muestra el panel correspondiente.

### Flujo alternativo

**A1 – Credenciales incorrectas**

1. El sistema detecta que las credenciales no son válidas.
2. El acceso es rechazado.
3. El sistema muestra un mensaje de error.

En una versión posterior se implementará el bloqueo de la cuenta después de cinco intentos fallidos consecutivos, correspondiente al requisito RF-03.

### Postcondición

El usuario accede al sistema con los permisos asociados a su rol.

---

# 7. Prototipo del Sprint 1

Durante el Sprint 1 se ha desarrollado un primer prototipo funcional en:

`src/index.html`

El objetivo de esta primera versión no es implementar la totalidad de los requisitos definidos en la ERS, sino validar el diseño general del sistema y sus principales interacciones.

El prototipo incluye:

- Inicio de sesión como jugador.
- Inicio de sesión como administrador.
- Validación básica de credenciales.
- Visualización de Escape Rooms.
- Información básica de cada sala.
- Selección de una sesión.
- Selección del número de jugadores.
- Comprobación de la capacidad máxima.
- Comprobación básica de sesiones ya reservadas.
- Creación de reservas.
- Consulta de reservas realizadas.
- Cancelación de reservas.
- Panel básico de administración.
- Creación de salas.
- Eliminación de salas.
- Interfaz adaptable a diferentes tamaños de pantalla.

Los datos utilizados durante esta versión se almacenan en memoria mediante JavaScript, por lo que se pierden al actualizar la página.

---

# 8. Limitaciones actuales

La versión desarrollada durante el Sprint 1 constituye únicamente un primer prototipo.

Todavía no se han implementado:

- Registro real de usuarios.
- Base de datos.
- Persistencia de salas y reservas.
- Bloqueo tras cinco intentos fallidos.
- Gestión completa de sesiones.
- Restricción temporal de cancelaciones.
- Gestión de resultados.
- Exportación de reservas a CSV.
- Gestión avanzada de usuarios.

Estas funcionalidades se desarrollarán progresivamente durante los siguientes sprints.

---

# 9. Conclusiones del Sprint 1

Durante el Sprint 1 se ha establecido la base funcional del proyecto.

Se ha definido el alcance inicial del sistema, identificado sus actores principales y especificado un conjunto inicial de requisitos funcionales y no funcionales.

Además, se ha desarrollado un prototipo que permite validar las principales interacciones del jugador y una primera versión de las funciones de administración.

Esta primera versión servirá como base para continuar el desarrollo del producto durante los siguientes sprints.
