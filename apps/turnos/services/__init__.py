def format_turno_horario(bloques):
    bloques = list(bloques or [])
    if not bloques:
        return ""
    bloques = sorted(bloques, key=lambda item: item.orden)
    return " / ".join(f"{item.hora_entrada.strftime('%H:%M')}-{item.hora_salida.strftime('%H:%M')}" for item in bloques)


def build_turno_label(turno):
    if turno is None:
        return ""
    return f"{turno.codigo} - {turno.nombre}"


__all__ = ["build_turno_label", "format_turno_horario"]
