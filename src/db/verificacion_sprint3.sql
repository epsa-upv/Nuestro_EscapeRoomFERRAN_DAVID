-- Pruebas no destructivas para pgAdmin; ejecutar después de la migración.
-- Se validan nombres, FK y restricciones mediante metadatos del sistema.

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'retos', 'dependencias_reto', 'pistas', 'objetos', 'partidas',
      'progreso_retos', 'intentos_reto', 'pistas_utilizadas', 'inventario_partida'
  )
ORDER BY table_name;
-- Resultado esperado: nueve filas.

SELECT table_name, constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'public'
  AND table_name IN ('retos', 'partidas', 'progreso_retos', 'inventario_partida')
ORDER BY table_name, constraint_type, constraint_name;

SELECT * FROM vista_progreso_partida ORDER BY partida_id;
-- Puede estar vacía si todavía no se han creado partidas reales.

-- Verificación de integridad: debe devolver 0 filas.
SELECT p.id AS partida_incoherente
FROM partidas p
JOIN sesiones s ON p.sesion_id = s.id
JOIN reservas r ON p.reserva_id = r.id
WHERE s.sala_id <> p.sala_id OR r.sesion_id <> p.sesion_id;
