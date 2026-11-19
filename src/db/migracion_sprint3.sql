-- =====================================================
-- ESCAPEHUB
-- Sprint 3 - Migración PROPUESTA (decisiones A, B y C)
-- PostgreSQL 14+
--
-- Ejecutar sobre escapehub DESPUÉS de:
--   schema.sql + seed.sql (Sprint 2) + ampliacion_sprint3.sql
-- Conectado como postgres (o como propietario de las tablas).
-- Se puede ejecutar varias veces sin errores.
--
-- ESTADO: pendiente de aprobación por Ferran.
-- El backend funciona también SIN esta migración: en ese caso
-- no se puede re-reservar una sesión cancelada y los retos
-- OPCION / OBJETO responden 422 ("pendiente de migración").
-- =====================================================

BEGIN;


-- =========================
-- A. RE-RESERVAR UNA SESIÓN CANCELADA
-- Antes: reservas.sesion_id era UNIQUE (también para canceladas).
-- Ahora: solo puede haber UNA reserva ACTIVA por sesión,
-- y se conserva el historial de reservas canceladas.
-- =========================

ALTER TABLE reservas
    DROP CONSTRAINT IF EXISTS reservas_sesion_id_key;

CREATE UNIQUE INDEX IF NOT EXISTS uq_reserva_activa_por_sesion
    ON reservas (sesion_id)
    WHERE estado = 'ACTIVA';



-- =========================
-- B. ALTERNATIVAS DE LOS RETOS DE TIPO OPCION
-- El jugador ve las opciones y responde con el texto de una.
-- La opción correcta sigue guardándose solo como respuesta_hash.
-- =========================

CREATE TABLE IF NOT EXISTS opciones_reto (

    id BIGSERIAL PRIMARY KEY,

    reto_id BIGINT
        NOT NULL,

    orden INTEGER
        NOT NULL,

    texto VARCHAR(200)
        NOT NULL,


    CONSTRAINT fk_opcion_reto
        FOREIGN KEY (reto_id)
        REFERENCES retos(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_opcion_orden
        UNIQUE (reto_id, orden),

    CONSTRAINT uq_opcion_texto
        UNIQUE (reto_id, texto),

    CONSTRAINT chk_opcion_orden
        CHECK (orden > 0)

);



-- =========================
-- C. RETOS DE TIPO OBJETO Y OBJETOS DESBLOQUEABLES
-- retos.objeto_requerido_id : objeto que resuelve un reto OBJETO
-- objetos.reto_desbloqueo_id: reto que hay que completar para poder
--                             recoger el objeto (NULL = desde el inicio)
-- Las FK compuestas (..., sala_id) impiden mezclar salas.
-- =========================

ALTER TABLE retos
    ADD COLUMN IF NOT EXISTS objeto_requerido_id BIGINT;

ALTER TABLE objetos
    ADD COLUMN IF NOT EXISTS reto_desbloqueo_id BIGINT;

ALTER TABLE retos
    DROP CONSTRAINT IF EXISTS fk_reto_objeto_requerido;
ALTER TABLE retos
    ADD CONSTRAINT fk_reto_objeto_requerido
        FOREIGN KEY (objeto_requerido_id, sala_id)
        REFERENCES objetos(id, sala_id)
        ON DELETE RESTRICT;

ALTER TABLE retos
    DROP CONSTRAINT IF EXISTS chk_reto_objeto_requerido;
ALTER TABLE retos
    ADD CONSTRAINT chk_reto_objeto_requerido
        CHECK ((tipo = 'OBJETO') = (objeto_requerido_id IS NOT NULL));

ALTER TABLE objetos
    DROP CONSTRAINT IF EXISTS fk_objeto_reto_desbloqueo;
ALTER TABLE objetos
    ADD CONSTRAINT fk_objeto_reto_desbloqueo
        FOREIGN KEY (reto_desbloqueo_id, sala_id)
        REFERENCES retos(id, sala_id)
        ON DELETE RESTRICT;



-- =========================
-- PROPIETARIO
-- Si existe escapeuser (usuario.sql), todas las tablas
-- del juego y la vista pasan a ser suyas.
-- =========================

DO $$
DECLARE
    t TEXT;
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'escapeuser') THEN
        FOREACH t IN ARRAY ARRAY[
            'retos', 'dependencias_reto', 'pistas', 'objetos', 'partidas',
            'progreso_retos', 'intentos_reto', 'pistas_utilizadas',
            'inventario_partida', 'opciones_reto'
        ] LOOP
            EXECUTE format('ALTER TABLE %I OWNER TO escapeuser', t);
        END LOOP;
        ALTER VIEW vista_progreso_partida OWNER TO escapeuser;
    END IF;
END $$;

COMMIT;
