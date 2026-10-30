# Informe semanal – Sprint 2

**Proyecto:** Sistema de creación y gestión de Escape Rooms  
**Equipo:** Ferran y David  
**Sprint:** Sprint 2  
**Periodo:** 21/10/2026 – 04/11/2026  
**Fecha límite:** 03/11/2026  

---

## 1. Objetivo del Sprint

El objetivo del Sprint 2 es desarrollar el modelo de datos del sistema de gestión de Escape Rooms y crear las tablas necesarias para almacenar la información de la aplicación.

Durante el sprint se trabaja en:

- Identificación de entidades.
- Definición de atributos.
- Definición de relaciones.
- Definición de cardinalidades.
- Elaboración del diagrama de clases.
- Implementación del esquema SQL.
- Configuración y utilización de PostgreSQL.
- Realización de pruebas sobre la base de datos.

---

## 2. Trabajo realizado

| Tarea | Responsable | Estado |
|---|---|---|
| Análisis del modelo de datos | Ferran | Completada |
| Documentación del modelo | Ferran | Completada |
| Diagrama de clases | Ferran | Completada |
| Esquema SQL | Ferran | Completada |
| Sprint Planning | Ferran | Completada |
| Informe semanal | Ferran | En preparación |
| Preparación PostgreSQL | David | Pendiente de confirmar |
| Datos de prueba | David | Pendiente de confirmar |
| Consultas SQL de prueba | David | Pendiente de confirmar |
| Segunda reunión | David | Pendiente de confirmar |
| Sprint Review | David | Pendiente de confirmar |

---

## 3. Actividad de Ferran

Durante el Sprint 2, Ferran se ha encargado principalmente del análisis y diseño del modelo de datos.

El trabajo realizado incluye:

- Revisión de los requisitos definidos en la ERS.
- Identificación de las entidades necesarias.
- Definición de los atributos de cada entidad.
- Definición de claves primarias.
- Definición de relaciones entre entidades.
- Definición de cardinalidades.
- Definición de restricciones de integridad.
- Elaboración del diagrama de clases.
- Elaboración del documento del modelo de datos.
- Implementación de las sentencias SQL de creación de tablas.
- Definición de claves foráneas.
- Definición de restricciones `UNIQUE`.
- Definición de restricciones `CHECK`.
- Elaboración del Sprint Planning.
- Elaboración del informe semanal.

---

## 4. Actividad de David

Este apartado deberá actualizarse con el trabajo realizado realmente por David.

El trabajo previsto incluye:

- Preparación del sistema PostgreSQL.
- Ejecución del esquema SQL.
- Comprobación de las tablas creadas.
- Creación de datos de prueba.
- Realización de consultas SQL.
- Elaboración de la segunda reunión Scrum.
- Preparación del Sprint Review.

---

## 5. Modelo obtenido

El modelo está formado actualmente por cinco entidades principales:

- Usuario.
- Sala.
- Sesión.
- Reserva.
- Resultado.

Las principales relaciones son:

- Un usuario puede realizar múltiples reservas.
- Una sala puede disponer de múltiples sesiones.
- Una sesión puede tener una reserva.
- Una sesión puede generar un resultado.

---

## 6. Implementación SQL

El esquema de base de datos se encuentra en:

`src/db/schema.sql`

El script contiene:

- Claves primarias.
- Claves foráneas.
- Restricciones de unicidad.
- Restricciones sobre los valores.
- Integridad referencial.
- Índices básicos.

---

## 7. Problemas y dificultades

Este apartado deberá completarse con los problemas que realmente se hayan encontrado durante las pruebas.

Entre los posibles aspectos a comprobar se encuentran:

- Configuración de PostgreSQL.
- Ejecución del script desde una base de datos vacía.
- Funcionamiento de claves foráneas.
- Restricciones de unicidad.
- Coherencia entre el diagrama y las tablas.

---

## 8. Resultado del Sprint

El resultado definitivo se completará cuando se hayan terminado las pruebas de PostgreSQL y las tareas asignadas a ambos miembros del equipo.

---

## 9. Próximos pasos

Los próximos pasos se decidirán después del Sprint Review y del feedback recibido para el Sprint 3.
