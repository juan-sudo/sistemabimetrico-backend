# Checklist de Rendimiento (Backend + Frontend)

## Endpoints y Consultas
- Aplicar filtros server-side para cualquier listado grande.
- Usar serializer `lite` cuando la UI no necesite todos los campos.
- Evitar respuestas gigantes por defecto (`include_raw=1` opcional para depuracion).
- Usar `only()`/`select_related()`/`prefetch_related()` cuando corresponda.
- Evitar cargar datasets completos en memoria si se pueden procesar por lotes.

## Procesamiento Masivo
- Procesar en chunks (`batch size`) para lectura y escritura.
- Preferir `bulk_create`/`bulk_update` para inserciones masivas.
- Limitar payload de depuracion (`raw_limit`, `raw_offset`).
- Desacoplar tareas pesadas con cola async cuando este disponible.

## Frontend
- Carga inicial con Server Components cuando haya datos grandes de arranque.
- Evitar cascadas de requests en cliente para el primer render.
- Aplicar `debounce` en busquedas.
- Evitar filtrar listas enormes en cliente si se puede filtrar en backend.
- Mostrar estado de `isFetching` para no bloquear la UX.

