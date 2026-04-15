from apps.reporte_asistencia_diaria.models import ReporteAsistenciaDiaria
from apps.reporte_asistencia_diaria.serializers import ReporteAsistenciaDiariaSerializer


class AsistenciaDiariaSerializer(ReporteAsistenciaDiariaSerializer):
    class Meta(ReporteAsistenciaDiariaSerializer.Meta):
        model = ReporteAsistenciaDiaria
        fields = "__all__"


__all__ = ["AsistenciaDiariaSerializer"]
