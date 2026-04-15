def format_ubicacion_label(ubicacion):
    if ubicacion is None:
        return ""
    return f"{ubicacion.departamento} / {ubicacion.provincia} / {ubicacion.distrito}"


__all__ = ["format_ubicacion_label"]
