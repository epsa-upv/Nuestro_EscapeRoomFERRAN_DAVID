# ERS – Especificación de Requisitos Software

**Proyecto:** Sistema de creación y gestión de Escape Rooms  
**Versión:** 1.0  
**Sprint:** Sprint 1  
**Equipo:** Ferran y David  

---

## 1. Introducción

### 1.1 Propósito

El objetivo de este documento es definir los requisitos iniciales del sistema de creación y gestión de Escape Rooms desarrollado durante el proyecto de la asignatura Ingeniería del Software.

Esta especificación servirá como base para el desarrollo de las diferentes versiones del software durante los siguientes sprints.

Durante el Sprint 1 se realizará un primer análisis de los requisitos del sistema y se desarrollará un prototipo inicial que permita comprobar el funcionamiento básico de la aplicación.

### 1.2 Alcance

El sistema estará orientado a la gestión de un negocio de Escape Rooms presenciales.

Los jugadores podrán consultar las salas disponibles, visualizar información sobre ellas, consultar sesiones y realizar reservas.

Los administradores podrán gestionar las salas y, progresivamente durante los siguientes sprints, gestionar sesiones, resultados y otra información relacionada con el funcionamiento del negocio.

### 1.3 Tipo de Escape Rooms

Se ha decidido desarrollar un sistema para Escape Rooms temáticos presenciales.

Las salas podrán tener diferentes temáticas:

- Terror.
- Misterio.
- Ciencia ficción.
- Aventura.

Cada sala tendrá diferentes características:

- Nombre.
- Temática.
- Dificultad.
- Duración.
- Capacidad máxima.

Las sesiones tendrán una duración aproximada de 60 minutos y estarán destinadas a grupos de jugadores.

### 1.4 Definiciones

- **RF:** Requisito funcional.
- **RNF:** Requisito no funcional.
- **Jugador:** usuario que consulta y reserva Escape Rooms.
- **Administrador:** usuario encargado de gestionar el sistema.
- **Sala:** Escape Room disponible en el sistema.
- **Sesión:** fecha y hora en la que una sala puede ser reservada.
- **Reserva:** asignación de un grupo de jugadores a una sesión.
- **ERS:** Especificación de Requisitos Software.

---

## 2. Descripción general

### 2.1 Perspectiva del producto

El sistema será una aplicación accesible mediante navegador web.

Durante el Sprint 1 se desarrollará un prototipo utilizando HTML, CSS y JavaScript.

El objetivo de esta primera versión será validar las principales interacciones del sistema antes de incorporar funcionalidades más complejas como persistencia de datos o una base de datos.

### 2.2 Actores

El sistema tendrá inicialmente dos actores principales.

#### Jugador

El jugador podrá:

- Iniciar sesión.
- Consultar Escape Rooms.
- Consultar sesiones.
- Realizar reservas.
- Cancelar reservas.
- Consultar sus reservas.

#### Administrador

El administrador podrá:

- Iniciar sesión.
- Gestionar salas.
- Gestionar sesiones.
- Consultar reservas.
- Registrar resultados.
- Exportar información.

### 2.3 Suposiciones y restricciones

- El sistema será utilizado mediante navegador web.
- Las reservas estarán asociadas a una sesión.
- Cada sala tendrá una capacidad máxima.
- Una misma sesión no podrá ser reservada simultáneamente por dos grupos.
- Los pagos se realizarán en el establecimiento y no formarán parte del sistema.
- Durante el Sprint 1 los datos se almacenarán únicamente en memoria.
- La persistencia de datos se implementará en posteriores sprints.

---

## 3. Requisitos funcionales

| ID | Requisito |
|---|---|
| RF-01 | El sistema permitirá a un visitante registrarse indicando nombre, correo electrónico y contraseña. |
| RF-02 | El sistema permitirá iniciar sesión mediante usuario y contraseña y mostrará un mensaje de error cuando las credenciales sean incorrectas. |
| RF-03 | El sistema bloqueará temporalmente una cuenta después de cinco intentos fallidos consecutivos de inicio de sesión. |
| RF-04 | El jugador podrá consultar el listado de Escape Rooms mostrando nombre, temática, dificultad, duración y capacidad. |
| RF-05 | El jugador podrá consultar las sesiones disponibles de una sala. |
| RF-06 | El jugador podrá realizar una reserva seleccionando sala, sesión y número de jugadores. |
| RF-07 | El sistema comprobará la disponibilidad de una sesión antes de realizar una reserva. |
| RF-08 | El jugador podrá cancelar una reserva propia dentro del plazo permitido. |
| RF-09 | El jugador podrá consultar sus reservas. |
| RF-10 | El administrador podrá crear, modificar y eliminar Escape Rooms. |
| RF-11 | El administrador podrá crear y gestionar sesiones indicando sala, fecha y hora. |
| RF-12 | El administrador podrá registrar el resultado de una sesión indicando equipo, tiempo empleado y si se ha superado. |
| RF-13 | El administrador podrá exportar las reservas en formato CSV seleccionando un rango de fechas. |

