-- ESCAPEHUB · Sprint 3
-- AMPLIACION DEL MODELO DE DATOS PARA RETOS Y PARTIDAS
-- PostgreSQL 14+ · Ejecutar sobre escapehub DESPUÉS de schema.sql
-- No borra ni modifica las filas de las 5 tablas del Sprint 2.
-- Ejecutar con un usuario con permisos de DDL sobre el esquema public.
-- IMPORTANTE: hacer una copia de seguridad antes de migrar una BD con datos reales.

BEGIN;

-- Permiten FKs compuestas que garantizan que reserva, sesión y sala coincidan.
CREATE UNIQUE INDEX IF NOT EXISTS ux_sesiones_id_sala
    ON sesiones (id, sala_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_reservas_id_sesion
    ON reservas (id, sesion_id);

-- 1. RETOS: diseño persistente de los pasos que configuran los administradores.
CREATE TABLE IF NOT EXISTS retos (
    id BIGSERIAL PRIMARY KEY,
    sala_id BIGINT NOT NULL REFERENCES salas(id) ON DELETE RESTRICT,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    tipo VARCHAR(15) NOT NULL
        CHECK (tipo IN ('CODIGO', 'TEXTO', 'OPCION', 'OBJETO')),
    orden INTEGER NOT NULL CHECK (orden > 0),
    -- Hash obtenido por el backend usando HMAC con secreto de servidor.
    -- NO guardar soluciones en texto claro; jamás devolver este campo en JSON.
    respuesta_hash VARCHAR(128),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_reto_respuesta CHECK (
        (tipo = 'OBJETO' AND respuesta_hash IS NULL)
        OR (tipo <> 'OBJETO' AND respuesta_hash IS NOT NULL
            AND LENGTH(TRIM(respuesta_hash)) >= 32)
    ),
    CONSTRAINT uq_reto_orden UNIQUE (sala_id, orden),
    CONSTRAINT uq_reto_id_sala UNIQUE (id, sala_id)
);

-- 2. DEPENDENCIAS: permite retos lineales o con varias ramas.
-- La API debe impedir ciclos al crear dependencias.
CREATE TABLE IF NOT EXISTS dependencias_reto (
    sala_id BIGINT NOT NULL,
    reto_id BIGINT NOT NULL,
    prerequisito_id BIGINT NOT NULL,
    PRIMARY KEY (reto_id, prerequisito_id),
    FOREIGN KEY (reto_id, sala_id)
        REFERENCES retos(id, sala_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisito_id, sala_id)
        REFERENCES retos(id, sala_id) ON DELETE CASCADE,
    CONSTRAINT chk_dependencia_distinta CHECK (reto_id <> prerequisito_id)
);

-- 3. PISTAS: instrucciones o ayudas editables de cada reto.
CREATE TABLE IF NOT EXISTS pistas (
    id BIGSERIAL PRIMARY KEY,
    reto_id BIGINT NOT NULL REFERENCES retos(id) ON DELETE CASCADE,
    orden INTEGER NOT NULL CHECK (orden > 0),
    contenido TEXT NOT NULL,
    penalizacion_segundos INTEGER NOT NULL DEFAULT 0
        CHECK (penalizacion_segundos >= 0),
    CONSTRAINT uq_pista_orden UNIQUE (reto_id, orden),
    CONSTRAINT uq_pista_id_reto UNIQUE (id, reto_id)
);

-- 4. OBJETOS: llaves y elementos de inventario pertenecientes a una sala.
CREATE TABLE IF NOT EXISTS objetos (
    id BIGSERIAL PRIMARY KEY,
    sala_id BIGINT NOT NULL REFERENCES salas(id) ON DELETE RESTRICT,
    nombre VARCHAR(120) NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_objeto_nombre UNIQUE (sala_id, nombre),
    CONSTRAINT uq_objeto_id_sala UNIQUE (id, sala_id)
);

-- 5. PARTIDAS: instancias jugadas a partir de una reserva real.
CREATE TABLE IF NOT EXISTS partidas (
    id BIGSERIAL PRIMARY KEY,
    reserva_id BIGINT NOT NULL UNIQUE,
    sesion_id BIGINT NOT NULL,
    sala_id BIGINT NOT NULL,
    estado VARCHAR(15) NOT NULL DEFAULT 'PENDIENTE'
        CHECK (estado IN ('PENDIENTE', 'EN_CURSO', 'SUPERADA', 'AGOTADA', 'ABANDONADA')),
    inicio TIMESTAMPTZ,
    fin TIMESTAMPTZ,
    CONSTRAINT fk_partida_reserva_sesion
        FOREIGN KEY (reserva_id, sesion_id)
        REFERENCES reservas(id, sesion_id) ON DELETE RESTRICT,
    CONSTRAINT fk_partida_sesion_sala
        FOREIGN KEY (sesion_id, sala_id)
        REFERENCES sesiones(id, sala_id) ON DELETE RESTRICT,
    CONSTRAINT uq_partida_id_sala UNIQUE (id, sala_id),
    CONSTRAINT chk_partida_tiempos CHECK (
        (estado = 'PENDIENTE' AND inicio IS NULL AND fin IS NULL)
        OR (estado = 'EN_CURSO' AND inicio IS NOT NULL AND fin IS NULL)
        OR (estado IN ('SUPERADA', 'AGOTADA', 'ABANDONADA')
            AND inicio IS NOT NULL AND fin IS NOT NULL AND fin >= inicio)
    )
);

-- 6. PROGRESO: cada reto completado o disponible dentro de una partida.
CREATE TABLE IF NOT EXISTS progreso_retos (
    partida_id BIGINT NOT NULL,
    sala_id BIGINT NOT NULL,
    reto_id BIGINT NOT NULL,
    estado VARCHAR(12) NOT NULL DEFAULT 'BLOQUEADO'
        CHECK (estado IN ('BLOQUEADO', 'DISPONIBLE', 'COMPLETADO')),
    fecha_completado TIMESTAMPTZ,
    PRIMARY KEY (partida_id, reto_id),
    CONSTRAINT fk_progreso_partida
        FOREIGN KEY (partida_id, sala_id)
        REFERENCES partidas(id, sala_id) ON DELETE CASCADE,
    CONSTRAINT fk_progreso_reto
        FOREIGN KEY (reto_id, sala_id)
        REFERENCES retos(id, sala_id) ON DELETE RESTRICT,
    CONSTRAINT uq_progreso_partida_sala_reto
        UNIQUE (partida_id, sala_id, reto_id),
    CONSTRAINT chk_progreso_completado CHECK (
        (estado = 'COMPLETADO' AND fecha_completado IS NOT NULL)
        OR (estado <> 'COMPLETADO' AND fecha_completado IS NULL)
    )
);

-- 7. INTENTOS: histórico de respuestas; no guarda las soluciones ni respuestas crudas.
CREATE TABLE IF NOT EXISTS intentos_reto (
    id BIGSERIAL PRIMARY KEY,
    partida_id BIGINT NOT NULL,
    sala_id BIGINT NOT NULL,
    reto_id BIGINT NOT NULL,
    correcta BOOLEAN NOT NULL,
    fecha_intento TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (partida_id, sala_id, reto_id)
        REFERENCES progreso_retos(partida_id, sala_id, reto_id) ON DELETE CASCADE
);

-- 8. PISTAS USADAS: cada pista se utiliza una sola vez por partida.
CREATE TABLE IF NOT EXISTS pistas_utilizadas (
    partida_id BIGINT NOT NULL,
    sala_id BIGINT NOT NULL,
    reto_id BIGINT NOT NULL,
    pista_id BIGINT NOT NULL,
    fecha_uso TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (partida_id, pista_id),
    FOREIGN KEY (partida_id, sala_id, reto_id)
        REFERENCES progreso_retos(partida_id, sala_id, reto_id) ON DELETE CASCADE,
    FOREIGN KEY (pista_id, reto_id)
        REFERENCES pistas(id, reto_id) ON DELETE RESTRICT
);

-- 9. INVENTARIO: objetos recogidos por una partida; FK impide cruzar salas.
CREATE TABLE IF NOT EXISTS inventario_partida (
    partida_id BIGINT NOT NULL,
    sala_id BIGINT NOT NULL,
    objeto_id BIGINT NOT NULL,
    fecha_obtencion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    consumido BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (partida_id, objeto_id),
    FOREIGN KEY (partida_id, sala_id)
        REFERENCES partidas(id, sala_id) ON DELETE CASCADE,
    FOREIGN KEY (objeto_id, sala_id)
        REFERENCES objetos(id, sala_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_retos_sala ON retos(sala_id, orden);
CREATE INDEX IF NOT EXISTS idx_pistas_reto ON pistas(reto_id, orden);
CREATE INDEX IF NOT EXISTS idx_partidas_estado ON partidas(estado);
CREATE INDEX IF NOT EXISTS idx_intentos_partida_reto ON intentos_reto(partida_id, reto_id);
CREATE INDEX IF NOT EXISTS idx_pistas_usadas_partida ON pistas_utilizadas(partida_id);

-- Vista pública de progreso: datos de estado, sin hashes ni contenidos sensibles.
CREATE OR REPLACE VIEW vista_progreso_partida AS
SELECT p.id AS partida_id,
       p.reserva_id,
       p.sala_id,
       p.estado AS estado_partida,
       COUNT(pr.reto_id) FILTER (WHERE r.activo) AS retos_totales,
       COUNT(pr.reto_id) FILTER (WHERE r.activo AND pr.estado = 'COMPLETADO') AS retos_completados,
       COUNT(pr.reto_id) FILTER (WHERE r.activo AND pr.estado = 'DISPONIBLE') AS retos_disponibles
FROM partidas p
LEFT JOIN progreso_retos pr ON pr.partida_id = p.id
LEFT JOIN retos r ON r.id = pr.reto_id
GROUP BY p.id, p.reserva_id, p.sala_id, p.estado;

COMMIT;
