from django.db import models

from apps.core.api import BaseModelViewSet
from apps.descanso_medico.models import DescansoMedico
from apps.descanso_medico.serializers import DescansoMedicoSerializer


class DescansoMedicoViewSet(BaseModelViewSet):
    queryset = DescansoMedico.objects.select_related("personal", "personal__sucursal", "personal__area").all()
    serializer_class = DescansoMedicoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sucursal = self.request.query_params.get("sucursal")
        area = self.request.query_params.get("area")
        motivo = self.request.query_params.get("motivo")
        fecha = self.request.query_params.get("fecha")
        mes = self.request.query_params.get("mes")
        anio = self.request.query_params.get("anio")
        q = self.request.query_params.get("q")

        if sucursal:
            queryset = queryset.filter(personal__sucursal_id=sucursal)
        if area:
            queryset = queryset.filter(personal__area_id=area)
        if motivo:
            queryset = queryset.filter(motivo=motivo)
        if fecha:
            queryset = queryset.filter(fecha_inicio=fecha)
        if mes:
            queryset = queryset.filter(fecha_inicio__month=mes)
        if anio:
            queryset = queryset.filter(fecha_inicio__year=anio)
        if q:
            queryset = queryset.filter(
                models.Q(personal__nombres_completos__icontains=q)
                | models.Q(personal__numero_documento__icontains=q)
                | models.Q(numero_documento__icontains=q)
            )

        return queryset
