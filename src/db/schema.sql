-- =====================================================
-- ESCAPEHUB
-- Sprint 2 - Modelo de datos
-- PostgreSQL
-- =====================================================


-- =========================
-- TABLA USUARIOS
-- =========================

CREATE TABLE usuarios (

    id BIGSERIAL PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    rol VARCHAR(10) NOT NULL DEFAULT 'JUGADOR',

    intentos_fallidos INTEGER NOT NULL DEFAULT 0,

    bloqueado BOOLEAN NOT NULL DEFAULT FALSE,

    fecha_creacion TIMESTAMP
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT chk_usuario_rol
        CHECK (
            rol IN ('JUGADOR', 'ADMIN')
        ),

    CONSTRAINT chk_intentos_fallidos
        CHECK (
            intentos_fallidos >= 0
        )

);



-- =========================
-- TABLA SALAS
-- =========================

CREATE TABLE salas (

    id BIGSERIAL PRIMARY KEY,

    nombre VARCHAR(120)
        NOT NULL
        UNIQUE,

    tematica VARCHAR(80)
        NOT NULL,

    dificultad VARCHAR(10)
        NOT NULL,

    duracion_minutos INTEGER
        NOT NULL
        DEFAULT 60,

    capacidad INTEGER
        NOT NULL,

    activa BOOLEAN
        NOT NULL
        DEFAULT TRUE,


    CONSTRAINT chk_sala_dificultad
        CHECK (
            dificultad IN (
                'BAJA',
                'MEDIA',
                'ALTA'
            )
        ),

    CONSTRAINT chk_sala_duracion
        CHECK (
            duracion_minutos > 0
        ),

    CONSTRAINT chk_sala_capacidad
        CHECK (
            capacidad >= 2
        )

);



-- =========================
-- TABLA SESIONES
-- =========================

CREATE TABLE sesiones (

    id BIGSERIAL PRIMARY KEY,

    sala_id BIGINT
        NOT NULL,

    fecha DATE
        NOT NULL,

    hora_inicio TIME
        NOT NULL,

    estado VARCHAR(12)
        NOT NULL
        DEFAULT 'DISPONIBLE',


    CONSTRAINT fk_sesion_sala

        FOREIGN KEY (sala_id)

        REFERENCES salas(id)

        ON UPDATE CASCADE

        ON DELETE RESTRICT,


    CONSTRAINT uq_sesion_fecha_hora

        UNIQUE (
            sala_id,
            fecha,
            hora_inicio
        ),


    CONSTRAINT chk_sesion_estado

        CHECK (
            estado IN (
                'DISPONIBLE',
                'RESERVADA',
                'CANCELADA'
            )
        )

);



-- =========================
-- TABLA RESERVAS
-- =========================

CREATE TABLE reservas (

    id BIGSERIAL PRIMARY KEY,

    usuario_id BIGINT
        NOT NULL,

    sesion_id BIGINT
        NOT NULL
        UNIQUE,

    numero_jugadores INTEGER
        NOT NULL,

    estado VARCHAR(10)
        NOT NULL
        DEFAULT 'ACTIVA',

    fecha_reserva TIMESTAMP
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT fk_reserva_usuario

        FOREIGN KEY (usuario_id)

        REFERENCES usuarios(id)

        ON UPDATE CASCADE

        ON DELETE RESTRICT,


    CONSTRAINT fk_reserva_sesion

        FOREIGN KEY (sesion_id)

        REFERENCES sesiones(id)

        ON UPDATE CASCADE

        ON DELETE RESTRICT,


    CONSTRAINT chk_reserva_jugadores

        CHECK (
            numero_jugadores > 0
        ),


    CONSTRAINT chk_reserva_estado

        CHECK (
            estado IN (
                'ACTIVA',
                'CANCELADA'
            )
        )

);



-- =========================
-- TABLA RESULTADOS
-- =========================

CREATE TABLE resultados (

    id BIGSERIAL PRIMARY KEY,

    sesion_id BIGINT
        NOT NULL
        UNIQUE,

    nombre_equipo VARCHAR(120)
        NOT NULL,

    tiempo_minutos INTEGER,

    superada BOOLEAN
        NOT NULL,


    CONSTRAINT fk_resultado_sesion

        FOREIGN KEY (sesion_id)

        REFERENCES sesiones(id)

        ON UPDATE CASCADE

        ON DELETE CASCADE,


    CONSTRAINT chk_resultado_tiempo

        CHECK (
            tiempo_minutos IS NULL
            OR tiempo_minutos >= 0
        )

);



-- =========================
-- ÍNDICES
-- =========================

CREATE INDEX idx_sesiones_fecha
ON sesiones(fecha);


CREATE INDEX idx_reservas_usuario
ON reservas(usuario_id);


CREATE INDEX idx_reservas_fecha
ON reservas(fecha_reserva);
