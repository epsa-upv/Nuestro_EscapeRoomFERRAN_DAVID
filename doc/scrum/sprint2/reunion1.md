# Acta de reunión – Sprint Planning

**Proyecto:** Sistema de creación y gestión de Escape Rooms  
**Sprint:** Sprint 2  
**Tipo de reunión:** Sprint Planning  
**Fecha:** 30/10/2026  
**Asistentes:** Ferran y David  
**Duración aproximada:** 35 minutos  

---

## 1. Objetivo de la reunión

El objetivo de la reunión es planificar el trabajo correspondiente al Sprint 2 y establecer las tareas necesarias para desarrollar el modelo de datos del sistema.

Durante este sprint se pretende transformar los requisitos definidos durante el Sprint 1 en un modelo de datos estructurado e implementar posteriormente las tablas correspondientes mediante SQL.

---

## 2. Objetivo del Sprint 2

El objetivo principal del Sprint 2 será desarrollar el modelo de datos del sistema de gestión de Escape Rooms.

Como resultado se espera obtener:

- Identificación de las entidades principales.
- Definición de atributos.
- Definición de relaciones.
- Definición de cardinalidades.
- Diagrama de clases.
- Esquema SQL.
- Creación de las tablas en PostgreSQL.
- Datos y consultas de prueba.
- Documentación Scrum.

---

## 3. Modelo inicial

A partir de la ERS desarrollada durante el Sprint 1 se identifican inicialmente las siguientes entidades:

- Usuario.
- Sala.
- Sesión.
- Reserva.
- Resultado.

El modelo podrá modificarse durante el desarrollo si se detectan nuevas necesidades.

---

## 4. Decisiones técnicas

Se acuerda utilizar PostgreSQL como sistema gestor de bases de datos.

Las tablas utilizarán:

- Identificadores numéricos.
- Claves primarias.
- Claves foráneas.
- Restricciones `NOT NULL`.
- Restricciones `UNIQUE`.
- Restricciones `CHECK`.
- Integridad referencial.

También se prepararán datos y consultas de prueba para comprobar el funcionamiento de las tablas.

---

## 5. Reparto de tareas

| Tarea | Responsable | Estado |
|---|---|---|
| Analizar el modelo de datos | Ferran | Pendiente |
| Documentar entidades y relaciones | Ferran | Pendiente |
| Elaborar diagrama de clases | Ferran | Pendiente |
| Crear esquema SQL | Ferran | Pendiente |
| Elaborar Sprint Planning | Ferran | En curso |
| Elaborar informe semanal | Ferran | Pendiente |
| Preparar PostgreSQL | David | Pendiente |
| Comprobar el esquema SQL | David | Pendiente |
| Crear datos de prueba | David | Pendiente |
| Crear consultas de prueba | David | Pendiente |
| Segunda reunión Scrum | David | Pendiente |
| Sprint Review | David | Pendiente |

---

## 6. Organización de archivos

Se acuerda utilizar:

```text
doc/
    modelo_datos.md

    scrum/
        sprint2/
            reunion1.md
            reunion2.md
            informe_semanal.md
            review.md

src/
    db/
        schema.sql
        seed.sql
        queries.sql
```

---

## 7. Riesgos identificados

Se identifican los siguientes riesgos:

- Diseñar un modelo que no sea coherente con la ERS.
- Crear relaciones incorrectas entre las entidades.
- Definir cardinalidades incorrectas.
- Crear tablas diferentes al modelo documentado.
- No mantener correctamente la integridad referencial.
- Introducir datos incompatibles con las restricciones.
- Problemas de configuración de PostgreSQL.

---

## 8. Acuerdos

Se acuerda:

1. Mantener el modelo de datos coherente con la ERS.
2. Utilizar PostgreSQL como DBMS.
3. Mantener el diagrama y el esquema SQL sincronizados.
4. Utilizar claves foráneas para representar las relaciones.
5. Comprobar el funcionamiento del esquema mediante datos de prueba.
6. Gestionar el trabajo mediante issues asociados al milestone `Sprint 2`.
7. No cerrar un issue hasta que el trabajo correspondiente esté terminado y subido al repositorio.
8. Realizar una segunda reunión antes de finalizar el Sprint.

---

## 9. Criterios de finalización

Se considerará completada la parte técnica principal del Sprint 2 cuando:

- El modelo de datos esté documentado.
- El diagrama de clases esté finalizado.
- Las sentencias SQL estén implementadas.
- Las tablas puedan crearse correctamente.
- Se hayan realizado pruebas básicas sobre la base de datos.
