# Diagramas UML del Sprint 3 — EscapeHub

**Proyecto:** Sistema de creación y gestión de Escape Rooms · **Autor de la documentación:** Ferran  
**Objetivo:** representar las interacciones y estados asociados a recursos REST, de acuerdo con el modelo de datos ampliado al finalizar Sprint 2 (14 tablas).

Los diagramas están escritos en Mermaid para renderizarse directamente en GitHub. No son imágenes estáticas; pueden mantenerse y versionarse con el código. **La lógica de servidor dibujada es el diseño objetivo, no una afirmación de que David ya la haya implementado.**

## 1. Secuencia: reservar una sesión

```mermaid
sequenceDiagram
    autonumber
    actor J as Jugador
    participant UI as Frontend EscapeHub
    participant API as API Flask
    participant DB as PostgreSQL
    J->>UI: Selecciona sala, sesión y jugadores
    UI->>API: POST /api/reservas (Bearer token)
    API->>API: Validar identidad y datos
    API->>DB: BEGIN + bloquear sesión
    DB-->>API: Estado, capacidad y fecha
    alt Sesión libre y dentro de capacidad
        API->>DB: INSERT reserva + UPDATE sesión
        DB-->>API: Commit confirmado
        API-->>UI: 201 Created + JSON reserva
        UI-->>J: Mostrar confirmación y actualizar sesiones
    else Sesión ocupada
        API->>DB: ROLLBACK
        API-->>UI: 409 Conflict
        UI-->>J: Avisar de ocupación
    else Capacidad/fecha inválida
        API->>DB: ROLLBACK
        API-->>UI: 422 Unprocessable Content
        UI-->>J: Mostrar motivo
    end
```

**Explicación:** una reserva se hace mediante `POST`; el backend es quien comprueba ocupación y aforo, no el navegador. La operación de verificación y escritura debe ser atómica para evitar reservas simultáneas.

## 2. Actividad: reserva y cancelación

```mermaid
flowchart TD
    A([Inicio]) --> B[Identificar al jugador]
    B --> C[Consultar salas y sesiones]
    C --> D[Elegir sesión y nº de jugadores]
    D --> E{¿Datos válidos?}
    E -- No --> F[Mostrar error] --> D
    E -- Sí --> G{¿Disponible y con capacidad?}
    G -- No --> H[Mostrar alternativas] --> C
    G -- Sí --> I[Registrar reserva]
    I --> J[Mostrar confirmación]
    J --> K{¿Solicita cancelar?}
    K -- No --> Z([Fin])
    K -- Sí --> L{¿Es titular y faltan 24 h o más?}
    L -- No --> M[Rechazar cancelación] --> Z
    L -- Sí --> N[Marcar reserva como cancelada]
    N --> O[Actualizar disponibilidad]
    O --> P[Confirmar cancelación] --> Z
```

**Explicación:** el diagrama señala las validaciones, alternativas y regla temporal del RF-08. Las acciones sobre la base de datos son responsabilidad del servicio.

## 3. Estados: ciclo de vida de una sesión

```mermaid
stateDiagram-v2
    [*] --> DISPONIBLE: Administrador crea sesión
    DISPONIBLE --> RESERVADA: Reserva confirmada
    RESERVADA --> DISPONIBLE: Cancelación válida
    DISPONIBLE --> CANCELADA: Administrador anula sesión
    RESERVADA --> CANCELADA: Anulación administrativa excepcional
    CANCELADA --> [*]: Fin administrativo
```

**Nota:** `CANCELADA` es el estado de la **sesión**, diferente de una reserva histórica cancelada. Las reglas para anulación administrativa con una reserva activa deben decidirse e implementarse de manera explícita.

## 4. Estados: ciclo de vida de una reserva

```mermaid
stateDiagram-v2
    [*] --> ACTIVA: POST /api/reservas
    ACTIVA --> CANCELADA: PUT /api/reservas/id
    CANCELADA --> [*]: Registro histórico conservado
```

**Explicación:** una reserva cancelada se conserva para el historial. La sesión vuelve a estar disponible si la cancelación es válida. No se elimina el historial.

## 5. Componentes: división de responsabilidades

```mermaid
flowchart LR
    J[Jugador / Administrador] --> UI[HTML + CSS + JavaScript]
    UI -->|HTTP + JSON| API[API REST Flask]
    API -->|SQLAlchemy| BD[(PostgreSQL)]
    API --> AUTH[Validación y roles]
    API --> REGLAS[Reglas de reserva / aforo / cancelación]
```

## 6. Relación con el modelo de datos y los requisitos

| Recurso | Tabla SQL | Requisitos | Diagrama relevante |
|---|---|---|---|
| Usuario | `usuarios` | RF-01, RF-02, RF-03 | Componentes / autenticación |
| Sala | `salas` | RF-04, RF-10 | Componentes |
| Sesión | `sesiones` | RF-05, RF-07, RF-11 | Secuencia, estados |
| Reserva | `reservas` | RF-06, RF-08, RF-09 | Secuencia, actividad, estados |
| Resultado | `resultados` | RF-12 | Componentes |

