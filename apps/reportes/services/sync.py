import calendar
from datetime import date, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import models, transaction

from apps.boleta_concepto.models import BoletaConcepto
from apps.boleta_mensual.models import BoletaMensual
from apps.descanso_medico.models import DescansoMedico
from apps.justificacion.models import Justificacion
from apps.marcacion.models import Marcacion
from apps.reporte_asistencia_diaria.models import ReporteAsistenciaDiaria
from apps.reporte_concepto_personal.models import ReporteConceptoPersonal
from apps.reporte_incidencia_personal.models import ReporteIncidenciaPersonal
from apps.reporte_personal_mensual.models import ReportePersonalMensual
from apps.turnos.models.personal_turno import PersonalTurno

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


def build_boleta_detalle(*, personal, boleta, anio, mes, dias_con_marcacion, dias_justificados, dias_descanso, faltas):
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
        ingresos.append({"codigo": "I001", "concepto": profile["ingreso_principal"], "monto": _decimal_str(boleta.sueldo_base)})

    total_ingresos = _decimal(boleta.total_ingresos if boleta else 0)
    if total_ingresos > 0 and not aportes_trabajador and profile["aporte_trabajador_rate"] > 0:
        aportes_trabajador.append({"codigo": "AT001", "concepto": profile["aporte_trabajador_label"], "monto": _decimal_str(total_ingresos * profile["aporte_trabajador_rate"])})

    if total_ingresos > 0 and profile["aporte_empleador_rate"] > 0 and profile["aporte_empleador_concepto"]:
        aportes_empleador.append({"codigo": "AE001", "concepto": profile["aporte_empleador_concepto"], "monto": _decimal_str(total_ingresos * profile["aporte_empleador_rate"])})

    situacion = "ACTIVO O SUBSIDIADO" if dias_descanso else "ACTIVO"
    dias_trabajados = max(len(dias_con_marcacion) + len(dias_justificados), 0)
    total_horas = len(dias_con_marcacion) * 8
    meses_label = MONTH_LABELS[mes] if 0 < mes < len(MONTH_LABELS) else str(mes)

    return {
        "periodo_texto": f"{meses_label} {anio}",
        "periodo_corto": f"{mes:02d}/{anio}",
        "numero_orden": f"{anio}{mes:02d}-{personal.id:05d}",
        "documento_identidad": {"tipo": personal.tipo_documento.descripcion if personal.tipo_documento_id else "Documento", "numero": personal.numero_documento},
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
        "conceptos": {"ingresos": ingresos, "descuentos": descuentos, "aportes_trabajador": aportes_trabajador, "aportes_empleador": aportes_empleador},
    }


