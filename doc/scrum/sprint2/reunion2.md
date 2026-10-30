# Acta de reunión – Segunda reunión Scrum

**Proyecto:** Sistema de creación y gestión de Escape Rooms  
**Sprint:** Sprint 2  
**Tipo de reunión:** Reunión de seguimiento  
**Fecha:** 30/10/2026  
**Asistentes:** Ferran y David  
**Duración aproximada:** 30 minutos

\---

## 1\. Objetivo de la reunión

El objetivo de la reunión es revisar el avance del Sprint 2 antes de su finalización. En ella se comprueba el estado de las tareas acordadas en el Sprint Planning y se detectan los problemas surgidos durante el desarrollo.

También se revisa que el modelo de datos, el esquema SQL y las tablas creadas en PostgreSQL sean coherentes entre sí, y se organiza el trabajo que queda pendiente hasta el Sprint Review.

\---

## 2\. Revisión del Sprint Planning

Se revisan los acuerdos tomados en la primera reunión:

* Se mantiene PostgreSQL como sistema gestor de bases de datos.
* El modelo de datos se ha desarrollado a partir de la ERS del Sprint 1.
* Las tablas utilizan identificadores numéricos, claves primarias, claves foráneas y restricciones `NOT NULL`, `UNIQUE` y `CHECK`.
* El trabajo se gestiona mediante issues asociados al milestone `Sprint 2`.

No se han producido cambios en el objetivo del sprint.

\---

## 3\. Estado de las tareas

|Tarea|Responsable|Estado|
|-|-|-|
|Analizar el modelo de datos|Ferran|Completada|
|Documentar entidades y relaciones|Ferran|Completada|
|Elaborar diagrama de clases|Ferran|Completada|
|Crear esquema SQL|Ferran|Completada|
|Elaborar Sprint Planning|Ferran|Completada|
|Elaborar informe semanal|Ferran|En curso|
|Preparar PostgreSQL|David|Completada|
|Comprobar el esquema SQL|David|Completada|
|Crear datos de prueba|David|Completada|
|Crear consultas de prueba|David|Completada|
|Segunda reunión Scrum|David|En curso|
|Sprint Review|David|Pendiente|

\---

## 4\. Trabajo realizado

### Ferran

* Ha analizado la ERS y ha identificado las entidades principales del sistema: Usuario, Sala, Sesión, Reserva y Resultado.
* Ha documentado los atributos, las relaciones y las cardinalidades en `doc/modelo\_datos.md`.
* Ha elaborado el diagrama de clases.
* Ha implementado el esquema SQL en `src/db/schema.sql`.

### David

* Ha instalado y configurado PostgreSQL y pgAdmin 4.
* Ha creado la base de datos del proyecto y ha comprobado que el esquema SQL se ejecuta sin errores.
* Ha creado los datos de prueba en `src/db/seed.sql`.
* Ha creado las consultas de prueba en `src/db/queries.sql`.
* Ha comprobado que las restricciones de las tablas rechazan los datos incorrectos.

\---

## 5\. Pruebas realizadas

Se comprueba el funcionamiento de la base de datos mediante:

* Creación de todas las tablas a partir de `schema.sql`.
* Inserción de los datos de prueba de `seed.sql`.
* Consultas de selección, consultas con `JOIN` entre varias tablas y consultas con agrupaciones (`GROUP BY`, `COUNT`, `AVG`).
* Inserción de datos incorrectos para comprobar las restricciones:

  * Valores duplicados en campos `UNIQUE`.
  * Valores fuera de rango en campos con `CHECK`.
  * Claves foráneas que hacen referencia a registros inexistentes.
  * Campos obligatorios vacíos (`NOT NULL`).

En todos los casos la base de datos rechaza los datos incorrectos, por lo que se mantiene la integridad referencial.

\---

## 6\. Problemas detectados

Durante el desarrollo se han detectado los siguientes problemas:

* **Caracteres especiales en la consola de Windows:** los acentos no se mostraban correctamente al ejecutar los scripts con `psql`. Se soluciona ejecutando `chcp 65001` o utilizando pgAdmin.
* **Orden de ejecución de los scripts:** si se ejecuta `seed.sql` antes que `schema.sql`, se producen errores. Se acuerda ejecutarlos siempre en el orden `schema.sql`, `seed.sql`, `queries.sql`.
* **Orden de inserción de los datos:** las tablas con claves foráneas deben rellenarse después de las tablas a las que hacen referencia. Se ordenan los `INSERT` de `seed.sql` de forma adecuada.
* **Consulta de estadísticas:** una consulta de prueba contaba como no superadas las reservas que todavía no se habían jugado. Se corrige para tener en cuenta solo los resultados registrados.

\---

## 7\. Revisión de riesgos

Se revisan los riesgos identificados en el Sprint Planning:

|Riesgo|Situación|
|-|-|
|Diseñar un modelo que no sea coherente con la ERS|Controlado: el modelo se ha revisado con la ERS|
|Crear relaciones incorrectas entre las entidades|Controlado: las relaciones se han comprobado con consultas `JOIN`|
|Definir cardinalidades incorrectas|Controlado: revisadas en el diagrama de clases|
|Crear tablas diferentes al modelo documentado|Controlado: el diagrama y `schema.sql` están sincronizados|
|No mantener correctamente la integridad referencial|Controlado: comprobado con las pruebas de restricciones|
|Introducir datos incompatibles con las restricciones|Controlado: los datos de prueba se cargan sin errores|
|Problemas de configuración de PostgreSQL|Resuelto|

\---

## 8\. Acuerdos

Se acuerda:

1. Mantener sincronizados `doc/modelo\_datos.md`, el diagrama de clases y `src/db/schema.sql`.
2. Ejecutar los scripts siempre en el orden `schema.sql`, `seed.sql` y `queries.sql`.
3. No subir al repositorio contraseñas ni datos de conexión de PostgreSQL.
4. Subir al repositorio todos los archivos pendientes antes del Sprint Review.
5. Cerrar los issues del milestone `Sprint 2` cuyo trabajo esté terminado y subido.
6. Realizar en el Sprint Review una demostración de la creación de las tablas, la carga de datos y las consultas de prueba.

\---

## 9\. Próximos pasos

|Tarea|Responsable|
|-|-|
|Finalizar el informe semanal|Ferran|
|Subir el esquema de la base de datos y ejemplos al repositorio|David|
|Subir esta acta al repositorio|David|
|Preparar y realizar el Sprint Review|David|
|Cerrar los issues completados del milestone `Sprint 2`|Ferran y David|



