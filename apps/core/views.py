import calendar
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth import authenticate, get_user_model
from django.db import models
from django.db import transaction
from django.utils.timezone import localdate, now
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Area,
    BoletaConcepto,
    BoletaMensual,
    Cargo,
    Categoria,
    DescansoMedico,
    DescargaMarcacion,
    Dispositivo,
    Empresa,
    Justificacion,
    LicenciaAgua,
    Marcacion,
    Personal,
    PersonalTurno,
    ReporteAsistenciaDiaria,
    ReporteConceptoPersonal,
    ReporteIncidenciaPersonal,
    ReportePersonalMensual,
    Sucursal,
    TipoDocumento,
    TipoSindicato,
    TipoTrabajador,
    Turno,
    TurnoBloqueHorario,
    UbicacionGeografica,
    UsuarioAgua,
)
from .biometric import BiometricConnectionError, probe_device_connection, read_attendance_logs, read_device_capacity
from .serializers import (
    AreaSerializer,
    BoletaConceptoSerializer,
    BoletaMensualSerializer,
    CargoSerializer,
    CategoriaSerializer,
    DescansoMedicoSerializer,
    DescargaMarcacionSerializer,
    DispositivoSerializer,
    EmpresaSerializer,
    JustificacionSerializer,
    LicenciaAguaSerializer,
    MarcacionSerializer,
    PersonalSerializer,
    PersonalTurnoSerializer,
    ReporteAsistenciaDiariaSerializer,
    ReporteConceptoPersonalSerializer,
    ReporteIncidenciaPersonalSerializer,
    ReportePersonalMensualSerializer,
    SucursalSerializer,
    TipoDocumentoSerializer,
    TipoSindicatoSerializer,
    TipoTrabajadorSerializer,
    TurnoBloqueHorarioSerializer,
    TurnoSerializer,
    UbicacionGeograficaSerializer,
    UsuarioAguaSerializer,
    UserSerializer,
)


User = get_user_model()

MONTH_LABELS = (
    "",
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)


def _decimal(value):
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    try:
        return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal("0.00")


def _decimal_str(value):
    return f"{_decimal(value):.2f}"


def _resolve_boleta_profile(personal):
    tipo_codigo = (personal.tipo_trabajador.codigo or "").strip().upper() if personal.tipo_trabajador_id else ""
    tipo_desc = (personal.tipo_trabajador.descripcion or "").strip().upper() if personal.tipo_trabajador_id else ""
    categoria_codigo = (personal.categoria.codigo or "").strip().upper() if personal.categoria_id else ""
    categoria_desc = (personal.categoria.descripcion or "").strip().upper() if personal.categoria_id else ""
    source = " ".join(filter(None, [tipo_codigo, tipo_desc, categoria_codigo, categoria_desc]))

    profile = {
        "tipo_codigo": tipo_codigo,
        "tipo_label": personal.tipo_trabajador.descripcion if personal.tipo_trabajador_id else "",
        "ingreso_principal": "REMUNERACION MENSUAL",
        "regimen_pensionario": personal.categoria.descripcion if personal.categoria_id else "NO REGISTRA",
        "aporte_empleador_concepto": "ESSALUD",
        "aporte_empleador_rate": Decimal("0.09"),
        "aporte_trabajador_label": "",
        "aporte_trabajador_rate": Decimal("0.00"),
    }

    if "CAS" in source:
        profile.update(
            {
                "ingreso_principal": "RETRIBUCION CONTRATACION ADM SERVICIOS",
                "regimen_pensionario": "PENSION - ONP" if "ONP" in source or "19990" in source else profile["regimen_pensionario"],
            }
        )
    elif "276" in source:
        profile.update(
            {
                "ingreso_principal": "REMUNERACION BASICA D.L. 276",
                "regimen_pensionario": "SISTEMA PUBLICO" if profile["regimen_pensionario"] == "NO REGISTRA" else profile["regimen_pensionario"],
            }
        )
    elif "728" in source:
        profile.update(
            {
                "ingreso_principal": "REMUNERACION BASICA D.L. 728",
                "regimen_pensionario": "REGIMEN PRIVADO" if profile["regimen_pensionario"] == "NO REGISTRA" else profile["regimen_pensionario"],
            }
        )
    elif any(word in source for word in ("LOCACION", "SERVICIO", "HONORARIO")):
        profile.update(
            {
                "ingreso_principal": "HONORARIOS POR SERVICIOS",
                "regimen_pensionario": "SIN REGIMEN EN PLANILLA",
                "aporte_empleador_concepto": "",
                "aporte_empleador_rate": Decimal("0.00"),
            }
        )

    if any(word in source for word in ("ONP", "19990")):
        profile.update(
            {
                "aporte_trabajador_label": "SISTEMA NAC. DE PENSIONES D.L. 19990",
                "aporte_trabajador_rate": Decimal("0.13"),
                "regimen_pensionario": "SNP - ONP",
            }
        )
    elif "AFP" in source:
        profile.update(
            {
                "aporte_trabajador_label": "APORTE AFP",
                "aporte_trabajador_rate": Decimal("0.10"),
                "regimen_pensionario": "SPP - AFP",
            }
        )

    return profile


def _build_boleta_detalle(
    *,
    personal,
    boleta,
    anio,
    mes,
    dias_con_marcacion,
    dias_justificados,
    dias_descanso,
    faltas,
):
    conceptos = list(boleta.conceptos.all().order_by("tipo", "concepto", "id")) if boleta else []
    profile = _resolve_boleta_profile(personal)
    ingresos = []
    descuentos = []
    aportes_trabajador = []
    aportes_empleador = []

    for item in conceptos:
        row = {
            "codigo": f"{'I' if item.tipo == BoletaConcepto.Tipo.INGRESO else 'D'}{item.id:03d}",
            "concepto": item.concepto,
            "monto": _decimal_str(item.monto),
        }
        if item.tipo == BoletaConcepto.Tipo.INGRESO:
            ingresos.append(row)
            continue

        concepto_upper = item.concepto.upper()
        if any(word in concepto_upper for word in ("ONP", "AFP", "PENSION", "RETENCION")):
            row["codigo"] = f"AT{item.id:03d}"
            aportes_trabajador.append(row)
        else:
            descuentos.append(row)

    if boleta and not ingresos:
        ingresos.append(
            {
                "codigo": "I001",
                "concepto": profile["ingreso_principal"],
                "monto": _decimal_str(boleta.sueldo_base),
            }
        )

    total_ingresos = _decimal(boleta.total_ingresos if boleta else 0)
    if total_ingresos > 0 and not aportes_trabajador and profile["aporte_trabajador_rate"] > 0:
        aportes_trabajador.append(
            {
                "codigo": "AT001",
                "concepto": profile["aporte_trabajador_label"],
                "monto": _decimal_str(total_ingresos * profile["aporte_trabajador_rate"]),
            }
        )

    if total_ingresos > 0 and profile["aporte_empleador_rate"] > 0 and profile["aporte_empleador_concepto"]:
        aportes_empleador.append(
            {
                "codigo": "AE001",
                "concepto": profile["aporte_empleador_concepto"],
                "monto": _decimal_str(total_ingresos * profile["aporte_empleador_rate"]),
            }
        )

    situacion = "ACTIVO"
    if dias_descanso:
        situacion = "ACTIVO O SUBSIDIADO"

    dias_trabajados = max(len(dias_con_marcacion) + len(dias_justificados), 0)
    total_horas = len(dias_con_marcacion) * 8
    meses_label = MONTH_LABELS[mes] if 0 < mes < len(MONTH_LABELS) else str(mes)

    return {
        "periodo_texto": f"{meses_label} {anio}",
        "periodo_corto": f"{mes:02d}/{anio}",
        "numero_orden": f"{anio}{mes:02d}-{personal.id:05d}",
        "documento_identidad": {
            "tipo": personal.tipo_documento.descripcion if personal.tipo_documento_id else "Documento",
            "numero": personal.numero_documento,
        },
        "laboral": {
            "fecha_ingreso": personal.fecha_ingreso.isoformat() if personal.fecha_ingreso else "",
            "tipo_trabajador": profile["tipo_label"],
            "regimen_pensionario": profile["regimen_pensionario"],
            "cuspp": personal.codigo_empleado or "",
            "situacion": situacion,
        },
        "asistencia": {
            "dias_laborados": dias_trabajados,
            "dias_no_laborados": len(faltas),
            "dias_subsidiados": len(dias_descanso),
            "condicion": "Jornada Ordinaria",
            "total_horas": total_horas,
            "total_minutos": 0,
            "sobretiempo_horas": 0,
            "sobretiempo_minutos": 0,
        },
        "suspension_laboral": {
            "tipo": "DESCANSO MEDICO" if dias_descanso else ("JUSTIFICACION" if dias_justificados else ""),
            "motivo": "Con registro en el periodo" if (dias_descanso or dias_justificados) else "Sin novedades",
            "dias": max(len(dias_descanso), len(dias_justificados)),
        },
        "otros_empleadores": "No tiene",
        "conceptos": {
            "ingresos": ingresos,
            "descuentos": descuentos,
            "aportes_trabajador": aportes_trabajador,
            "aportes_empleador": aportes_empleador,
        },
    }


