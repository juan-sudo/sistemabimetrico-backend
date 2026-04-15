def build_periodo_label(anio, mes):
    return f"{int(mes):02d}/{anio}" if anio and mes else ""


__all__ = ["build_periodo_label"]
