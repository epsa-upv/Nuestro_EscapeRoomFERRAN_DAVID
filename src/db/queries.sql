-- =====================================================
-- ESCAPEHUB
-- Sprint 2 - Consultas de prueba
-- PostgreSQL
-- Ejecutar después de schema.sql y seed.sql
-- En pgAdmin: seleccionar una consulta y pulsar F5
-- =====================================================


-- =========================
-- C1. Número de filas de cada tabla
-- Esperado: usuarios 10, salas 5, sesiones 14,
--           reservas 10, resultados 6
-- =========================

SELECT 'usuarios' AS tabla, COUNT(*) AS filas FROM usuarios
UNION ALL SELECT 'salas',      COUNT(*) FROM salas
UNION ALL SELECT 'sesiones',   COUNT(*) FROM sesiones
UNION ALL SELECT 'reservas',   COUNT(*) FROM reservas
UNION ALL SELECT 'resultados', COUNT(*) FROM resultados;



-- =========================
-- C2. Salas activas ordenadas por dificultad
-- =========================

SELECT nombre, tematica, dificultad, duracion_minutos, capacidad
FROM salas
WHERE activa = TRUE
ORDER BY CASE dificultad
             WHEN 'BAJA'  THEN 1
             WHEN 'MEDIA' THEN 2
             WHEN 'ALTA'  THEN 3
         END,
         nombre;



-- =========================
-- C3. Sesiones disponibles para reservar
-- =========================

SELECT se.fecha, se.hora_inicio, sa.nombre AS sala, sa.capacidad
FROM sesiones se
JOIN salas sa ON sa.id = se.sala_id
WHERE se.estado = 'DISPONIBLE'
  AND sa.activa = TRUE
ORDER BY se.fecha, se.hora_inicio;



-- =========================
-- C4. Reservas activas con usuario, sala, fecha y hora
-- =========================

SELECT r.id AS reserva, u.nombre AS usuario, sa.nombre AS sala,
       se.fecha, se.hora_inicio, r.numero_jugadores
FROM reservas r
JOIN usuarios u  ON u.id  = r.usuario_id
JOIN sesiones se ON se.id = r.sesion_id
JOIN salas sa    ON sa.id = se.sala_id
WHERE r.estado = 'ACTIVA'
ORDER BY se.fecha, se.hora_inicio;



-- =========================
-- C5. Reservas de un usuario concreto (Marta García)
-- =========================

SELECT sa.nombre AS sala, se.fecha, se.hora_inicio,
       r.numero_jugadores, r.estado
FROM reservas r
JOIN usuarios u  ON u.id  = r.usuario_id
JOIN sesiones se ON se.id = r.sesion_id
JOIN salas sa    ON sa.id = se.sala_id
WHERE u.email = 'marta.garcia@mail.com'
ORDER BY se.fecha;



-- =========================
-- C6. Ranking de los equipos más rápidos
-- =========================

SELECT re.nombre_equipo, sa.nombre AS sala, re.tiempo_minutos
FROM resultados re
JOIN sesiones se ON se.id = re.sesion_id
JOIN salas sa    ON sa.id = se.sala_id
WHERE re.superada = TRUE
ORDER BY re.tiempo_minutos
LIMIT 5;



-- =========================
-- C7. Estadísticas por sala
-- (partidas jugadas, % superadas y tiempo medio)
-- =========================

SELECT sa.nombre AS sala,
       COUNT(re.id) AS partidas,
       ROUND(100.0 * SUM(CASE WHEN re.superada THEN 1 ELSE 0 END)
             / NULLIF(COUNT(re.id), 0), 1) AS porcentaje_superada,
       ROUND(AVG(re.tiempo_minutos), 1) AS tiempo_medio
FROM salas sa
LEFT JOIN sesiones se   ON se.sala_id   = sa.id
LEFT JOIN resultados re ON re.sesion_id = se.id
GROUP BY sa.nombre
ORDER BY partidas DESC, sa.nombre;



-- =========================
-- C8. Usuarios con más de una reserva
-- =========================

SELECT u.nombre, u.email, COUNT(*) AS reservas
FROM usuarios u
JOIN reservas r ON r.usuario_id = u.id
GROUP BY u.id, u.nombre, u.email
HAVING COUNT(*) > 1
ORDER BY reservas DESC;



-- =========================
-- C9. Jugadores que nunca han reservado
-- =========================

SELECT u.nombre, u.email
FROM usuarios u
WHERE u.rol = 'JUGADOR'
  AND NOT EXISTS (
      SELECT 1 FROM reservas r WHERE r.usuario_id = u.id
  );



-- =========================
-- C10. Usuarios bloqueados o con intentos fallidos
-- =========================

SELECT nombre, email, intentos_fallidos, bloqueado
FROM usuarios
WHERE bloqueado = TRUE OR intentos_fallidos > 0
ORDER BY intentos_fallidos DESC;



-- =========================
-- C11. Comprobación de coherencia:
-- reservas con más jugadores que la capacidad de la sala
-- Esperado: 0 filas
-- =========================

SELECT r.id AS reserva, sa.nombre AS sala,
       r.numero_jugadores, sa.capacidad
FROM reservas r
JOIN sesiones se ON se.id = r.sesion_id
JOIN salas sa    ON sa.id = se.sala_id
WHERE r.numero_jugadores > sa.capacidad;