def build_reporte_general_payload(personal, anio, mes):
    if mes < 1 or mes > 12:
        raise ValueError("mes debe estar entre 1 y 12.")
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, ultimo_dia)
    boleta = BoletaMensual.objects.filter(personal=personal, anio=anio, mes=mes).prefetch_related("conceptos").order_by("-created_at").first()
    justificaciones = list(Justificacion.objects.filter(personal=personal, fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_inicio).order_by("fecha_inicio", "id"))
    descansos = list(DescansoMedico.objects.filter(personal=personal, fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_inicio).order_by("fecha_inicio", "id"))
    marcaciones = list(Marcacion.objects.filter(personal=personal, fecha_hora__date__gte=fecha_inicio, fecha_hora__date__lte=fecha_fin + timedelta(days=1)).order_by("fecha_hora", "id"))
    asignaciones_turno = list(
        PersonalTurno.objects.select_related("turno")
        .prefetch_related("turno__bloques")
        .filter(personal=personal, fecha_inicio__lte=fecha_fin)
        .filter(models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=fecha_inicio))
        .order_by("-fecha_inicio", "-id")
    )
    bloques_by_asignacion = {
        item.id: sorted(list(item.turno.bloques.all()), key=lambda block: block.orden)
        for item in asignaciones_turno
    }
    dias_justificados, dias_descanso, marcaciones_por_dia = set(), set(), {}
    for item in justificaciones:
        current = max(item.fecha_inicio, fecha_inicio)
        end = min(item.fecha_fin, fecha_fin)
        while current <= end:
            if item.estado == Justificacion.Estado.AUTORIZADO:
                dias_justificados.add(current)
            current += timedelta(days=1)
    for item in descansos:
        current = max(item.fecha_inicio, fecha_inicio)
        end = min(item.fecha_fin, fecha_fin)
        while current <= end:
            dias_descanso.add(current)
            current += timedelta(days=1)
    for item in marcaciones:
        marcaciones_por_dia.setdefault(item.fecha_hora.date(), []).append(item)

    def _assignment_for_day(current_day):
        fallback = None
        for item in asignaciones_turno:
            if item.fecha_inicio <= current_day:
                if fallback is None:
                    fallback = item
                if item.fecha_fin is None or item.fecha_fin >= current_day:
                    return item
        return fallback if fallback is not None else (asignaciones_turno[-1] if asignaciones_turno else None)

    dias, faltas = [], []
    total_horas_trabajadas, total_horas_extra = Decimal("0.00"), Decimal("0.00")
    total_minutos_tardanza = 0
    for offset in range(ultimo_dia):
        current = fecha_inicio + timedelta(days=offset)
        marks = marcaciones_por_dia.get(current, [])
        entradas = [item for item in marks if item.tipo_evento == Marcacion.TipoEvento.ENTRADA]
        salidas = [item for item in marks if item.tipo_evento == Marcacion.TipoEvento.SALIDA]
        active_assignment = _assignment_for_day(current)
        bloques_turno = bloques_by_asignacion.get(active_assignment.id, []) if active_assignment else []
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
            dias.append({"fecha": current.isoformat(), "bloque_orden": block.orden if block else block_index, "estado_dia": estado_dia, "hora_entrada_programada": block.hora_entrada.isoformat() if block else None, "hora_salida_programada": block.hora_salida.isoformat() if block else None, "hora_entrada_real": entrada_mark.isoformat() if entrada_mark else None, "hora_salida_real": salida_mark.isoformat() if salida_mark else None, "minutos_tardanza": 0, "horas_trabajadas": _decimal_str(horas_trabajadas), "horas_extra": "0.00", "observacion": "", "marcaciones": [{"id": item.id, "fecha_hora": item.fecha_hora.isoformat(), "tipo_evento": item.tipo_evento} for item in marks]})
    boleta_detalle = build_boleta_detalle(personal=personal, boleta=boleta, anio=anio, mes=mes, dias_con_marcacion=set(marcaciones_por_dia.keys()), dias_justificados=dias_justificados, dias_descanso=dias_descanso, faltas=faltas)
    conceptos_reporte, concept_order = [], 1
    for tipo, items in [("INGRESO", boleta_detalle["conceptos"]["ingresos"]), ("DESCUENTO", boleta_detalle["conceptos"]["descuentos"]), ("APORTE_TRABAJADOR", boleta_detalle["conceptos"]["aportes_trabajador"]), ("APORTE_EMPLEADOR", boleta_detalle["conceptos"]["aportes_empleador"])]:
        for item in items:
            conceptos_reporte.append({"tipo": tipo, "codigo": item["codigo"], "concepto": item["concepto"], "monto": item["monto"], "orden": concept_order})
            concept_order += 1
    incidencias = []
    for item in justificaciones:
        incidencias.append({"tipo": ReporteIncidenciaPersonal.Tipo.JUSTIFICACION, "fecha_inicio": item.fecha_inicio.isoformat(), "fecha_fin": item.fecha_fin.isoformat(), "cantidad_dias": item.dias, "cantidad_minutos": 0, "referencia_modelo": "Justificacion", "referencia_id": item.id, "descripcion": item.motivo, "observacion": item.estado})
    for item in descansos:
        incidencias.append({"tipo": ReporteIncidenciaPersonal.Tipo.DESCANSO_MEDICO, "fecha_inicio": item.fecha_inicio.isoformat(), "fecha_fin": item.fecha_fin.isoformat(), "cantidad_dias": item.dias, "cantidad_minutos": 0, "referencia_modelo": "DescansoMedico", "referencia_id": item.id, "descripcion": item.motivo, "observacion": item.citt})
    for item in faltas:
        incidencias.append({"tipo": ReporteIncidenciaPersonal.Tipo.FALTA, "fecha_inicio": item, "fecha_fin": item, "cantidad_dias": 1, "cantidad_minutos": 0, "referencia_modelo": "", "referencia_id": None, "descripcion": "Falta sin marcacion ni sustento", "observacion": ""})
    return {"personal": {"id": personal.id, "codigo_empleado": personal.codigo_empleado, "numero_documento": personal.numero_documento, "nombres_completos": personal.nombres_completos, "empresa": {"id": personal.empresa_id, "razon_social": personal.empresa.razon_social if personal.empresa_id else "", "ruc": personal.empresa.ruc if personal.empresa_id else ""}, "sucursal_nombre": personal.sucursal.nombre if personal.sucursal_id else "", "area_nombre": personal.area.nombre if personal.area_id else "", "tipo_trabajador_codigo": personal.tipo_trabajador.codigo if personal.tipo_trabajador_id else "", "tipo_trabajador": personal.tipo_trabajador.descripcion if personal.tipo_trabajador_id else "", "categoria_codigo": personal.categoria.codigo if personal.categoria_id else "", "categoria": personal.categoria.descripcion if personal.categoria_id else "", "cargo": personal.cargo.descripcion if personal.cargo_id else ""}, "periodo": {"anio": anio, "mes": mes, "fecha_inicio": fecha_inicio.isoformat(), "fecha_fin": fecha_fin.isoformat(), "etiqueta": f"{MONTH_LABELS[mes]} {anio}", "etiqueta_corta": f"{mes:02d}/{anio}"}, "reporte": {"sueldo_base": _decimal_str(boleta.sueldo_base if boleta else 0), "total_ingresos": _decimal_str(boleta.total_ingresos if boleta else 0), "total_descuentos": _decimal_str(boleta.total_descuentos if boleta else 0), "neto_pagar": _decimal_str(boleta.neto_pagar if boleta else 0), "total_dias_periodo": ultimo_dia, "total_dias_laborados": sum(1 for item in dias if item["estado_dia"] == ReporteAsistenciaDiaria.EstadoDia.ASISTIO), "total_dias_falta": len(faltas), "total_dias_justificados": len(dias_justificados), "total_dias_descanso_medico": len(dias_descanso), "total_minutos_tardanza": total_minutos_tardanza, "total_horas_trabajadas": _decimal_str(total_horas_trabajadas), "total_horas_extra": _decimal_str(total_horas_extra), "estado": ReportePersonalMensual.Estado.GENERADO}, "dias": dias, "conceptos": conceptos_reporte, "incidencias": incidencias, "boleta_detalle": boleta_detalle}


