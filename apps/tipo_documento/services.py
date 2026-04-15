def build_tipo_documento_label(tipo_documento):
    if tipo_documento is None:
        return ""
    return f"{tipo_documento.codigo} - {tipo_documento.descripcion}"


__all__ = ["build_tipo_documento_label"]