-- =====================================================
-- PRUEBAS DE RESTRICCIONES
-- Cada bloque intenta insertar un dato incorrecto.
-- Si la base de datos lo rechaza, muestra "OK" en
-- Messages / Mensajes. No modifica ningún dato.
-- =====================================================

-- R1. Email duplicado (UNIQUE)
DO $$
BEGIN
    INSERT INTO usuarios (nombre, email, password_hash)
    VALUES ('Prueba', 'marta.garcia@mail.com', 'x');
    RAISE EXCEPTION 'FALLO: se ha aceptado un email duplicado';
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'R1 OK: email duplicado rechazado';
END $$;


-- R2. Rol no permitido (CHECK)
DO $$
BEGIN
    INSERT INTO usuarios (nombre, email, password_hash, rol)
    VALUES ('Prueba', 'prueba@mail.com', 'x', 'SUPERUSER');
    RAISE EXCEPTION 'FALLO: se ha aceptado un rol incorrecto';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'R2 OK: rol incorrecto rechazado';
END $$;


-- R3. Dificultad no permitida (CHECK)
DO $$
BEGIN
    INSERT INTO salas (nombre, tematica, dificultad, capacidad)
    VALUES ('Sala Prueba', 'Prueba', 'EXTREMA', 4);
    RAISE EXCEPTION 'FALLO: se ha aceptado una dificultad incorrecta';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'R3 OK: dificultad incorrecta rechazada';
END $$;


-- R4. Capacidad menor que 2 (CHECK)
DO $$
BEGIN
    INSERT INTO salas (nombre, tematica, dificultad, capacidad)
    VALUES ('Sala Prueba', 'Prueba', 'BAJA', 1);
    RAISE EXCEPTION 'FALLO: se ha aceptado una capacidad de 1';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'R4 OK: capacidad menor que 2 rechazada';
END $$;


-- R5. Dos sesiones de la misma sala a la misma fecha y hora (UNIQUE)
DO $$
BEGIN
    INSERT INTO sesiones (sala_id, fecha, hora_inicio)
    VALUES (1, '2026-11-06', '17:00');
    RAISE EXCEPTION 'FALLO: se ha aceptado una sesión duplicada';
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'R5 OK: sesión duplicada rechazada';
END $$;


-- R6. Sesión de una sala que no existe (FOREIGN KEY)
DO $$
BEGIN
    INSERT INTO sesiones (sala_id, fecha, hora_inicio)
    VALUES (999, '2026-12-01', '17:00');
    RAISE EXCEPTION 'FALLO: se ha aceptado una sala inexistente';
EXCEPTION WHEN foreign_key_violation THEN
    RAISE NOTICE 'R6 OK: sala inexistente rechazada';
END $$;


-- R7. Segunda reserva para una sesión ya reservada (UNIQUE)
DO $$
BEGIN
    INSERT INTO reservas (usuario_id, sesion_id, numero_jugadores)
    VALUES (10, 8, 2);
    RAISE EXCEPTION 'FALLO: se ha aceptado una reserva duplicada';
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'R7 OK: sesión ya reservada rechazada';
END $$;


-- R8. Reserva con 0 jugadores (CHECK)
DO $$
BEGIN
    INSERT INTO reservas (usuario_id, sesion_id, numero_jugadores)
    VALUES (10, 11, 0);
    RAISE EXCEPTION 'FALLO: se ha aceptado una reserva con 0 jugadores';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'R8 OK: reserva con 0 jugadores rechazada';
END $$;


-- R9. Reserva de un usuario que no existe (FOREIGN KEY)
DO $$
BEGIN
    INSERT INTO reservas (usuario_id, sesion_id, numero_jugadores)
    VALUES (999, 11, 2);
    RAISE EXCEPTION 'FALLO: se ha aceptado un usuario inexistente';
EXCEPTION WHEN foreign_key_violation THEN
    RAISE NOTICE 'R9 OK: usuario inexistente rechazado';
END $$;


-- R10. Resultado con tiempo negativo (CHECK)
DO $$
BEGIN
    INSERT INTO resultados (sesion_id, nombre_equipo, tiempo_minutos, superada)
    VALUES (8, 'Equipo Prueba', -5, TRUE);
    RAISE EXCEPTION 'FALLO: se ha aceptado un tiempo negativo';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'R10 OK: tiempo negativo rechazado';
END $$;


-- R11. Usuario sin email (NOT NULL)
DO $$
BEGIN
    INSERT INTO usuarios (nombre, email, password_hash)
    VALUES ('Prueba', NULL, 'x');
    RAISE EXCEPTION 'FALLO: se ha aceptado un usuario sin email';
EXCEPTION WHEN not_null_violation THEN
    RAISE NOTICE 'R11 OK: usuario sin email rechazado';
END $$;


-- R12. Borrar una sala con sesiones (ON DELETE RESTRICT)
DO $$
BEGIN
    DELETE FROM salas WHERE id = 1;
    RAISE EXCEPTION 'FALLO: se ha borrado una sala con sesiones';
EXCEPTION WHEN foreign_key_violation OR restrict_violation THEN
    RAISE NOTICE 'R12 OK: no se puede borrar una sala con sesiones';
END $$;