def sync_reporte_general(personal, anio, mes):
    payload = build_reporte_general_payload(personal, anio, mes)
    with transaction.atomic():
        reporte, _ = ReportePersonalMensual.objects.update_or_create(personal=personal, anio=anio, mes=mes, defaults={"fecha_inicio": date.fromisoformat(payload["periodo"]["fecha_inicio"]), "fecha_fin": date.fromisoformat(payload["periodo"]["fecha_fin"]), "sueldo_base": payload["reporte"]["sueldo_base"], "total_ingresos": payload["reporte"]["total_ingresos"], "total_descuentos": payload["reporte"]["total_descuentos"], "neto_pagar": payload["reporte"]["neto_pagar"], "total_dias_periodo": payload["reporte"]["total_dias_periodo"], "total_dias_laborados": payload["reporte"]["total_dias_laborados"], "total_dias_falta": payload["reporte"]["total_dias_falta"], "total_dias_justificados": payload["reporte"]["total_dias_justificados"], "total_dias_descanso_medico": payload["reporte"]["total_dias_descanso_medico"], "total_minutos_tardanza": payload["reporte"]["total_minutos_tardanza"], "total_horas_trabajadas": payload["reporte"]["total_horas_trabajadas"], "total_horas_extra": payload["reporte"]["total_horas_extra"], "estado": payload["reporte"]["estado"], "observacion": "Generado automaticamente desde marcaciones, boletas e incidencias."})
        ReporteAsistenciaDiaria.objects.filter(reporte=reporte).delete()
        ReporteConceptoPersonal.objects.filter(reporte=reporte).delete()
        ReporteIncidenciaPersonal.objects.filter(reporte=reporte).delete()
        ReporteAsistenciaDiaria.objects.bulk_create([ReporteAsistenciaDiaria(reporte=reporte, fecha=date.fromisoformat(item["fecha"]), bloque_orden=item["bloque_orden"], estado_dia=item["estado_dia"], hora_entrada_programada=time.fromisoformat(item["hora_entrada_programada"]) if item["hora_entrada_programada"] else None, hora_salida_programada=time.fromisoformat(item["hora_salida_programada"]) if item["hora_salida_programada"] else None, hora_entrada_real=time.fromisoformat(item["hora_entrada_real"]) if item["hora_entrada_real"] else None, hora_salida_real=time.fromisoformat(item["hora_salida_real"]) if item["hora_salida_real"] else None, minutos_tardanza=item["minutos_tardanza"], horas_trabajadas=item["horas_trabajadas"], horas_extra=item["horas_extra"], observacion=item["observacion"]) for item in payload["dias"]])
        if payload["conceptos"]:
            ReporteConceptoPersonal.objects.bulk_create([ReporteConceptoPersonal(reporte=reporte, tipo=item["tipo"], codigo=item["codigo"], concepto=item["concepto"], monto=item["monto"], orden=item["orden"]) for item in payload["conceptos"]])
        if payload["incidencias"]:
            ReporteIncidenciaPersonal.objects.bulk_create([ReporteIncidenciaPersonal(reporte=reporte, tipo=item["tipo"], fecha_inicio=date.fromisoformat(item["fecha_inicio"]), fecha_fin=date.fromisoformat(item["fecha_fin"]), cantidad_dias=item["cantidad_dias"], cantidad_minutos=item["cantidad_minutos"], referencia_modelo=item["referencia_modelo"], referencia_id=item["referencia_id"], descripcion=item["descripcion"], observacion=item["observacion"]) for item in payload["incidencias"]])
    payload["reporte"]["id"] = reporte.id
    return payload
