from datetime import timedelta

from django.utils.timezone import localdate

from apps.core.utils import date_range
from apps.descanso_medico.models import DescansoMedico
from apps.justificacion.models import Justificacion
from apps.marcacion.models import Marcacion
from apps.personal.models.personal import Personal


def build_missing_mark_notifications():
    today = localdate()
    yesterday = today - timedelta(days=1)

    justificados = set()
    for item in Justificacion.objects.filter(
        fecha_inicio__lte=today,
        fecha_fin__gte=yesterday,
        estado=Justificacion.Estado.AUTORIZADO,
    ).values("personal_id", "fecha_inicio", "fecha_fin"):
        for d in date_range(max(item["fecha_inicio"], yesterday), min(item["fecha_fin"], today)):
            justificados.add((item["personal_id"], d))

    descansos = set()
    for item in DescansoMedico.objects.filter(
        fecha_inicio__lte=today,
        fecha_fin__gte=yesterday,
    ).values("personal_id", "fecha_inicio", "fecha_fin"):
        for d in date_range(max(item["fecha_inicio"], yesterday), min(item["fecha_fin"], today)):
            descansos.add((item["personal_id"], d))

    marcaciones = set(
        Marcacion.objects.filter(
            fecha_hora__date__gte=yesterday,
            fecha_hora__date__lte=today,
        ).values_list("personal_id", "fecha_hora__date")
    )

    excluidos = marcaciones | justificados | descansos

    notifications = []
    for personal in (
        Personal.objects
        .filter(estado=Personal.Estado.ACTIVO)
        .only("id", "nombres_completos", "numero_documento", "codigo_empleado")
        .order_by("nombres_completos")
    ):
        for target_day in (yesterday, today):
            if (personal.id, target_day) in excluidos:
                continue
            notifications.append({
                "personal_id": personal.id,
                "personal": personal.nombres_completos,
                "numero_documento": personal.numero_documento,
                "codigo_empleado": personal.codigo_empleado,
                "fecha": target_day.isoformat(),
                "tipo": "MARCACION_FALTANTE",
                "detalle": "Sin marcacion registrada ni sustento en el periodo monitoreado.",
            })

    return notifications
