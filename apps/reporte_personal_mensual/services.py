def build_periodo_label(anio, mes):
    return f"{int(mes):02d}/{anio}" if anio and mes else ""


def build_resumen_label(reporte):
    return f"{reporte.total_dias_laborados} laborados / {reporte.total_dias_falta} faltas / {reporte.total_horas_extra} extras"


__all__ = ["build_periodo_label", "build_resumen_label"]
