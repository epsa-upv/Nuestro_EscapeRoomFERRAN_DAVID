# Acta de reunión – Sprint Review

**Proyecto:** Sistema de creación y gestión de Escape Rooms  
**Sprint:** Sprint 2  
**Tipo de reunión:** Sprint Review  
**Fecha:** 30/10/2026  
**Asistentes:** Ferran y David  
**Duración aproximada:** 30 minutos

\---

## 1\. Objetivo de la reunión

El objetivo de la reunión es revisar el trabajo realizado durante el Sprint 2 y comprobar si se ha cumplido el objetivo del sprint.

En la reunión se presenta el incremento obtenido, se comprueban los criterios de finalización acordados en el Sprint Planning y se identifican las mejoras que pasarán al siguiente sprint.

\---

## 2\. Objetivo del Sprint 2

El objetivo del Sprint 2 era desarrollar el modelo de datos del sistema de gestión de Escape Rooms, implementarlo mediante SQL en PostgreSQL y comprobar su funcionamiento con datos y consultas de prueba.

\---

## 3\. Trabajo completado

|Tarea|Responsable|Estado|
|-|-|-|
|Analizar el modelo de datos|Ferran|Completada|
|Documentar entidades y relaciones|Ferran|Completada|
|Elaborar diagrama de clases|Ferran|Completada|
|Crear esquema SQL|Ferran|Completada|
|Elaborar Sprint Planning|Ferran|Completada|
|Elaborar informe semanal|Ferran|Completada|
|Preparar PostgreSQL|David|Completada|
|Comprobar el esquema SQL|David|Completada|
|Crear datos de prueba|David|Completada|
|Crear consultas de prueba|David|Completada|
|Segunda reunión Scrum|David|Completada|
|Sprint Review|David|Completada|

Se han completado todas las tareas planificadas para el Sprint 2.

\---

## 4\. Incremento obtenido

Al finalizar el sprint, el repositorio contiene los siguientes archivos:

```text
doc/
    modelo\_datos.md

    scrum/
        sprint2/
            reunion1.md
            reunion2.md
            informe\_semanal.md
            review.md
            img/

src/
    db/
        schema.sql
        seed.sql
        queries.sql
```

El modelo de datos está formado por cinco tablas:

|Tabla|Descripción|
|-|-|
|`usuarios`|Jugadores y administradores del sistema, con control de intentos fallidos y bloqueo|
|`salas`|Escape rooms disponibles, con temática, dificultad, duración y capacidad|
|`sesiones`|Fechas y horas en las que se puede jugar cada sala|
|`reservas`|Reserva de una sesión por parte de un usuario|
|`resultados`|Resultado de cada sesión jugada: equipo, tiempo y si se superó la sala|

Relaciones principales:

* Una sala tiene muchas sesiones (1:N).
* Un usuario puede hacer muchas reservas (1:N).
* Cada sesión puede tener como máximo una reserva (1:1).
* Cada sesión puede tener como máximo un resultado (1:1).

\---

## 5\. Demostración

Durante la reunión se realiza una demostración en PostgreSQL mediante pgAdmin 4:

1. Creación de la base de datos y ejecución de `schema.sql`.
2. Carga de los datos de prueba con `seed.sql`.
3. Ejecución de las consultas de `queries.sql`.
4. Ejecución de las pruebas de restricciones.

Tras ejecutar `schema.sql`, las cinco tablas del modelo aparecen creadas en la base de datos `escapehub`:

!\[Tablas creadas en pgAdmin](img/tablas\_pgadmin.png)

\---

## 6\. Resultados de las pruebas

### Datos de prueba

Los datos de `seed.sql` se cargan sin errores:

|Tabla|Registros|
|-|-|
|`usuarios`|10 (2 administradores y 8 jugadores)|
|`salas`|5 (4 activas y 1 inactiva)|
|`sesiones`|14|
|`reservas`|10|
|`resultados`|6|

La consulta C1 confirma el número de registros de cada tabla:

!\[Resultado de la consulta C1](img/c1\_recuento.png)

### Consultas de prueba

Se ejecutan 11 consultas que devuelven los resultados esperados:

