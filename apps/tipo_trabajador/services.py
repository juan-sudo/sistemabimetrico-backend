def build_tipo_trabajador_label(tipo_trabajador):
    if tipo_trabajador is None:
        return ""
    return f"{tipo_trabajador.codigo} - {tipo_trabajador.descripcion}"


__all__ = ["build_tipo_trabajador_label"]