---

## 4. Requisitos no funcionales

| ID | Requisito |
|---|---|
| RNF-01 | La aplicación deberá funcionar correctamente en navegadores web modernos. |
| RNF-02 | Las contraseñas deberán almacenarse mediante mecanismos seguros de hash y sal en la versión final. |
| RNF-03 | Las operaciones habituales de consulta y reserva deberán responder en menos de 2 segundos en condiciones normales. |
| RNF-04 | La interfaz deberá adaptarse correctamente a ordenadores y dispositivos móviles. |
| RNF-05 | Las funciones de administración solo podrán ser utilizadas por usuarios con rol de administrador. |

---

## 5. Casos de uso

### Jugador

- Registrarse.
- Iniciar sesión.
- Consultar salas.
- Consultar sesiones.
- Reservar sesión.
- Cancelar reserva.
- Consultar reservas.

### Administrador

- Iniciar sesión.
- Gestionar salas.
- Gestionar sesiones.
- Registrar resultados.
- Exportar reservas.

El caso de uso Reservar sesión incluye la comprobación previa de disponibilidad.

---

## 6. Especificación de casos de uso

### CU-01 – Reservar sesión

**Actor principal:** Jugador.

**Objetivo:** permitir al jugador reservar una sesión de un Escape Room.

#### Precondiciones

- El jugador ha iniciado sesión.
- Existe al menos una sala.
- Existe al menos una sesión disponible.

#### Flujo principal

1. El jugador consulta las salas.
2. Selecciona una sala.
3. El sistema muestra las sesiones disponibles.
4. El jugador selecciona una sesión.
5. Indica el número de jugadores.
6. El sistema comprueba la capacidad de la sala.
7. El sistema comprueba la disponibilidad de la sesión.
8. El sistema registra la reserva.
9. El sistema muestra un mensaje de confirmación.

#### Flujo alternativo: capacidad superada

1. El sistema detecta que se supera la capacidad.
2. La reserva se rechaza.
3. El sistema muestra la capacidad máxima.
4. El jugador puede modificar el número de participantes.

#### Flujo alternativo: sesión ocupada

1. El sistema detecta que la sesión está ocupada.
2. La reserva se rechaza.
3. El sistema informa al jugador.
4. El jugador deberá seleccionar otra sesión.

#### Postcondición

La reserva queda registrada y asociada a la sesión seleccionada.

---

### CU-02 – Iniciar sesión

**Actor principal:** Jugador / Administrador.

**Objetivo:** autenticar a un usuario y permitir el acceso a las funciones correspondientes a su rol.

#### Precondiciones

- El usuario dispone de credenciales.
- El sistema está disponible.

#### Flujo principal

1. El sistema solicita el usuario.
2. El sistema solicita la contraseña.
3. El usuario introduce las credenciales.
4. El sistema valida las credenciales.
5. El sistema identifica el rol.
6. El sistema muestra el panel correspondiente.

#### Flujo alternativo: credenciales incorrectas

1. El sistema detecta credenciales incorrectas.
2. El acceso es rechazado.
3. El sistema muestra un mensaje de error.

El bloqueo después de cinco intentos fallidos se desarrollará en una versión posterior.

---

## 7. Prototipo del Sprint 1

El prototipo inicial se encuentra en:

`src/index.html`

Durante el Sprint 1 se implementarán las siguientes funcionalidades:

- Inicio de sesión básico.
- Validación básica de credenciales.
- Visualización de Escape Rooms.
- Información básica de las salas.
- Selección de sesión.
- Número de jugadores.
- Comprobación de capacidad.
- Comprobación de sesiones ocupadas.
- Creación de reservas.
- Visualización de reservas.
- Cancelación de reservas.
- Panel básico de administración.
- Creación y eliminación de salas.
- Interfaz adaptable a diferentes tamaños de pantalla.

Los datos utilizados durante el prototipo se almacenan en memoria mediante JavaScript.

---

## 8. Limitaciones actuales

En el Sprint 1 todavía no se implementarán:

- Registro real de usuarios.
- Base de datos.
- Persistencia de salas y reservas.
- Bloqueo de cuentas tras cinco intentos.
- Gestión completa de sesiones.
- Restricción temporal de cancelaciones.
- Gestión de resultados.
- Exportación CSV.
- Gestión avanzada de usuarios.

Estas funcionalidades serán desarrolladas progresivamente en posteriores sprints.

---

## 9. Conclusiones

El Sprint 1 permite establecer la base del sistema.

Se han identificado los actores principales, los requisitos funcionales y no funcionales y los principales casos de uso.

Además, el prototipo inicial permitirá comprobar la interacción básica entre el jugador y el sistema antes de continuar con el desarrollo de nuevas funcionalidades.
