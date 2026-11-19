# Backend de EscapeHub (Flask + SQLAlchemy + PostgreSQL)

Implementa el contrato [`doc/api_rest.md`](../../doc/api_rest.md) sobre las 14 tablas del modelo
(5 del Sprint 2 + 9 de la ampliación). Notas de implementación: [`doc/backend_sprint3.md`](../../doc/backend_sprint3.md).

Flask sirve también la web de `src/` (`index.html`, `js/api.js`…): se abre todo en **http://127.0.0.1:5000**.

## Estructura

```text
src/backend/
    run.py                  Arranca el servidor
    requirements.txt        Dependencias
    .env.example            Plantilla de configuración (copiar como .env, que NO se sube)
    app/
        __init__.py         Crea la app, sirve la web y registra las rutas
        config.py           Configuración (.env)
        db.py               Conexión SQLAlchemy y transacción por petición
        auth.py             Tokens y permisos (JUGADOR / ADMIN / titular)
        errores.py          Errores {"error": {"codigo", "mensaje"}}
        validacion.py       Validación de datos recibidos
        serial.py           Objetos JSON del contrato
        juego.py            HMAC de respuestas y detección de la migración
        demo.py             Comando "flask --app run demo" (datos de prueba)
        rutas/
            auth.py         §2 Registro y login
            salas.py        §3 Salas
            sesiones.py     §4 Sesiones
            reservas.py     §5 Reservas
            resultados.py   §6 Resultados
            juego_admin.py  §7 Retos, pistas, objetos y dependencias
            partidas.py     §8 Partidas, respuestas y progreso
    tests/                  Pruebas automáticas (pytest)
```

## 1. Base de datos

En pgAdmin, conectado como `postgres`, sobre `escapehub`, **en este orden** (cada archivo una sola vez):

1. `src/db/verificacion_sprint3.sql` → si no salen las 9 tablas, ejecutar `src/db/ampliacion_sprint3.sql`.
2. `src/db/migracion_sprint3.sql` (decisiones A, B y C; pendiente de aprobar por Ferran).
   Sin ella el backend funciona, pero no se puede re-reservar una sesión cancelada y los retos OPCION/OBJETO dan 422.
3. Base de datos para las pruebas:
   ```sql
   CREATE DATABASE escapehub_test OWNER escapeuser;
   ```

⚠️ No volver a ejecutar `seed.sql` sobre `escapehub`: su `TRUNCATE ... CASCADE` borraría partidas y progreso.

## 2. Entorno de Python (PowerShell, en `src/backend`)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Abre `.env` y cambia `SECRET_KEY`, `RESPUESTA_SECRET` y `DEMO_PASSWORD`.
**No cambies `RESPUESTA_SECRET` después de crear retos**: las respuestas guardadas dejarían de coincidir.

## 3. Datos de demostración

```powershell
flask --app run demo --sesion-ahora
```

- Pone la contraseña de `DEMO_PASSWORD` a los usuarios del seed (sus hashes eran ficticios).
- Crea retos de ejemplo en las salas 1 y 2 (si no tienen ninguno).
- `--sesion-ahora` crea una sesión de la sala 1 que empieza en 10 minutos, para poder reservar y jugar ya.

## 4. Arrancar

```powershell
python run.py
```

- Web: <http://127.0.0.1:5000>
- Comprobación: <http://127.0.0.1:5000/api/health> → `{"estado": "ok", "base_de_datos": "ok"}`

## 5. Pruebas

```powershell
python -m pytest -v
```

Usan `escapehub_test` (se borra y se recrea en cada prueba); nunca tocan `escapehub`.
