from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.boleta_mensual.models import BoletaMensual
from apps.boleta_mensual.serializers import BoletaMensualSerializer
from apps.core.api import BaseModelViewSet
from apps.personal.models.personal import Personal


class BoletaMensualViewSet(BaseModelViewSet):
    queryset = BoletaMensual.objects.all()
    serializer_class = BoletaMensualSerializer

    class Pagination(PageNumberPagination):
        page_size = 50
        page_size_query_param = "page_size"
        max_page_size = 200

    def get_queryset(self):
        queryset = super().get_queryset()
        anio = self.request.query_params.get("anio")
        mes = self.request.query_params.get("mes")
        personal_ids = self.request.query_params.get("personal_ids")

        if anio:
            queryset = queryset.filter(anio=anio)
        if mes:
            queryset = queryset.filter(mes=mes)
        if personal_ids:
            ids = [item.strip() for item in personal_ids.split(",") if item.strip().isdigit()]
            if ids:
                queryset = queryset.filter(personal_id__in=ids)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        use_pagination = str(request.query_params.get("paginated", "")).strip().lower() in {"1", "true", "yes"}
        if use_pagination:
            paginator = self.Pagination()
            page = paginator.paginate_queryset(queryset, request, view=self)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="generar")
    def generar(self, request):
        anio = request.data.get("anio")
        mes = request.data.get("mes")
        personal_ids = request.data.get("personal_ids") or []
        sueldo_base = request.data.get("sueldo_base", 0)

        try:
            anio = int(anio)
            mes = int(mes)
        except (TypeError, ValueError):
            return Response({"detail": "anio y mes son obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

        if mes < 1 or mes > 12:
            return Response({"detail": "mes debe estar entre 1 y 12."}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(personal_ids, list) or not personal_ids:
            return Response(
                {"detail": "Debe enviar personal_ids como lista con al menos un elemento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_ids = []
        for item in personal_ids:
            try:
                valid_ids.append(int(item))
            except (TypeError, ValueError):
                continue

        if not valid_ids:
            return Response({"detail": "No se enviaron IDs validos."}, status=status.HTTP_400_BAD_REQUEST)

        existing_personal_ids = set(Personal.objects.filter(id__in=valid_ids).values_list("id", flat=True))
        target_ids = [pid for pid in valid_ids if pid in existing_personal_ids]

        existing_boletas_ids = set(
            BoletaMensual.objects.filter(anio=anio, mes=mes, personal_id__in=target_ids).values_list(
                "personal_id", flat=True
            )
        )
        new_ids = [pid for pid in target_ids if pid not in existing_boletas_ids]

        try:
            sueldo = float(sueldo_base)
        except (TypeError, ValueError):
            sueldo = 0

        BoletaMensual.objects.bulk_create(
            [
                BoletaMensual(
                    personal_id=pid,
                    anio=anio,
                    mes=mes,
                    sueldo_base=sueldo,
                    total_ingresos=sueldo,
                    total_descuentos=0,
                    neto_pagar=sueldo,
                )
                for pid in new_ids
            ]
        )

        return Response(
            {
                "recibidos": len(valid_ids),
                "validos": len(target_ids),
                "creados": len(new_ids),
                "existentes": len(existing_boletas_ids),
            }
        )
