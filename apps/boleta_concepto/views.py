from apps.boleta_concepto.models import BoletaConcepto
from apps.boleta_concepto.serializers import BoletaConceptoSerializer
from apps.core.api import BaseModelViewSet


class BoletaConceptoViewSet(BaseModelViewSet):
    queryset = BoletaConcepto.objects.all()
    serializer_class = BoletaConceptoSerializer


__all__ = ["BoletaConceptoViewSet"]
