def build_sucursal_label(sucursal):
    if sucursal is None:
        return ""
    empresa = sucursal.empresa.razon_social if getattr(sucursal, "empresa_id", None) else ""
    return f"{sucursal.codigo} - {sucursal.nombre}" if not empresa else f"{empresa} / {sucursal.codigo} - {sucursal.nombre}"


__all__ = ["build_sucursal_label"]
