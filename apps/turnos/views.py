from apps.core.api import BaseModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from apps.turnos.models.personal_turno import PersonalTurno
from apps.turnos.models.turno import Turno
from apps.turnos.models.turno_bloque_horario import TurnoBloqueHorario
from apps.turnos.selectors import (
    filter_personal_turno_queryset,
    filter_turno_bloque_queryset,
    filter_turno_queryset,
    get_personal_turno_queryset,
    get_turno_bloque_queryset,
    get_turno_queryset,
)
from apps.turnos.serializers import PersonalTurnoSerializer, TurnoBloqueHorarioSerializer, TurnoSerializer


class PersonalTurnoPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class TurnoViewSet(BaseModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer

    def get_queryset(self):
        queryset = get_turno_queryset()
        return filter_turno_queryset(
            queryset,
            activo=self.request.query_params.get("activo"),
            tipo=self.request.query_params.get("tipo"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("nombre")


class TurnoBloqueHorarioViewSet(BaseModelViewSet):
    queryset = TurnoBloqueHorario.objects.all()
    serializer_class = TurnoBloqueHorarioSerializer

    def get_queryset(self):
        queryset = get_turno_bloque_queryset()
        return filter_turno_bloque_queryset(
            queryset,
            turno=self.request.query_params.get("turno"),
        ).order_by("turno_id", "orden")


class PersonalTurnoViewSet(BaseModelViewSet):
    queryset = PersonalTurno.objects.all()
    serializer_class = PersonalTurnoSerializer
    pagination_class = PersonalTurnoPagination

    def get_queryset(self):
        queryset = get_personal_turno_queryset()
        search_term = (self.request.query_params.get("q") or self.request.query_params.get("search") or "").strip()
        return filter_personal_turno_queryset(
            queryset,
            personal=self.request.query_params.get("personal"),
            turno=self.request.query_params.get("turno"),
            fecha_inicio=self.request.query_params.get("fecha_inicio"),
            fecha_fin=self.request.query_params.get("fecha_fin"),
            q=search_term,
        ).order_by("-fecha_inicio", "personal__nombres_completos")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        use_pagination = str(request.query_params.get("paginated", "")).strip().lower() in {"1", "true", "yes"}
        if use_pagination:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
