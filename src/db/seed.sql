-- =====================================================
-- ESCAPEHUB
-- Sprint 2 - Datos de prueba (seed)
-- PostgreSQL
-- Ejecutar después de schema.sql
-- =====================================================


-- Vacía las tablas y reinicia los identificadores
-- (permite ejecutar este script varias veces)
TRUNCATE resultados, reservas, sesiones, salas, usuarios
    RESTART IDENTITY CASCADE;



-- =========================
-- USUARIOS
-- 2 administradores y 8 jugadores
-- (password_hash contiene hashes ficticios de ejemplo)
-- =========================

INSERT INTO usuarios (nombre, email, password_hash, rol, intentos_fallidos, bloqueado, fecha_creacion) VALUES
('Ferran Admin',     'ferran@escapehub.es',     '$2b$10$adminHashEjemplo000000000000000000000000000000001', 'ADMIN',   0, FALSE, '2026-10-01 10:00'),
('David Admin',      'david@escapehub.es',      '$2b$10$adminHashEjemplo000000000000000000000000000000002', 'ADMIN',   0, FALSE, '2026-10-01 10:05'),
('Marta García',     'marta.garcia@mail.com',   '$2b$10$jugadorHashEjemplo0000000000000000000000000000003', 'JUGADOR', 0, FALSE, '2026-10-03 18:20'),
('Javier Pérez',     'javi.perez@mail.com',     '$2b$10$jugadorHashEjemplo0000000000000000000000000000004', 'JUGADOR', 1, FALSE, '2026-10-05 12:45'),
('Lucía Sanchis',    'lucia.sanchis@mail.com',  '$2b$10$jugadorHashEjemplo0000000000000000000000000000005', 'JUGADOR', 0, FALSE, '2026-10-08 09:10'),
('Álvaro Moltó',     'alvaro.molto@mail.com',   '$2b$10$jugadorHashEjemplo0000000000000000000000000000006', 'JUGADOR', 0, FALSE, '2026-10-10 20:00'),
('Nerea Domènech',   'nerea.domenech@mail.com', '$2b$10$jugadorHashEjemplo0000000000000000000000000000007', 'JUGADOR', 3, TRUE,  '2026-10-12 17:30'),
('Sergio Albors',    'sergio.albors@mail.com',  '$2b$10$jugadorHashEjemplo0000000000000000000000000000008', 'JUGADOR', 0, FALSE, '2026-10-15 11:15'),
('Paula Jordá',      'paula.jorda@mail.com',    '$2b$10$jugadorHashEjemplo0000000000000000000000000000009', 'JUGADOR', 0, FALSE, '2026-10-20 16:40'),
('Andrea Botella',   'andrea.botella@mail.com', '$2b$10$jugadorHashEjemplo0000000000000000000000000000010', 'JUGADOR', 0, FALSE, '2026-10-28 13:00');



-- =========================
-- SALAS
-- 4 activas y 1 inactiva
-- =========================

INSERT INTO salas (nombre, tematica, dificultad, duracion_minutos, capacidad, activa) VALUES
('El Laboratorio Perdido',  'Ciencia ficción', 'MEDIA', 60, 5, TRUE),
('La Cripta del Conde',     'Terror',          'ALTA',  75, 6, TRUE),
('Atraco al Banco',         'Acción',          'BAJA',  60, 6, TRUE),
('El Despacho de Sherlock', 'Investigación',   'ALTA',  90, 4, TRUE),
('La Isla del Pirata',      'Aventura',        'BAJA',  45, 8, FALSE);



-- =========================
-- SESIONES
-- Pasadas (ya jugadas), futuras reservadas,
-- futuras disponibles y una cancelada
-- =========================

INSERT INTO sesiones (sala_id, fecha, hora_inicio, estado) VALUES
-- Sesiones pasadas (id 1-7)
(1, '2026-10-17', '17:00', 'RESERVADA'),
(2, '2026-10-18', '19:00', 'RESERVADA'),
(3, '2026-10-24', '18:00', 'RESERVADA'),
(4, '2026-10-25', '20:00', 'RESERVADA'),
(1, '2026-10-25', '17:00', 'RESERVADA'),
(3, '2026-10-26', '12:00', 'RESERVADA'),
(2, '2026-10-26', '19:00', 'CANCELADA'),
-- Sesiones futuras reservadas (id 8-10)
(1, '2026-11-06', '17:00', 'RESERVADA'),
(2, '2026-11-07', '19:00', 'RESERVADA'),
(4, '2026-11-07', '20:00', 'RESERVADA'),
-- Sesiones futuras disponibles (id 11-14)
(3, '2026-11-08', '18:00', 'DISPONIBLE'),
(1, '2026-11-08', '17:00', 'DISPONIBLE'),
(4, '2026-11-13', '20:00', 'DISPONIBLE'),
(2, '2026-11-14', '19:00', 'DISPONIBLE');



-- =========================
-- RESERVAS
-- Una reserva por sesión (sesion_id es UNIQUE)
-- =========================

INSERT INTO reservas (usuario_id, sesion_id, numero_jugadores, estado, fecha_reserva) VALUES
(3, 1,  4, 'ACTIVA',    '2026-10-10 18:00'),
(4, 2,  5, 'ACTIVA',    '2026-10-11 20:15'),
(5, 3,  3, 'ACTIVA',    '2026-10-15 10:30'),
(3, 4,  2, 'ACTIVA',    '2026-10-18 21:00'),
(6, 5,  5, 'ACTIVA',    '2026-10-19 13:45'),
(8, 6,  6, 'ACTIVA',    '2026-10-20 09:00'),
(7, 7,  4, 'CANCELADA', '2026-10-13 17:00'),
(9, 8,  3, 'ACTIVA',    '2026-10-29 19:30'),
(4, 9,  4, 'ACTIVA',    '2026-10-29 22:10'),
(5, 10, 2, 'ACTIVA',    '2026-10-30 11:00');



-- =========================
-- RESULTADOS
-- Solo de las sesiones ya jugadas
-- (tiempo_minutos es NULL si el equipo no superó la sala)
-- =========================

INSERT INTO resultados (sesion_id, nombre_equipo, tiempo_minutos, superada) VALUES
(1, 'Los Científicos Locos', 52,   TRUE),
(2, 'Cazavampiros',          NULL, FALSE),
(3, 'La Banda del Martes',   41,   TRUE),
(4, 'Watson & Co',           85,   TRUE),
(5, 'Probeta Team',          58,   TRUE),
(6, 'Los Atracadores',       47,   TRUE);
