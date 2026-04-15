from datetime import datetime, time

from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.core.api import BaseModelViewSet
from apps.marcacion.models import Marcacion
from apps.marcacion.serializers import MarcacionSerializer


class MarcacionPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class MarcacionViewSet(BaseModelViewSet):
    queryset = Marcacion.objects.select_related("personal", "dispositivo").all()
    serializer_class = MarcacionSerializer
    pagination_class = MarcacionPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        personal = self.request.query_params.get("personal")
        fecha_inicio = self.request.query_params.get("fecha_inicio")
        fecha_fin = self.request.query_params.get("fecha_fin")
        q = self.request.query_params.get("q") or self.request.query_params.get("search")

        if personal:
            queryset = queryset.filter(personal_id=personal)
        if fecha_inicio:
            start = parse_date(fecha_inicio)
            if start:
                start_dt = timezone.make_aware(datetime.combine(start, time.min))
                queryset = queryset.filter(fecha_hora__gte=start_dt)
        if fecha_fin:
            end = parse_date(fecha_fin)
            if end:
                end_dt = timezone.make_aware(datetime.combine(end, time.max))
                queryset = queryset.filter(fecha_hora__lte=end_dt)
        if q:
            queryset = queryset.filter(
                models.Q(personal__nombres_completos__icontains=q)
                | models.Q(personal__numero_documento__icontains=q)
                | models.Q(personal__codigo_empleado__icontains=q)
                | models.Q(codigo_equipo__icontains=q)
            )

        return queryset.order_by("-fecha_hora", "personal_id")

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