def _build_reporte_general_payload(personal, anio, mes):
    if mes < 1 or mes > 12:
        raise ValueError("mes debe estar entre 1 y 12.")

    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, ultimo_dia)

    boleta = (
        BoletaMensual.objects.filter(personal=personal, anio=anio, mes=mes)
        .prefetch_related("conceptos")
        .order_by("-created_at")
        .first()
    )
    conceptos = list(boleta.conceptos.all().order_by("tipo", "concepto", "id")) if boleta else []
    justificaciones = list(
        Justificacion.objects.filter(
            personal=personal,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio,
        ).order_by("fecha_inicio", "id")
    )
    descansos = list(
        DescansoMedico.objects.filter(
            personal=personal,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio,
        ).order_by("fecha_inicio", "id")
    )
    marcaciones = list(
        Marcacion.objects.filter(
            personal=personal,
            fecha_hora__date__gte=fecha_inicio,
            fecha_hora__date__lte=fecha_fin + timedelta(days=1),
        ).order_by("fecha_hora", "id")
    )
    asignaciones_turno = list(
        PersonalTurno.objects.select_related("turno")
        .prefetch_related("turno__bloques")
        .filter(
            personal=personal,
            fecha_inicio__lte=fecha_fin,
        )
        .filter(models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=fecha_inicio))
        .order_by("-fecha_inicio", "-id")
    )

    dias_justificados = set()
    dias_descanso = set()
    justificadas_por_dia = {}
    descansos_por_dia = {}
    marcaciones_por_dia = {}

    for item in justificaciones:
        start = max(item.fecha_inicio, fecha_inicio)
        end = min(item.fecha_fin, fecha_fin)
        current = start
        while current <= end:
            if item.estado == Justificacion.Estado.AUTORIZADO:
                dias_justificados.add(current)
                justificadas_por_dia.setdefault(current, []).append(item)
            current += timedelta(days=1)

    for item in descansos:
        start = max(item.fecha_inicio, fecha_inicio)
        end = min(item.fecha_fin, fecha_fin)
        current = start
        while current <= end:
            dias_descanso.add(current)
            descansos_por_dia.setdefault(current, []).append(item)
            current += timedelta(days=1)

    for item in marcaciones:
        day = item.fecha_hora.date()
        marcaciones_por_dia.setdefault(day, []).append(item)

    dias = []
    faltas = []
    total_horas_trabajadas = Decimal("0.00")
    total_horas_extra = Decimal("0.00")
    total_minutos_tardanza = 0

    def _assignment_for_day(current_day):
        active = next(
            (
                item
                for item in asignaciones_turno
                if item.fecha_inicio <= current_day and (item.fecha_fin is None or item.fecha_fin >= current_day)
            ),
            None,
        )
        if active is not None:
            return active

        # Si el trabajador solo tiene una asignacion o la fecha queda fuera de su vigencia,
        # usamos el turno mas cercano del periodo para no dejar el reporte mensual sin bloques.
        previous_assignment = next(
            (
                item
                for item in asignaciones_turno
                if item.fecha_inicio <= current_day
            ),
            None,
        )
        if previous_assignment is not None:
            return previous_assignment

        return asignaciones_turno[-1] if asignaciones_turno else None

    for offset in range(ultimo_dia):
        current = fecha_inicio + timedelta(days=offset)
        marks = marcaciones_por_dia.get(current, [])
        entradas = [item for item in marks if item.tipo_evento == Marcacion.TipoEvento.ENTRADA]
        salidas = [item for item in marks if item.tipo_evento == Marcacion.TipoEvento.SALIDA]
        active_assignment = _assignment_for_day(current)
        bloques_turno = list(active_assignment.turno.bloques.all().order_by("orden")) if active_assignment else []

        estado_dia = ReporteAsistenciaDiaria.EstadoDia.FALTA
        if current in dias_descanso:
            estado_dia = ReporteAsistenciaDiaria.EstadoDia.DESCANSO_MEDICO
        elif current in dias_justificados:
            estado_dia = ReporteAsistenciaDiaria.EstadoDia.JUSTIFICADO
        elif marks:
            estado_dia = ReporteAsistenciaDiaria.EstadoDia.ASISTIO

        if estado_dia == ReporteAsistenciaDiaria.EstadoDia.FALTA and not bloques_turno:
            faltas.append(current.isoformat())
        blocks_to_render = bloques_turno or [None]
        if estado_dia == ReporteAsistenciaDiaria.EstadoDia.FALTA and blocks_to_render != [None]:
            faltas.append(current.isoformat())

        for block_index, block in enumerate(blocks_to_render, start=1):
            entrada_mark = entradas[block_index - 1].fecha_hora.time() if len(entradas) >= block_index else None
            salida_mark = salidas[block_index - 1].fecha_hora.time() if len(salidas) >= block_index else None
            horas_trabajadas = Decimal("0.00")
            if len(entradas) >= block_index and len(salidas) >= block_index:
                start_dt = entradas[block_index - 1].fecha_hora
                end_dt = salidas[block_index - 1].fecha_hora
                if end_dt > start_dt:
                    horas_trabajadas = _decimal((end_dt - start_dt).total_seconds() / 3600)

            total_horas_trabajadas += horas_trabajadas
            dias.append(
                {
                    "fecha": current.isoformat(),
                    "bloque_orden": block.orden if block else block_index,
                    "estado_dia": estado_dia,
                    "hora_entrada_programada": block.hora_entrada.isoformat() if block else None,
                    "hora_salida_programada": block.hora_salida.isoformat() if block else None,
                    "hora_entrada_real": entrada_mark.isoformat() if entrada_mark else None,
                    "hora_salida_real": salida_mark.isoformat() if salida_mark else None,
                    "minutos_tardanza": 0,
                    "horas_trabajadas": _decimal_str(horas_trabajadas),
                    "horas_extra": "0.00",
                    "observacion": "",
                    "marcaciones": [
                        {
                            "id": item.id,
                            "fecha_hora": item.fecha_hora.isoformat(),
                            "tipo_evento": item.tipo_evento,
                        }
                        for item in marks
                    ],
                }
            )

    boleta_detalle = _build_boleta_detalle(
        personal=personal,
        boleta=boleta,
        anio=anio,
        mes=mes,
        dias_con_marcacion=set(marcaciones_por_dia.keys()),
        dias_justificados=dias_justificados,
        dias_descanso=dias_descanso,
        faltas=faltas,
    )

    conceptos_reporte = []
    concept_order = 1
    concept_groups = [
        ("INGRESO", boleta_detalle["conceptos"]["ingresos"]),
        ("DESCUENTO", boleta_detalle["conceptos"]["descuentos"]),
        ("APORTE_TRABAJADOR", boleta_detalle["conceptos"]["aportes_trabajador"]),
        ("APORTE_EMPLEADOR", boleta_detalle["conceptos"]["aportes_empleador"]),
    ]
    for tipo, items in concept_groups:
        for item in items:
            conceptos_reporte.append(
                {
                    "tipo": tipo,
                    "codigo": item["codigo"],
                    "concepto": item["concepto"],
                    "monto": item["monto"],
                    "orden": concept_order,
                }
            )
            concept_order += 1

    incidencias = []
    for item in justificaciones:
        incidencias.append(
            {
                "tipo": ReporteIncidenciaPersonal.Tipo.JUSTIFICACION,
                "fecha_inicio": item.fecha_inicio.isoformat(),
                "fecha_fin": item.fecha_fin.isoformat(),
                "cantidad_dias": item.dias,
                "cantidad_minutos": 0,
                "referencia_modelo": "Justificacion",
                "referencia_id": item.id,
                "descripcion": item.motivo,
                "observacion": item.estado,
            }
        )
    for item in descansos:
        incidencias.append(
            {
                "tipo": ReporteIncidenciaPersonal.Tipo.DESCANSO_MEDICO,
                "fecha_inicio": item.fecha_inicio.isoformat(),
                "fecha_fin": item.fecha_fin.isoformat(),
                "cantidad_dias": item.dias,
                "cantidad_minutos": 0,
                "referencia_modelo": "DescansoMedico",
                "referencia_id": item.id,
                "descripcion": item.motivo,
                "observacion": item.citt,
            }
        )
    for item in faltas:
        incidencias.append(
            {
                "tipo": ReporteIncidenciaPersonal.Tipo.FALTA,
                "fecha_inicio": item,
                "fecha_fin": item,
                "cantidad_dias": 1,
                "cantidad_minutos": 0,
                "referencia_modelo": "",
                "referencia_id": None,
                "descripcion": "Falta sin marcacion ni sustento",
                "observacion": "",
            }
        )

    payload = {
        "personal": {
            "id": personal.id,
            "codigo_empleado": personal.codigo_empleado,
            "numero_documento": personal.numero_documento,
            "nombres_completos": personal.nombres_completos,
            "empresa": {
                "id": personal.empresa_id,
                "razon_social": personal.empresa.razon_social if personal.empresa_id else "",
                "ruc": personal.empresa.ruc if personal.empresa_id else "",
            },
            "sucursal_nombre": personal.sucursal.nombre if personal.sucursal_id else "",
            "area_nombre": personal.area.nombre if personal.area_id else "",
            "tipo_trabajador_codigo": personal.tipo_trabajador.codigo if personal.tipo_trabajador_id else "",
            "tipo_trabajador": personal.tipo_trabajador.descripcion if personal.tipo_trabajador_id else "",
            "categoria_codigo": personal.categoria.codigo if personal.categoria_id else "",
            "categoria": personal.categoria.descripcion if personal.categoria_id else "",
            "cargo": personal.cargo.descripcion if personal.cargo_id else "",
        },
        "periodo": {
            "anio": anio,
            "mes": mes,
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "etiqueta": f"{MONTH_LABELS[mes]} {anio}",
            "etiqueta_corta": f"{mes:02d}/{anio}",
        },
        "reporte": {
            "sueldo_base": _decimal_str(boleta.sueldo_base if boleta else 0),
            "total_ingresos": _decimal_str(boleta.total_ingresos if boleta else 0),
            "total_descuentos": _decimal_str(boleta.total_descuentos if boleta else 0),
            "neto_pagar": _decimal_str(boleta.neto_pagar if boleta else 0),
            "total_dias_periodo": ultimo_dia,
            "total_dias_laborados": sum(
                1 for item in dias if item["estado_dia"] == ReporteAsistenciaDiaria.EstadoDia.ASISTIO
            ),
            "total_dias_falta": len(faltas),
            "total_dias_justificados": len(dias_justificados),
            "total_dias_descanso_medico": len(dias_descanso),
            "total_minutos_tardanza": total_minutos_tardanza,
            "total_horas_trabajadas": _decimal_str(total_horas_trabajadas),
            "total_horas_extra": _decimal_str(total_horas_extra),
            "estado": ReportePersonalMensual.Estado.GENERADO,
        },
        "dias": dias,
        "conceptos": conceptos_reporte,
        "incidencias": incidencias,
        "boleta_detalle": boleta_detalle,
    }
    return payload


