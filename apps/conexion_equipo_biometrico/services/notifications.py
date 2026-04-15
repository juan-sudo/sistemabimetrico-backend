from datetime import timedelta

from django.utils.timezone import localdate

from apps.descanso_medico.models import DescansoMedico
from apps.justificacion.models import Justificacion
from apps.marcacion.models import Marcacion
from apps.personal.models.personal import Personal


def build_missing_mark_notifications():
    today = localdate()
    yesterday = today - timedelta(days=1)
    start_day = yesterday
    end_day = today

    justificados = set()
    for item in Justificacion.objects.filter(
        fecha_inicio__lte=end_day,
        fecha_fin__gte=start_day,
        estado=Justificacion.Estado.AUTORIZADO,
    ):
        current = max(item.fecha_inicio, start_day)
        limit = min(item.fecha_fin, end_day)
        while current <= limit:
            justificados.add((item.personal_id, current))
            current += timedelta(days=1)

    descansos = set()
    for item in DescansoMedico.objects.filter(
        fecha_inicio__lte=end_day,
        fecha_fin__gte=start_day,
    ):
        current = max(item.fecha_inicio, start_day)
        limit = min(item.fecha_fin, end_day)
        while current <= limit:
            descansos.add((item.personal_id, current))
            current += timedelta(days=1)

    marcaciones = set(
        Marcacion.objects.filter(
            fecha_hora__date__gte=start_day,
            fecha_hora__date__lte=end_day,
        ).values_list("personal_id", "fecha_hora__date")
    )

    notifications = []
    for personal in Personal.objects.filter(estado=Personal.Estado.ACTIVO).order_by("nombres_completos"):
        for target_day in (yesterday, today):
            key = (personal.id, target_day)
            if key in marcaciones or key in justificados or key in descansos:
                continue
            notifications.append(
                {
                    "personal_id": personal.id,
                    "personal": personal.nombres_completos,
                    "numero_documento": personal.numero_documento,
                    "codigo_empleado": personal.codigo_empleado,
                    "fecha": target_day.isoformat(),
                    "tipo": "MARCACION_FALTANTE",
                    "detalle": "Sin marcacion registrada ni sustento en el periodo monitoreado.",
                }
            )

    return notifications
