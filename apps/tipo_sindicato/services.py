def build_tipo_sindicato_label(tipo_sindicato):
    if tipo_sindicato is None:
        return ""
    return f"{tipo_sindicato.codigo} - {tipo_sindicato.descripcion}"


__all__ = ["build_tipo_sindicato_label"]