Los diagramas representan el comportamiento deseado del sistema a través de REST. Si durante la implementación se cambia el contrato de la API, se actualizarán antes de cerrar el issue.


## 7. Diagrama de secuencia: resolver un reto y persistir el progreso

```mermaid
sequenceDiagram
    autonumber
    actor J as Jugador
    participant F as Frontend
    participant A as API Flask
    participant BD as PostgreSQL
    J->>F: Abre una partida autorizada
    F->>A: GET /api/partidas/8 (Bearer)
    A->>BD: Consultar partida, progreso, inventario y pistas usadas
    BD-->>A: Datos asociados al jugador
    A-->>F: 200 JSON sin respuestas ni hashes
    F-->>J: Mostrar retos disponibles
    J->>F: Introduce respuesta
    F->>A: POST /api/partidas/8/retos/15/intentos
    A->>A: Verificar rol, reserva, horario, estado y reto desbloqueado
    A->>BD: BEGIN y bloquear filas relevantes
    A->>A: Validar respuesta usando HMAC de servidor
    A->>BD: INSERT intentos_reto
    alt Respuesta correcta
        A->>BD: Actualizar progreso_retos y desbloqueos
        opt Todos los retos superados
            A->>BD: Finalizar partida y registrar resultado
        end
    else Respuesta incorrecta
        A->>BD: Mantener progreso y contabilizar intento
    end
    A->>BD: COMMIT
    A-->>F: 200 {correcta,reto_estado,partida_estado}
    F->>A: GET /api/partidas/8
    A-->>F: Estado actualizado
    F-->>J: Refrescar reto, progreso e inventario
```

## 8. Actividad: iniciar partida y desbloquear retos

```mermaid
flowchart TD
 A([Inicio]) --> B[Seleccionar reserva activa]
 B --> C{¿Es propia y horario permitido?}
 C -- No --> X[Rechazar y mostrar error] --> Z([Fin])
 C -- Sí --> D[Crear partida PENDIENTE]
 D --> E[Iniciar EN_CURSO y registrar inicio]
 E --> F[Crear progreso inicial según dependencias]
 F --> G[Mostrar retos DISPONIBLES]
 G --> H[Jugador envía respuesta o usa pista]
 H --> I{¿Acción autorizada?}
 I -- No --> X
 I -- Sí --> J[Guardar intento o uso de pista]
 J --> K{¿Respuesta correcta?}
 K -- No --> G
 K -- Sí --> L[Marcar reto COMPLETADO]
 L --> M[Evaluar dependencias y desbloquear]
 M --> N{¿Todos completados?}
 N -- No --> G
 N -- Sí --> O[Marcar SUPERADA, fin y resultado]
 O --> Z
```

## 9. Estados de una partida

```mermaid
stateDiagram-v2
 [*] --> PENDIENTE: Reserva válida
 PENDIENTE --> EN_CURSO: Iniciar con horario autorizado
 EN_CURSO --> SUPERADA: Todos los retos completados
 EN_CURSO --> AGOTADA: Tiempo agotado
 EN_CURSO --> ABANDONADA: Abandono confirmado
 SUPERADA --> [*]
 AGOTADA --> [*]
 ABANDONADA --> [*]
```

## 10. Estados de un reto dentro de una partida

```mermaid
stateDiagram-v2
 [*] --> BLOQUEADO: Tiene prerrequisitos pendientes
 [*] --> DISPONIBLE: No tiene prerrequisitos
 BLOQUEADO --> DISPONIBLE: Se completan prerrequisitos
 DISPONIBLE --> COMPLETADO: Respuesta validada
 COMPLETADO --> [*]
```

## 11. Recursos SQL y responsabilidad

```mermaid
flowchart TD
 U[usuarios] --> R[reservas]
 S[salas] --> SE[sesiones]
 SE --> R
 SE --> RES[resultados]
 R --> P[partidas]
 S --> RET[retos]
 RET --> DEP[dependencias_reto]
 RET --> PIS[pistas]
 S --> OBJ[objetos]
 P --> PRO[progreso_retos]
 RET --> PRO
 PRO --> INT[intentos_reto]
 P --> PU[pistas_utilizadas]
 PIS --> PU
 P --> INV[inventario_partida]
 OBJ --> INV
```

**Nota del diagrama:** son relaciones lógicas; la implementación SQL contiene FKs simples y compuestas. `dependencias_reto` referencia dos veces a `retos`, y `pistas_utilizadas` asocia partida, reto y pista. Las decisiones sobre respuestas de tipo `OBJETO`, penalización y autorización son lógica de negocio, no se delegan al frontend.
