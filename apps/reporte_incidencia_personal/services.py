def build_periodo_label(anio, mes):
    return f"{int(mes):02d}/{anio}" if anio and mes else ""


def build_rango_label(fecha_inicio, fecha_fin):
    if not fecha_inicio:
        return ""
    if not fecha_fin or fecha_inicio == fecha_fin:
        return str(fecha_inicio)
    return f"{fecha_inicio} a {fecha_fin}"


__all__ = ["build_periodo_label", "build_rango_label"]