* Número de registros de cada tabla.
* Salas activas ordenadas por dificultad.
* Sesiones disponibles para reservar.
* Reservas activas con usuario, sala, fecha y hora.
* Reservas de un usuario concreto.
* Ranking de los equipos más rápidos.
* Estadísticas por sala: partidas jugadas, porcentaje superado y tiempo medio.
* Usuarios con más de una reserva.
* Jugadores que nunca han reservado.
* Usuarios bloqueados o con intentos fallidos.
* Reservas con más jugadores que la capacidad de la sala (0 resultados, como se esperaba).

**Consulta C4 – Reservas activas con usuario, sala, fecha y hora**

Se obtienen las 9 reservas activas. La reserva cancelada no aparece, como se esperaba.

!\[Resultado de la consulta C4](img/c4\_reservas.png)

**Consulta C7 – Estadísticas por sala**

Se obtienen, para cada sala, las partidas jugadas, el porcentaje de partidas superadas y el tiempo medio. Las salas sin partidas o sin ninguna partida superada muestran `null` en los valores que no se pueden calcular.

!\[Resultado de la consulta C7](img/c7\_estadisticas.png)

### Pruebas de restricciones

Se realizan 12 pruebas insertando datos incorrectos. En todos los casos la base de datos los rechaza:

|Prueba|Restricción comprobada|Resultado|
|-|-|-|
|Email duplicado|`UNIQUE`|Rechazado|
|Rol no permitido|`CHECK`|Rechazado|
|Dificultad no permitida|`CHECK`|Rechazado|
|Capacidad menor que 2|`CHECK`|Rechazado|
|Sesión duplicada en la misma sala, fecha y hora|`UNIQUE`|Rechazado|
|Sesión de una sala inexistente|Clave foránea|Rechazado|
|Segunda reserva de una misma sesión|`UNIQUE`|Rechazado|
|Reserva con 0 jugadores|`CHECK`|Rechazado|
|Reserva de un usuario inexistente|Clave foránea|Rechazado|
|Resultado con tiempo negativo|`CHECK`|Rechazado|
|Usuario sin email|`NOT NULL`|Rechazado|
|Borrar una sala que tiene sesiones|`ON DELETE RESTRICT`|Rechazado|

!\[Resultado de las pruebas de restricciones en pgAdmin](img/pruebas\_restricciones.png)

\---

## 7\. Comprobación de los criterios de finalización

|Criterio|Cumplido|
|-|-|
|El modelo de datos está documentado|Sí|
|El diagrama de clases está finalizado|Sí|
|Las sentencias SQL están implementadas|Sí|
|Las tablas se pueden crear correctamente|Sí|
|Se han realizado pruebas básicas sobre la base de datos|Sí|

\---

## 8\. Problemas y mejoras detectadas

Al comprobar el esquema SQL se detectan los siguientes aspectos a mejorar:

* **Reejecución del esquema:** si `schema.sql` se ejecuta dos veces, se produce un error porque las tablas ya existen. Se propone añadir `DROP TABLE IF EXISTS ... CASCADE` al inicio del script.
* **Resultados sin tiempo:** se puede registrar un resultado con `superada = TRUE` y sin `tiempo\_minutos`. Se propone añadir una restricción `CHECK` que obligue a indicar el tiempo cuando la sala se ha superado.
* **Capacidad de la sala:** la base de datos no impide reservar con más jugadores que la capacidad de la sala, porque esta comprobación afecta a dos tablas. De momento se controla con una consulta de comprobación y se validará en la aplicación.
* **Coherencia de estados:** el estado de la sesión (`RESERVADA`) y el de la reserva (`ACTIVA` o `CANCELADA`) se gestionan por separado, por lo que la aplicación deberá mantenerlos sincronizados.

\---

## 9\. Acuerdos

Se acuerda:

1. Dar por cumplido el objetivo del Sprint 2.
2. Cerrar todos los issues del milestone `Sprint 2`.
3. Añadir al Product Backlog las mejoras detectadas en el esquema SQL.
4. Mantener `schema.sql`, `seed.sql` y `queries.sql` como base para el siguiente sprint.

\---

## 10\. Próximos pasos

Para el siguiente sprint se proponen las siguientes tareas:

|Tarea|Responsable|
|-|-|
|Aplicar las mejoras detectadas en `schema.sql`|Ferran|
|Actualizar `seed.sql` y `queries.sql` si cambia el esquema|David|
|Conectar el panel de administración con la base de datos|Por asignar|
|Mostrar en la interfaz del jugador las salas y sesiones disponibles|Por asignar|
|Validar en la aplicación la capacidad de las salas al reservar|Por asignar|

\---

## 