def _sync_reporte_general(personal, anio, mes):
    payload = _build_reporte_general_payload(personal, anio, mes)

    with transaction.atomic():
        reporte, _ = ReportePersonalMensual.objects.update_or_create(
            personal=personal,
            anio=anio,
            mes=mes,
            defaults={
                "fecha_inicio": date.fromisoformat(payload["periodo"]["fecha_inicio"]),
                "fecha_fin": date.fromisoformat(payload["periodo"]["fecha_fin"]),
                "sueldo_base": payload["reporte"]["sueldo_base"],
                "total_ingresos": payload["reporte"]["total_ingresos"],
                "total_descuentos": payload["reporte"]["total_descuentos"],
                "neto_pagar": payload["reporte"]["neto_pagar"],
                "total_dias_periodo": payload["reporte"]["total_dias_periodo"],
                "total_dias_laborados": payload["reporte"]["total_dias_laborados"],
                "total_dias_falta": payload["reporte"]["total_dias_falta"],
                "total_dias_justificados": payload["reporte"]["total_dias_justificados"],
                "total_dias_descanso_medico": payload["reporte"]["total_dias_descanso_medico"],
                "total_minutos_tardanza": payload["reporte"]["total_minutos_tardanza"],
                "total_horas_trabajadas": payload["reporte"]["total_horas_trabajadas"],
                "total_horas_extra": payload["reporte"]["total_horas_extra"],
                "estado": payload["reporte"]["estado"],
                "observacion": "Generado automaticamente desde marcaciones, boletas e incidencias.",
            },
        )

        ReporteAsistenciaDiaria.objects.filter(reporte=reporte).delete()
        ReporteConceptoPersonal.objects.filter(reporte=reporte).delete()
        ReporteIncidenciaPersonal.objects.filter(reporte=reporte).delete()

        ReporteAsistenciaDiaria.objects.bulk_create(
            [
                ReporteAsistenciaDiaria(
                    reporte=reporte,
                    fecha=date.fromisoformat(item["fecha"]),
                    bloque_orden=item["bloque_orden"],
                    estado_dia=item["estado_dia"],
                    hora_entrada_programada=time.fromisoformat(item["hora_entrada_programada"]) if item["hora_entrada_programada"] else None,
                    hora_salida_programada=time.fromisoformat(item["hora_salida_programada"]) if item["hora_salida_programada"] else None,
                    hora_entrada_real=time.fromisoformat(item["hora_entrada_real"]) if item["hora_entrada_real"] else None,
                    hora_salida_real=time.fromisoformat(item["hora_salida_real"]) if item["hora_salida_real"] else None,
                    minutos_tardanza=item["minutos_tardanza"],
                    horas_trabajadas=item["horas_trabajadas"],
                    horas_extra=item["horas_extra"],
                    observacion=item["observacion"],
                )
                for item in payload["dias"]
            ]
        )

        if payload["conceptos"]:
            ReporteConceptoPersonal.objects.bulk_create(
                [
                    ReporteConceptoPersonal(
                        reporte=reporte,
                        tipo=item["tipo"],
                        codigo=item["codigo"],
                        concepto=item["concepto"],
                        monto=item["monto"],
                        orden=item["orden"],
                    )
                    for item in payload["conceptos"]
                ]
            )

        if payload["incidencias"]:
            ReporteIncidenciaPersonal.objects.bulk_create(
                [
                    ReporteIncidenciaPersonal(
                        reporte=reporte,
                        tipo=item["tipo"],
                        fecha_inicio=date.fromisoformat(item["fecha_inicio"]),
                        fecha_fin=date.fromisoformat(item["fecha_fin"]),
                        cantidad_dias=item["cantidad_dias"],
                        cantidad_minutos=item["cantidad_minutos"],
                        referencia_modelo=item["referencia_modelo"],
                        referencia_id=item["referencia_id"],
                        descripcion=item["descripcion"],
                        observacion=item["observacion"],
                    )
                    for item in payload["incidencias"]
                ]
            )

    payload["reporte"]["id"] = reporte.id
    return payload


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response(
        {
            "name": "Sistema Biometrico API",
            "version": "1.0.0",
            "health": request.build_absolute_uri("health/"),
            "auth_login": request.build_absolute_uri("auth/login/"),
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response(
        {
            "status": "ok",
            "service": "backend-django",
            "timestamp": now().isoformat(),
        }
    )


def build_missing_mark_notifications():
    today = localdate()
    justified_ids = set(
        Justificacion.objects.filter(
            fecha_inicio__lte=today,
            fecha_fin__gte=today,
            estado=Justificacion.Estado.AUTORIZADO,
        ).values_list("personal_id", flat=True)
    )
    medical_leave_ids = set(
        DescansoMedico.objects.filter(
            fecha_inicio__lte=today,
            fecha_fin__gte=today,
        ).values_list("personal_id", flat=True)
    )
    excluded_personal_ids = justified_ids | medical_leave_ids

    assignments = (
        PersonalTurno.objects.select_related("personal", "turno", "personal__area", "personal__sucursal")
        .prefetch_related("turno__bloques")
        .filter(fecha_inicio__lte=today, turno__activo=True, personal__estado=Personal.Estado.ACTIVO)
        .filter(models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=today))
        .exclude(personal_id__in=excluded_personal_ids)
        .order_by("personal_id", "-fecha_inicio", "-id")
    )

    active_assignments = {}
    for assignment in assignments:
        if assignment.personal_id not in active_assignments:
            active_assignments[assignment.personal_id] = assignment

    if not active_assignments:
        return {
            "fecha": today.isoformat(),
            "total": 0,
            "items": [],
        }

    marks_by_personal = {}
    for row in (
        Marcacion.objects.filter(
            personal_id__in=active_assignments.keys(),
            situacion=Marcacion.Situacion.ACTIVO,
            fecha_hora__date=today,
        )
        .values("personal_id", "tipo_evento")
    ):
        personal_id = row["personal_id"]
        if personal_id not in marks_by_personal:
            marks_by_personal[personal_id] = {
                Marcacion.TipoEvento.ENTRADA: 0,
                Marcacion.TipoEvento.SALIDA: 0,
            }
        marks_by_personal[personal_id][row["tipo_evento"]] += 1

    items = []
    for assignment in active_assignments.values():
        if assignment.turno.tipo == Turno.Tipo.DESCANSO:
            continue

        blocks = list(assignment.turno.bloques.all())
        if not blocks:
            continue

        counts = marks_by_personal.get(
            assignment.personal_id,
            {
                Marcacion.TipoEvento.ENTRADA: 0,
                Marcacion.TipoEvento.SALIDA: 0,
            },
        )
        entry_marks = int(counts.get(Marcacion.TipoEvento.ENTRADA, 0))
        exit_marks = int(counts.get(Marcacion.TipoEvento.SALIDA, 0))

        missing_slots = []
        for index, block in enumerate(blocks, start=1):
            if index > entry_marks:
                missing_slots.append(
                    {
                        "tipo": Marcacion.TipoEvento.ENTRADA,
                        "label": f"Entrada {index}",
                        "hora": block.hora_entrada.strftime("%H:%M"),
                    }
                )
            if index > exit_marks:
                missing_slots.append(
                    {
                        "tipo": Marcacion.TipoEvento.SALIDA,
                        "label": f"Salida {index}",
                        "hora": block.hora_salida.strftime("%H:%M"),
                    }
                )

        if not missing_slots:
            continue

        items.append(
            {
                "personal_id": assignment.personal_id,
                "personal_nombre": assignment.personal.nombres_completos,
                "numero_documento": assignment.personal.numero_documento,
                "sucursal": assignment.personal.sucursal.nombre,
                "area": assignment.personal.area.nombre,
                "turno": assignment.turno.nombre,
                "fecha": today.isoformat(),
                "total_esperadas": len(blocks) * 2,
                "total_registradas": min(entry_marks, len(blocks)) + min(exit_marks, len(blocks)),
                "total_faltantes": len(missing_slots),
                "faltantes": missing_slots,
            }
        )

    items.sort(key=lambda item: (-item["total_faltantes"], item["personal_nombre"]))
    return {
        "fecha": today.isoformat(),
        "total": len(items),
        "items": items,
    }


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""

        if not username or not password:
            return Response(
                {"detail": "username y password son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_obj = User.objects.filter(username__iexact=username).first() or User.objects.filter(
            email__iexact=username
        ).first()
        auth_username = user_obj.username if user_obj else username
        user = authenticate(request, username=auth_username, password=password)

        if not user:
            return Response(
                {"detail": "Credenciales invalidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]


class UsuarioViewSet(BaseModelViewSet):
    queryset = User.objects.prefetch_related("module_permissions").all().order_by("username")
    serializer_class = UserSerializer


class EmpresaViewSet(BaseModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer


class SucursalViewSet(BaseModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer


class AreaViewSet(BaseModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer


class CargoViewSet(BaseModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer


class TipoTrabajadorViewSet(BaseModelViewSet):
    queryset = TipoTrabajador.objects.all()
    serializer_class = TipoTrabajadorSerializer


class CategoriaViewSet(BaseModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class TipoDocumentoViewSet(BaseModelViewSet):
    queryset = TipoDocumento.objects.all()
    serializer_class = TipoDocumentoSerializer


class TipoSindicatoViewSet(BaseModelViewSet):
    queryset = TipoSindicato.objects.all()
    serializer_class = TipoSindicatoSerializer


class UbicacionGeograficaViewSet(BaseModelViewSet):
    queryset = UbicacionGeografica.objects.all()
    serializer_class = UbicacionGeograficaSerializer


class PersonalViewSet(BaseModelViewSet):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer

    @action(detail=True, methods=["get"], url_path="resumen-planilla")
    def resumen_planilla(self, request, pk=None):
        personal = (
            Personal.objects.select_related(
                "empresa",
                "sucursal",
                "area",
                "tipo_documento",
                "tipo_trabajador",
                "categoria",
                "cargo",
            )
            .filter(pk=pk)
            .first()
        )
        if personal is None:
            return Response({"detail": "Personal no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        try:
            anio = int(request.query_params.get("anio") or now().year)
            mes = int(request.query_params.get("mes") or now().month)
        except (TypeError, ValueError):
            return Response(
                {"detail": "anio y mes deben ser numericos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if mes < 1 or mes > 12:
            return Response({"detail": "mes debe estar entre 1 y 12."}, status=status.HTTP_400_BAD_REQUEST)

        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fecha_inicio = date(anio, mes, 1)
        fecha_fin = date(anio, mes, ultimo_dia)

        boleta = (
            BoletaMensual.objects.filter(personal=personal, anio=anio, mes=mes)
            .prefetch_related("conceptos")
            .order_by("-created_at")
            .first()
        )
        conceptos = list(boleta.conceptos.all().order_by("tipo", "concepto", "id")) if boleta else []
        justificaciones = list(
            Justificacion.objects.filter(
                personal=personal,
                fecha_inicio__lte=fecha_fin,
                fecha_fin__gte=fecha_inicio,
            ).order_by("fecha_inicio", "id")
        )
        descansos = list(
            DescansoMedico.objects.filter(
                personal=personal,
                fecha_inicio__lte=fecha_fin,
                fecha_fin__gte=fecha_inicio,
            ).order_by("fecha_inicio", "id")
        )
        marcaciones = list(
            Marcacion.objects.filter(
                personal=personal,
                fecha_hora__date__gte=fecha_inicio,
                fecha_hora__date__lte=fecha_fin,
            ).order_by("fecha_hora", "id")
        )

        dias_con_marcacion = {item.fecha_hora.date() for item in marcaciones}
        dias_justificados = set()
        dias_descanso = set()

        for item in justificaciones:
            start = max(item.fecha_inicio, fecha_inicio)
            end = min(item.fecha_fin, fecha_fin)
            current = start
            while current <= end:
                if item.estado == Justificacion.Estado.AUTORIZADO:
                    dias_justificados.add(current)
                current += timedelta(days=1)

        for item in descansos:
            start = max(item.fecha_inicio, fecha_inicio)
            end = min(item.fecha_fin, fecha_fin)
            current = start
            while current <= end:
                dias_descanso.add(current)
                current += timedelta(days=1)

        faltas = []
        for offset in range(ultimo_dia):
            current = fecha_inicio + timedelta(days=offset)
            if current in dias_con_marcacion or current in dias_justificados or current in dias_descanso:
                continue
            faltas.append(current.isoformat())

        resumen = {
            "personal": {
                "id": personal.id,
                "codigo_empleado": personal.codigo_empleado,
                "numero_documento": personal.numero_documento,
                "nombres_completos": personal.nombres_completos,
                "empresa": {
                    "id": personal.empresa_id,
                    "razon_social": personal.empresa.razon_social if personal.empresa_id else "",
                    "ruc": personal.empresa.ruc if personal.empresa_id else "",
                },
                "sucursal": personal.sucursal_id,
                "sucursal_nombre": personal.sucursal.nombre if personal.sucursal_id else "",
                "area": personal.area_id,
                "area_nombre": personal.area.nombre if personal.area_id else "",
                "tipo_documento": personal.tipo_documento.descripcion if personal.tipo_documento_id else "",
                "tipo_trabajador_codigo": personal.tipo_trabajador.codigo if personal.tipo_trabajador_id else "",
                "tipo_trabajador": personal.tipo_trabajador.descripcion if personal.tipo_trabajador_id else "",
                "categoria_codigo": personal.categoria.codigo if personal.categoria_id else "",
                "categoria": personal.categoria.descripcion if personal.categoria_id else "",
                "cargo": personal.cargo.descripcion if personal.cargo_id else "",
                "fecha_ingreso": personal.fecha_ingreso.isoformat() if personal.fecha_ingreso else "",
            },
            "periodo": {
                "anio": anio,
                "mes": mes,
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat(),
                "etiqueta": f"{MONTH_LABELS[mes]} {anio}",
                "etiqueta_corta": f"{mes:02d}/{anio}",
            },
            "boleta": {
                "id": boleta.id if boleta else None,
                "sueldo_base": str(boleta.sueldo_base) if boleta else "0.00",
                "total_ingresos": str(boleta.total_ingresos) if boleta else "0.00",
                "total_descuentos": str(boleta.total_descuentos) if boleta else "0.00",
                "neto_pagar": str(boleta.neto_pagar) if boleta else "0.00",
                "estado": boleta.estado if boleta else "NO_GENERADA",
                "conceptos": [
                    {
                        "id": item.id,
                        "tipo": item.tipo,
                        "concepto": item.concepto,
                        "monto": str(item.monto),
                    }
                    for item in conceptos
                ],
            },
            "boleta_detalle": _build_boleta_detalle(
                personal=personal,
                boleta=boleta,
                anio=anio,
                mes=mes,
                dias_con_marcacion=dias_con_marcacion,
                dias_justificados=dias_justificados,
                dias_descanso=dias_descanso,
                faltas=faltas,
            ),
            "resumen": {
                "dias_periodo": ultimo_dia,
                "dias_con_marcacion": len(dias_con_marcacion),
                "dias_justificados": len(dias_justificados),
                "dias_descanso_medico": len(dias_descanso),
                "dias_falta": len(faltas),
            },
            "faltas": faltas,
            "justificaciones": [
                {
                    "id": item.id,
                    "motivo": item.motivo,
                    "estado": item.estado,
                    "tipo": item.tipo,
                    "fecha_inicio": item.fecha_inicio.isoformat(),
                    "fecha_fin": item.fecha_fin.isoformat(),
                    "dias": item.dias,
                    "nombre_documento": item.nombre_documento,
                }
                for item in justificaciones
            ],
            "descansos_medicos": [
                {
                    "id": item.id,
                    "motivo": item.motivo,
                    "fecha_inicio": item.fecha_inicio.isoformat(),
                    "fecha_fin": item.fecha_fin.isoformat(),
                    "dias": item.dias,
                    "citt": item.citt,
                    "diagnostico": item.diagnostico,
                }
                for item in descansos
            ],
            "marcaciones": [
                {
                    "id": item.id,
                    "fecha_hora": item.fecha_hora.isoformat(),
                    "tipo_evento": item.tipo_evento,
                    "codigo_equipo": item.codigo_equipo,
                }
                for item in marcaciones
            ],
        }
        return Response(resumen)

    @action(detail=True, methods=["get"], url_path="reporte-general")
    def reporte_general(self, request, pk=None):
        personal = (
            Personal.objects.select_related(
                "empresa",
                "sucursal",
                "area",
                "tipo_documento",
                "tipo_trabajador",
                "categoria",
                "cargo",
            )
            .filter(pk=pk)
            .first()
        )
        if personal is None:
            return Response({"detail": "Personal no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            anio = int(request.query_params.get("anio") or now().year)
            mes = int(request.query_params.get("mes") or now().month)
        except (TypeError, ValueError):
            return Response(
                {"detail": "anio y mes deben ser numericos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = _sync_reporte_general(personal, anio, mes)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(payload)


class TurnoViewSet(BaseModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer


class TurnoBloqueHorarioViewSet(BaseModelViewSet):
    queryset = TurnoBloqueHorario.objects.all()
    serializer_class = TurnoBloqueHorarioSerializer


class PersonalTurnoViewSet(BaseModelViewSet):
    queryset = PersonalTurno.objects.all()
    serializer_class = PersonalTurnoSerializer


class DispositivoViewSet(BaseModelViewSet):
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer

    @action(detail=False, methods=["post"], url_path="probar-conexion")
    def probar_conexion(self, request):
        try:
            password = int(request.data.get("clave_comunicacion") or 0)
        except (TypeError, ValueError):
            return Response(
                {"detail": "La clave de comunicacion debe ser numerica."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dispositivo_id = request.data.get("dispositivo_id")
        host = ""
        port = 4370
        nombre = ""

        if dispositivo_id:
            try:
                dispositivo = Dispositivo.objects.get(pk=int(dispositivo_id))
            except (TypeError, ValueError, Dispositivo.DoesNotExist):
                return Response(
                    {"detail": "Dispositivo no encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            host = dispositivo.direccion
            port = dispositivo.puerto
            nombre = dispositivo.nombre
        else:
            host = (request.data.get("direccion") or "").strip()
            nombre = (request.data.get("nombre") or "").strip()
            try:
                port = int(request.data.get("puerto") or 4370)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "El puerto debe ser numerico."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not host:
            return Response(
                {"detail": "La direccion IP o dominio es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = probe_device_connection(host=host, port=port, password=password)
        except BiometricConnectionError as exc:
            return Response(
                {
                    "ok": False,
                    "estado": "error",
                    "nombre": nombre or host,
                    "host": host,
                    "port": port,
                    "detalle": str(exc),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "ok": True,
                "nombre": nombre or host,
                **result,
            }
        )


class DescargaMarcacionViewSet(BaseModelViewSet):
    queryset = DescargaMarcacion.objects.all()
    serializer_class = DescargaMarcacionSerializer

    @action(detail=False, methods=["get"], url_path="notificaciones-faltantes")
    def notificaciones_faltantes(self, request):
        return Response(build_missing_mark_notifications())

    @action(detail=False, methods=["post"], url_path="ver-capacidad-dispositivo")
    def ver_capacidad_dispositivo(self, request):
        raw_ids = request.data.get("dispositivo_ids") or []
        try:
            device_ids = [int(item) for item in raw_ids]
        except (TypeError, ValueError):
            return Response(
                {"detail": "dispositivo_ids debe ser una lista de enteros."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not device_ids:
            return Response(
                {"detail": "Selecciona al menos un dispositivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            password = int(request.data.get("clave_comunicacion") or 0)
        except (TypeError, ValueError):
            return Response(
                {"detail": "La clave de comunicacion debe ser numerica."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response(
                {"detail": "No se encontraron dispositivos activos para leer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resultados = []
        for dispositivo in dispositivos:
            try:
                capacidad = read_device_capacity(
                    host=dispositivo.direccion,
                    port=dispositivo.puerto,
                    password=password,
                )
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "estado": "ok",
                        "detalle": "Capacidad leida en modo solo lectura.",
                        **capacidad,
                    }
                )
            except BiometricConnectionError as exc:
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "estado": "error",
                        "detalle": str(exc),
                    }
                )

        return Response(
            {
                "procesados": len(dispositivos),
                "resultados": resultados,
            }
        )

    @action(detail=False, methods=["post"], url_path="ver-raw-dispositivo")
    def ver_raw_dispositivo(self, request):
        raw_ids = request.data.get("dispositivo_ids") or []
        try:
            device_ids = [int(item) for item in raw_ids]
        except (TypeError, ValueError):
            return Response(
                {"detail": "dispositivo_ids debe ser una lista de enteros."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not device_ids:
            return Response(
                {"detail": "Selecciona al menos un dispositivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            password = int(request.data.get("clave_comunicacion") or 0)
        except (TypeError, ValueError):
            return Response(
                {"detail": "La clave de comunicacion debe ser numerica."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fecha_inicio_raw = request.data.get("fecha_inicio")
        fecha_fin_raw = request.data.get("fecha_fin")
        fecha_inicio = None
        fecha_fin = None
        if fecha_inicio_raw:
            try:
                fecha_inicio = datetime.strptime(str(fecha_inicio_raw), "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "fecha_inicio debe tener formato YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if fecha_fin_raw:
            try:
                fecha_fin = datetime.strptime(str(fecha_fin_raw), "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "fecha_fin debe tener formato YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if fecha_inicio and not fecha_fin:
            fecha_fin = fecha_inicio
        if fecha_fin and not fecha_inicio:
            fecha_inicio = fecha_fin
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            return Response(
                {"detail": "fecha_inicio no puede ser mayor que fecha_fin."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response(
                {"detail": "No se encontraron dispositivos activos para leer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        personal_por_codigo = {
            str(item.codigo_empleado).strip(): item
            for item in Personal.objects.exclude(codigo_empleado="")
        }
        personal_por_documento = {
            str(item.numero_documento).strip(): item
            for item in Personal.objects.exclude(numero_documento="")
        }

        resultados = []
        raw_logs = []

        for dispositivo in dispositivos:
            try:
                logs = read_attendance_logs(
                    host=dispositivo.direccion,
                    port=dispositivo.puerto,
                    password=password,
                )
            except BiometricConnectionError as exc:
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "estado": "error",
                        "detalle": str(exc),
                        "leidos": 0,
                        "vinculados": 0,
                        "sin_personal": 0,
                    }
                )
                continue

            logs_filtrados = []
            for log in logs:
                log_date = log.timestamp.date()
                if fecha_inicio and log_date < fecha_inicio:
                    continue
                if fecha_fin and log_date > fecha_fin:
                    continue
                logs_filtrados.append(log)

            vinculados = 0
            sin_personal = 0
            for log in logs_filtrados:
                personal = personal_por_codigo.get(log.user_code) or personal_por_documento.get(log.user_code)
                estado = "SIN_PERSONAL"
                personal_id = None
                personal_documento = ""
                personal_nombre = ""
                if personal is not None:
                    estado = "VINCULADO"
                    personal_id = personal.id
                    personal_documento = personal.numero_documento
                    personal_nombre = personal.nombres_completos
                    vinculados += 1
                else:
                    sin_personal += 1

                raw_logs.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "user_code": log.user_code,
                        "timestamp": log.timestamp,
                        "punch": log.punch,
                        "tipo_evento": (
                            Marcacion.TipoEvento.SALIDA if log.punch in {1, 5} else Marcacion.TipoEvento.ENTRADA
                        ),
                        "estado": estado,
                        "personal_id": personal_id,
                        "personal_documento": personal_documento,
                        "personal_nombre": personal_nombre,
                        "equipo_nombre": log.device_user_name,
                        "equipo_raw": log.raw_data or {},
                    }
                )

            resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "estado": "ok",
                        "detalle": "Lectura RAW en modo solo lectura. No se guardo en base de datos.",
                        "leidos_equipo": len(logs),
                        "leidos": len(logs_filtrados),
                        "vinculados": vinculados,
                        "sin_personal": sin_personal,
                    }
                )

        return Response(
            {
                "procesados": len(dispositivos),
                "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
                "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
                "resultados": resultados,
                "raw_logs_total": len(raw_logs),
                "raw_logs": raw_logs,
            }
        )

    @action(detail=False, methods=["post"], url_path="descargar-dispositivo")
    def descargar_dispositivo(self, request):
        raw_ids = request.data.get("dispositivo_ids") or []
        try:
            device_ids = [int(item) for item in raw_ids]
        except (TypeError, ValueError):
            return Response(
                {"detail": "dispositivo_ids debe ser una lista de enteros."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not device_ids:
            return Response(
                {"detail": "Selecciona al menos un dispositivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            password = int(request.data.get("clave_comunicacion") or 0)
        except (TypeError, ValueError):
            return Response(
                {"detail": "La clave de comunicacion debe ser numerica."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response(
                {"detail": "No se encontraron dispositivos activos para descargar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resultados = []
        total_creadas = 0
        total_duplicadas = 0
        raw_logs = []
        periodos_a_sincronizar = set()
        personal_a_sincronizar = {}

        for dispositivo in dispositivos:
            try:
                logs = read_attendance_logs(
                    host=dispositivo.direccion,
                    port=dispositivo.puerto,
                    password=password,
                )
            except BiometricConnectionError as exc:
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "creadas": 0,
                        "duplicadas": 0,
                        "sin_personal": 0,
                        "estado": "error",
                        "detalle": str(exc),
                    }
                )
                continue

            personal_por_codigo = {
                str(item.codigo_empleado).strip(): item
                for item in Personal.objects.exclude(codigo_empleado="")
            }
            personal_por_documento = {
                str(item.numero_documento).strip(): item
                for item in Personal.objects.exclude(numero_documento="")
            }

            creadas = 0
            duplicadas = 0
            sin_personal = 0

            with transaction.atomic():
                descarga = DescargaMarcacion.objects.create(
                    dispositivo=dispositivo,
                    fuente=DescargaMarcacion.Fuente.DISPOSITIVO,
                    ejecutado_por=request.user,
                    observacion="Descarga en modo solo lectura desde dispositivo biometrico.",
                )

                for log in logs:
                    personal = personal_por_codigo.get(log.user_code) or personal_por_documento.get(log.user_code)
                    if personal is None:
                        raw_logs.append(
                            {
                                "dispositivo_id": dispositivo.id,
                                "dispositivo": dispositivo.nombre,
                                "user_code": log.user_code,
                                "timestamp": log.timestamp,
                                "punch": log.punch,
                                "tipo_evento": (
                                    Marcacion.TipoEvento.SALIDA if log.punch in {1, 5} else Marcacion.TipoEvento.ENTRADA
                                ),
                                "estado": "SIN_PERSONAL",
                                "personal_id": None,
                                "personal_documento": "",
                                "personal_nombre": "",
                                "equipo_nombre": log.device_user_name,
                                "equipo_raw": log.raw_data or {},
                            }
                        )
                        sin_personal += 1
                        continue

                    tipo_evento = (
                        Marcacion.TipoEvento.SALIDA
                        if log.punch in {1, 5}
                        else Marcacion.TipoEvento.ENTRADA
                    )
                    _, created = Marcacion.objects.get_or_create(
                        personal=personal,
                        fecha_hora=log.timestamp,
                        defaults={
                            "dispositivo": dispositivo,
                            "descarga": descarga,
                            "codigo_equipo": log.user_code,
                            "tipo_evento": tipo_evento,
                            "situacion": Marcacion.Situacion.ACTIVO,
                        },
                    )
                    if created:
                        creadas += 1
                        raw_logs.append(
                            {
                                "dispositivo_id": dispositivo.id,
                                "dispositivo": dispositivo.nombre,
                                "user_code": log.user_code,
                                "timestamp": log.timestamp,
                                "punch": log.punch,
                                "tipo_evento": tipo_evento,
                                "estado": "CREADA",
                                "personal_id": personal.id,
                                "personal_documento": personal.numero_documento,
                                "personal_nombre": personal.nombres_completos,
                                "equipo_nombre": log.device_user_name,
                                "equipo_raw": log.raw_data or {},
                            }
                        )
                        periodos_a_sincronizar.add((personal.id, log.timestamp.year, log.timestamp.month))
                        personal_a_sincronizar[personal.id] = personal
                    else:
                        duplicadas += 1
                        raw_logs.append(
                            {
                                "dispositivo_id": dispositivo.id,
                                "dispositivo": dispositivo.nombre,
                                "user_code": log.user_code,
                                "timestamp": log.timestamp,
                                "punch": log.punch,
                                "tipo_evento": tipo_evento,
                                "estado": "DUPLICADA",
                                "personal_id": personal.id,
                                "personal_documento": personal.numero_documento,
                                "personal_nombre": personal.nombres_completos,
                                "equipo_nombre": log.device_user_name,
                                "equipo_raw": log.raw_data or {},
                            }
                        )

                if creadas == 0 and duplicadas == 0 and sin_personal == 0:
                    descarga.observacion = "Descarga ejecutada sin marcaciones."
                elif creadas == 0 and duplicadas > 0 and sin_personal == 0:
                    descarga.observacion = "Descarga ejecutada. Todas las marcaciones ya existian."
                elif sin_personal > 0:
                    descarga.observacion = (
                        f"Descarga ejecutada. {sin_personal} marcaciones sin personal asociado."
                    )
                descarga.save(update_fields=["observacion"])

            total_creadas += creadas
            total_duplicadas += duplicadas
            resultados.append(
                {
                    "dispositivo_id": dispositivo.id,
                    "dispositivo": dispositivo.nombre,
                    "creadas": creadas,
                    "duplicadas": duplicadas,
                    "sin_personal": sin_personal,
                    "estado": "ok",
                    "detalle": "Lectura completada sin escribir en el reloj.",
                }
            )

        reportes_actualizados = 0
        for personal_id, anio, mes in sorted(periodos_a_sincronizar, key=lambda item: (item[1], item[2], item[0])):
            personal = personal_a_sincronizar.get(personal_id)
            if personal is None:
                continue
            _sync_reporte_general(personal, anio, mes)
            reportes_actualizados += 1

        return Response(
            {
                "procesados": len(dispositivos),
                "total_creadas": total_creadas,
                "total_duplicadas": total_duplicadas,
                "reportes_actualizados": reportes_actualizados,
                "resultados": resultados,
                "raw_logs_total": len(raw_logs),
                "raw_logs": raw_logs,
                "notificaciones": build_missing_mark_notifications(),
            }
        )


class MarcacionViewSet(BaseModelViewSet):
    queryset = Marcacion.objects.select_related("personal", "dispositivo").all()
    serializer_class = MarcacionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        personal = self.request.query_params.get("personal")
        fecha_inicio = self.request.query_params.get("fecha_inicio")
        fecha_fin = self.request.query_params.get("fecha_fin")
        q = self.request.query_params.get("q")

        if personal:
            queryset = queryset.filter(personal_id=personal)
        if fecha_inicio:
            queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
        if q:
            queryset = queryset.filter(
                models.Q(personal__nombres_completos__icontains=q)
                | models.Q(personal__numero_documento__icontains=q)
                | models.Q(personal__codigo_empleado__icontains=q)
                | models.Q(codigo_equipo__icontains=q)
            )

        return queryset.order_by("-fecha_hora", "personal_id")


class JustificacionViewSet(BaseModelViewSet):
    queryset = Justificacion.objects.select_related(
        "personal",
        "sucursal",
        "area",
        "gestionado_por",
    ).all()
    serializer_class = JustificacionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sucursal = self.request.query_params.get("sucursal")
        area = self.request.query_params.get("area")
        motivo = self.request.query_params.get("motivo")
        fecha = self.request.query_params.get("fecha")
        mes = self.request.query_params.get("mes")
        anio = self.request.query_params.get("anio")
        estado = self.request.query_params.get("estado")
        q = self.request.query_params.get("q")

        if sucursal:
            queryset = queryset.filter(sucursal_id=sucursal)
        if area:
            queryset = queryset.filter(area_id=area)
        if motivo:
            queryset = queryset.filter(motivo__icontains=motivo)
        if fecha:
            queryset = queryset.filter(fecha_inicio=fecha)
        if mes:
            queryset = queryset.filter(fecha_inicio__month=mes)
        if anio:
            queryset = queryset.filter(fecha_inicio__year=anio)
        if estado:
            queryset = queryset.filter(estado=estado)
        if q:
            queryset = queryset.filter(
                models.Q(personal__nombres_completos__icontains=q)
                | models.Q(personal__numero_documento__icontains=q)
                | models.Q(numero_documento__icontains=q)
            )

        return queryset

    @action(detail=False, methods=["post"], url_path="gestionar")
    def gestionar(self, request):
        ids = request.data.get("ids") or []
        accion = (request.data.get("accion") or "").upper()
        motivo = (request.data.get("motivo") or "").strip()

        if not isinstance(ids, list) or not ids:
            return Response({"detail": "Debe enviar ids como lista no vacia."}, status=status.HTTP_400_BAD_REQUEST)

        valid_ids = []
        for item in ids:
            try:
                valid_ids.append(int(item))
            except (TypeError, ValueError):
                continue

        if not valid_ids:
            return Response({"detail": "No se enviaron IDs validos."}, status=status.HTTP_400_BAD_REQUEST)

        if accion not in {"AUTORIZAR", "NO_AUTORIZAR"}:
            return Response({"detail": "accion invalida. Use AUTORIZAR o NO_AUTORIZAR."}, status=status.HTTP_400_BAD_REQUEST)

        if accion == "NO_AUTORIZAR" and not motivo:
            return Response({"detail": "Debe enviar motivo para no autorizar."}, status=status.HTTP_400_BAD_REQUEST)

        estado_target = (
            Justificacion.Estado.AUTORIZADO if accion == "AUTORIZAR" else Justificacion.Estado.NO_AUTORIZADO
        )

        payload = {
            "estado": estado_target,
            "gestionado_por": request.user if request.user.is_authenticated else None,
            "fecha_gestion": now(),
        }

        if accion == "AUTORIZAR":
            payload["motivo_no_autorizacion"] = ""
        else:
            payload["motivo_no_autorizacion"] = motivo

        updated = Justificacion.objects.filter(id__in=valid_ids).update(**payload)
        return Response({"actualizados": updated, "estado": estado_target})


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


class BoletaMensualViewSet(BaseModelViewSet):
    queryset = BoletaMensual.objects.all()
    serializer_class = BoletaMensualSerializer

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

        existing_personal_ids = set(
            Personal.objects.filter(id__in=valid_ids).values_list("id", flat=True)
        )
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

        created_boletas = list(
            BoletaMensual.objects.filter(anio=anio, mes=mes, personal_id__in=new_ids)
        )
        conceptos_nuevos = []
        for boleta in created_boletas:
            conceptos_nuevos.append(
                BoletaConcepto(
                    boleta=boleta,
                    tipo=BoletaConcepto.Tipo.INGRESO,
                    concepto="REMUNERACION BASICA",
                    monto=boleta.sueldo_base,
                )
            )
        if conceptos_nuevos:
            BoletaConcepto.objects.bulk_create(conceptos_nuevos)

        return Response(
            {
                "anio": anio,
                "mes": mes,
                "recibidos": len(valid_ids),
                "validos": len(target_ids),
                "creados": len(new_ids),
                "existentes": len(existing_boletas_ids),
            }
        )


class BoletaConceptoViewSet(BaseModelViewSet):
    queryset = BoletaConcepto.objects.all()
    serializer_class = BoletaConceptoSerializer


class ReportePersonalMensualViewSet(BaseModelViewSet):
    queryset = ReportePersonalMensual.objects.all()
    serializer_class = ReportePersonalMensualSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        anio = self.request.query_params.get("anio")
        mes = self.request.query_params.get("mes")
        personal_id = self.request.query_params.get("personal")

        if anio:
            queryset = queryset.filter(anio=anio)
        if mes:
            queryset = queryset.filter(mes=mes)
        if personal_id:
            queryset = queryset.filter(personal_id=personal_id)

        return queryset


class ReporteAsistenciaDiariaViewSet(BaseModelViewSet):
    queryset = ReporteAsistenciaDiaria.objects.all()
    serializer_class = ReporteAsistenciaDiariaSerializer


class ReporteConceptoPersonalViewSet(BaseModelViewSet):
    queryset = ReporteConceptoPersonal.objects.all()
    serializer_class = ReporteConceptoPersonalSerializer


class ReporteIncidenciaPersonalViewSet(BaseModelViewSet):
    queryset = ReporteIncidenciaPersonal.objects.all()
    serializer_class = ReporteIncidenciaPersonalSerializer


class UsuarioAguaViewSet(BaseModelViewSet):
    queryset = UsuarioAgua.objects.all()
    serializer_class = UsuarioAguaSerializer


class LicenciaAguaViewSet(BaseModelViewSet):
    queryset = LicenciaAgua.objects.all()
    serializer_class = LicenciaAguaSerializer
