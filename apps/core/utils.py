from __future__ import annotations

from datetime import date, timedelta
from typing import Iterator


MONTH_LABELS = (
    "",
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)


def date_range(start: date, end: date) -> Iterator[date]:
    """Yields every date from start to end inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def get_boleta_conceptos(boleta):
    if not boleta:
        return []
    prefetched = getattr(boleta, "_prefetched_objects_cache", {}).get("conceptos")
    conceptos = list(prefetched) if prefetched is not None else list(boleta.conceptos.all())
    return sorted(conceptos, key=lambda item: (item.tipo, item.concepto, item.id))


__all__ = ["date_range", "get_boleta_conceptos", "MONTH_LABELS"]
