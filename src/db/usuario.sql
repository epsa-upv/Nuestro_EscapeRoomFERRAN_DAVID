-- =====================================================
-- ESCAPEHUB
-- Sprint 2 - Usuario (rol) de la base de datos
-- PostgreSQL
--
-- Ejecutar conectado como postgres (administrador)
-- sobre la base de datos escapehub.
-- Las tablas del proyecto pasan a pertenecer a este usuario,
-- que es el que utilizará la aplicación.
-- =====================================================


-- =========================
-- CREAR EL USUARIO
-- =========================

CREATE USER escapeuser
    WITH ENCRYPTED PASSWORD 'escape2026';

ALTER USER escapeuser CREATEDB;



-- =========================
-- PERMISOS SOBRE LA BASE DE DATOS
-- =========================

GRANT ALL PRIVILEGES ON DATABASE escapehub TO escapeuser;

GRANT ALL ON SCHEMA public TO escapeuser;



-- =========================
-- PROPIETARIO DE LAS TABLAS
-- (si ya se habían creado con postgres)
-- =========================

ALTER TABLE IF EXISTS usuarios   OWNER TO escapeuser;
ALTER TABLE IF EXISTS salas      OWNER TO escapeuser;
ALTER TABLE IF EXISTS sesiones   OWNER TO escapeuser;
ALTER TABLE IF EXISTS reservas   OWNER TO escapeuser;
ALTER TABLE IF EXISTS resultados OWNER TO escapeuser;
