from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UsuarioModuloPermiso(TimestampedModel):
    class Modulo(models.TextChoices):
        ESCRITORIO = "ESCRITORIO", "Escritorio"
        EMPRESAS = "EMPRESAS", "Empresas"
        SUCURSALES = "SUCURSALES", "Sucursales"
        AREAS = "AREAS", "Areas"
        CARGOS = "CARGOS", "Cargos"
        TIPO_TRABAJADOR = "TIPO_TRABAJADOR", "Tipo trabajador"
        TIPO_SINDICATO = "TIPO_SINDICATO", "Tipo sindicato"
        CATEGORIAS = "CATEGORIAS", "Categorias"
        TURNOS = "TURNOS", "Turnos"
        DISPOSITIVOS = "DISPOSITIVOS", "Dispositivos"
        DESCARGAR_MARCAS = "DESCARGAR_MARCAS", "Descargar marcas"
        PERSONAL = "PERSONAL", "Personal"
        BOLETA_MENSUAL = "BOLETA_MENSUAL", "Boleta mensual"
        RESUMEN_PLANILLA = "RESUMEN_PLANILLA", "Resumen planilla"
        MARCACIONES = "MARCACIONES", "Marcaciones"
        PROCESAR_ASISTENCIA = "PROCESAR_ASISTENCIA", "Procesar asistencia"
        CONSULTAR_ASISTENCIA = "CONSULTAR_ASISTENCIA", "Consultar asistencia"
        JUSTIFICACIONES = "JUSTIFICACIONES", "Registrar justificacion"
        AUTORIZAR_JUSTIFICACION = "AUTORIZAR_JUSTIFICACION", "Autorizar justificacion"
        DESCANSO_MEDICO = "DESCANSO_MEDICO", "Descanso medico"
        USUARIOS = "USUARIOS", "Usuarios"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_permissions")
    modulo = models.CharField(max_length=40, choices=Modulo.choices)
    puede_ver = models.BooleanField(default=True)
    puede_crear = models.BooleanField(default=False)
    puede_editar = models.BooleanField(default=False)
    puede_eliminar = models.BooleanField(default=False)

    class Meta:
        db_table = "usuarios_modulos_permisos"
        ordering = ["user_id", "modulo"]
        constraints = [
            models.UniqueConstraint(fields=["user", "modulo"], name="uq_usuario_modulo_permiso"),
        ]


class Empresa(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)
    ruc = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(blank=True)
    logo = models.FileField(upload_to="empresas/logos/", blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "empresas"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social


class Sucursal(TimestampedModel):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="sucursales")
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "sucursales"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["empresa", "codigo"], name="uq_sucursal_empresa_codigo"),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Area(TimestampedModel):
    class Tipo(models.TextChoices):
        GERENCIA = "GERENCIA", "Gerencia"
        OFICINA = "OFICINA", "Oficina"
        SUBGERENCIA = "SUBGERENCIA", "Subgerencia"
        UNIDAD = "UNIDAD", "Unidad"

    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="areas")
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.GERENCIA)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        null=True,
        blank=True,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "areas"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["sucursal", "codigo"], name="uq_area_sucursal_codigo"),
        ]

    def __str__(self):
        return self.nombre


class Cargo(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "cargos"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


class TipoTrabajador(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "tipos_trabajador"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


class Categoria(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=120)
    periodos_vacacionales = models.BooleanField(default=False)
    dias_por_periodo = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "categorias"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


class TipoDocumento(TimestampedModel):
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "tipos_documento"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


class TipoSindicato(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "tipos_sindicato"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


class UbicacionGeografica(TimestampedModel):
    pais = models.CharField(max_length=80, default="Peru")
    departamento = models.CharField(max_length=80)
    provincia = models.CharField(max_length=80)
    distrito = models.CharField(max_length=80)

    class Meta:
        db_table = "ubicaciones_geograficas"
        ordering = ["departamento", "provincia", "distrito"]
        constraints = [
            models.UniqueConstraint(
                fields=["pais", "departamento", "provincia", "distrito"],
                name="uq_ubicacion_geo",
            )
        ]

    def __str__(self):
        return f"{self.departamento} / {self.provincia} / {self.distrito}"


class Personal(TimestampedModel):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="personales")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="personales")
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="personales")
    ubicacion = models.ForeignKey(
        UbicacionGeografica,
        on_delete=models.SET_NULL,
        related_name="personales",
        null=True,
        blank=True,
    )
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name="personales")
    tipo_trabajador = models.ForeignKey(TipoTrabajador, on_delete=models.PROTECT, related_name="personales")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="personales")
    tipo_sindicato = models.ForeignKey(
        TipoSindicato,
        on_delete=models.PROTECT,
        related_name="personales",
        null=True,
        blank=True,
    )
    cargo = models.ForeignKey(Cargo, on_delete=models.SET_NULL, related_name="personales", null=True, blank=True)
    codigo_empleado = models.CharField(max_length=30, unique=True)
    numero_documento = models.CharField(max_length=20, unique=True)
    nombres_completos = models.CharField(max_length=255)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)

    class Meta:
        db_table = "personales"
        ordering = ["nombres_completos"]

    def __str__(self):
        return f"{self.nombres_completos} ({self.numero_documento})"


class Turno(TimestampedModel):
    class Tipo(models.TextChoices):
        GENERAL = "GENERAL", "General"
        GENERAL_PERSONALIZADO = "GENERAL_PERSONALIZADO", "General Personalizado"
        DESCANSO = "DESCANSO", "Descanso"

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=180)
    tipo = models.CharField(max_length=30, choices=Tipo.choices, default=Tipo.GENERAL)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "turnos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class TurnoBloqueHorario(TimestampedModel):
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name="bloques")
    orden = models.PositiveSmallIntegerField(default=1)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    class Meta:
        db_table = "turno_bloques_horario"
        ordering = ["turno", "orden"]
        constraints = [
            models.UniqueConstraint(fields=["turno", "orden"], name="uq_turno_bloque_orden"),
        ]

    def __str__(self):
        return f"{self.turno.codigo} bloque {self.orden}"


class PersonalTurno(TimestampedModel):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="asignaciones_turno")
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT, related_name="asignaciones_personal")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "personal_turnos"
        ordering = ["-fecha_inicio"]


class Dispositivo(TimestampedModel):
    class DireccionTipo(models.TextChoices):
        IP = "IP", "Direccion IP"
        DOMINIO = "DOMINIO", "Dominio"

    class Uso(models.TextChoices):
        ASISTENCIA = "ASISTENCIA", "Control de Asistencia"
        ACCESO = "ACCESO", "Control de Acceso"

    nombre = models.CharField(max_length=120, unique=True)
    direccion_tipo = models.CharField(max_length=10, choices=DireccionTipo.choices, default=DireccionTipo.IP)
    direccion = models.CharField(max_length=255)
    comunicacion = models.CharField(max_length=40, default="TCP/IP")
    puerto = models.PositiveIntegerField(default=4370)
    uso = models.CharField(max_length=20, choices=Uso.choices, default=Uso.ASISTENCIA)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "dispositivos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class DescargaMarcacion(TimestampedModel):
    class Fuente(models.TextChoices):
        DISPOSITIVO = "DISPOSITIVO", "Dispositivo"
        USB = "USB", "USB"
        EXCEL = "EXCEL", "Importacion Excel"

    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.SET_NULL,
        related_name="descargas",
        null=True,
        blank=True,
    )
    fuente = models.CharField(max_length=20, choices=Fuente.choices, default=Fuente.DISPOSITIVO)
    ejecutado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "descargas_marcaciones"
        ordering = ["-created_at"]


class Marcacion(TimestampedModel):
    class Situacion(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    class TipoEvento(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"

    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="marcaciones")
    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.SET_NULL,
        related_name="marcaciones",
        null=True,
        blank=True,
    )
    descarga = models.ForeignKey(
        DescargaMarcacion,
        on_delete=models.SET_NULL,
        related_name="marcaciones",
        null=True,
        blank=True,
    )
    codigo_equipo = models.CharField(max_length=40, blank=True)
    fecha_hora = models.DateTimeField()
    tipo_evento = models.CharField(max_length=10, choices=TipoEvento.choices, default=TipoEvento.ENTRADA)
    situacion = models.CharField(max_length=10, choices=Situacion.choices, default=Situacion.ACTIVO)

    class Meta:
        db_table = "marcaciones"
        ordering = ["-fecha_hora"]


class Justificacion(TimestampedModel):
    class Tipo(models.TextChoices):
        SALIDA = "SALIDA", "Salida"
        INGRESO = "INGRESO", "Ingreso"

    class Rango(models.TextChoices):
        PARCIAL = "PARCIAL", "Parcial"
        COMPLETO = "COMPLETO", "Completo"

    class Estado(models.TextChoices):
        AUTORIZADO = "AUTORIZADO", "Autorizado"
        NO_AUTORIZADO = "NO_AUTORIZADO", "No Autorizado"
        PENDIENTE = "PENDIENTE", "Pendiente"

    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="justificaciones")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="justificaciones")
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="justificaciones")
    motivo = models.CharField(max_length=180)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.SALIDA)
    rango = models.CharField(max_length=10, choices=Rango.choices, default=Rango.PARCIAL)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias = models.PositiveIntegerField(default=1)
    descripcion = models.TextField(blank=True)
    tiene_adjunto = models.BooleanField(default=False)
    numero_documento = models.CharField(max_length=50, blank=True)
    nombre_documento = models.CharField(max_length=180, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    gestionado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_gestion = models.DateTimeField(null=True, blank=True)
    motivo_no_autorizacion = models.TextField(blank=True)

    class Meta:
        db_table = "justificaciones"
        ordering = ["-created_at"]


class DescansoMedico(TimestampedModel):
    class Motivo(models.TextChoices):
        SALUD = "SALUD", "Por salud"
        SUBSIDIO = "SUBSIDIO", "Subsidio"

    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="descansos_medicos")
    motivo = models.CharField(max_length=20, choices=Motivo.choices)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias = models.PositiveIntegerField(default=1)
    citt = models.CharField(max_length=60, blank=True)
    diagnostico = models.CharField(max_length=255, blank=True)
    tiene_adjunto = models.BooleanField(default=False)
    numero_documento = models.CharField(max_length=60, blank=True)

    class Meta:
        db_table = "descansos_medicos"
        ordering = ["-fecha_inicio"]


class BoletaMensual(TimestampedModel):
    class Estado(models.TextChoices):
        GENERADA = "GENERADA", "Generada"
        DESCARGADA = "DESCARGADA", "Descargada"
        ANULADA = "ANULADA", "Anulada"

    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="boletas")
    anio = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2)
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    neto_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.GENERADA)
    archivo_pdf = models.FileField(upload_to="boletas/", blank=True, null=True)

    class Meta:
        db_table = "boletas_mensuales"
        ordering = ["-anio", "-mes"]
        constraints = [
            models.UniqueConstraint(fields=["personal", "anio", "mes"], name="uq_boleta_personal_periodo"),
            models.CheckConstraint(condition=models.Q(mes__gte=1, mes__lte=12), name="ck_boleta_mes_1_12"),
        ]


class BoletaConcepto(TimestampedModel):
    class Tipo(models.TextChoices):
        INGRESO = "INGRESO", "Ingreso"
        DESCUENTO = "DESCUENTO", "Descuento"

    boleta = models.ForeignKey(BoletaMensual, on_delete=models.CASCADE, related_name="conceptos")
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    concepto = models.CharField(max_length=120)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "boletas_conceptos"
        ordering = ["boleta", "tipo", "concepto"]


class UsuarioAgua(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    dni = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "usuarios_agua"
        ordering = ["nombres"]

    def __str__(self):
        return f"{self.codigo} - {self.nombres}"


class LicenciaAgua(TimestampedModel):
    class Estado(models.TextChoices):
        AGUA = "AGUA", "Activa"
        TRANSFERIDA = "TRANSFERIDA", "Transferida"
        ELIMINADA = "ELIMINADA", "Eliminada"

    usuario = models.ForeignKey(UsuarioAgua, on_delete=models.CASCADE, related_name="licencias")
    numero = models.CharField(max_length=30)
    ubicacion = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=180)
    fecha = models.DateField()
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.AGUA)

    class Meta:
        db_table = "licencias_agua"
        ordering = ["-fecha"]
        constraints = [
            models.UniqueConstraint(fields=["usuario", "numero"], name="uq_licencia_agua_usuario_numero"),
        ]

    def __str__(self):
        return f"{self.numero} - {self.usuario.codigo}"


class ReportePersonalMensual(TimestampedModel):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        GENERADO = "GENERADO", "Generado"
        CERRADO = "CERRADO", "Cerrado"

    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="reportes_mensuales")
    anio = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    neto_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_dias_periodo = models.PositiveSmallIntegerField(default=0)
    total_dias_laborados = models.PositiveSmallIntegerField(default=0)
    total_dias_falta = models.PositiveSmallIntegerField(default=0)
    total_dias_justificados = models.PositiveSmallIntegerField(default=0)
    total_dias_descanso_medico = models.PositiveSmallIntegerField(default=0)
    total_minutos_tardanza = models.PositiveIntegerField(default=0)
    total_horas_trabajadas = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    total_horas_extra = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.BORRADOR)
    observacion = models.CharField(max_length=255, blank=True)
    archivo_pdf = models.FileField(upload_to="reportes_personal/", blank=True, null=True)

    class Meta:
        db_table = "reportes_personal_mensual"
        ordering = ["-anio", "-mes", "personal_id"]
        constraints = [
            models.UniqueConstraint(fields=["personal", "anio", "mes"], name="uq_reporte_personal_periodo"),
            models.CheckConstraint(condition=models.Q(mes__gte=1, mes__lte=12), name="ck_reporte_mes_1_12"),
        ]


class ReporteAsistenciaDiaria(TimestampedModel):
    class EstadoDia(models.TextChoices):
        ASISTIO = "ASISTIO", "Asistio"
        FALTA = "FALTA", "Falta"
        JUSTIFICADO = "JUSTIFICADO", "Justificado"
        DESCANSO_MEDICO = "DESCANSO_MEDICO", "Descanso medico"
        DESCANSO = "DESCANSO", "Descanso"
        FERIADO = "FERIADO", "Feriado"

    reporte = models.ForeignKey(ReportePersonalMensual, on_delete=models.CASCADE, related_name="dias")
    fecha = models.DateField()
    bloque_orden = models.PositiveSmallIntegerField(default=1)
    estado_dia = models.CharField(max_length=20, choices=EstadoDia.choices, default=EstadoDia.ASISTIO)
    hora_entrada_programada = models.TimeField(null=True, blank=True)
    hora_salida_programada = models.TimeField(null=True, blank=True)
    hora_entrada_real = models.TimeField(null=True, blank=True)
    hora_salida_real = models.TimeField(null=True, blank=True)
    minutos_tardanza = models.PositiveIntegerField(default=0)
    horas_trabajadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    horas_extra = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "reportes_asistencia_diaria"
        ordering = ["reporte", "fecha", "bloque_orden"]
        constraints = [
            models.UniqueConstraint(fields=["reporte", "fecha", "bloque_orden"], name="uq_reporte_asistencia_fecha_bloque"),
        ]


class ReporteConceptoPersonal(TimestampedModel):
    class Tipo(models.TextChoices):
        INGRESO = "INGRESO", "Ingreso"
        DESCUENTO = "DESCUENTO", "Descuento"
        APORTE_TRABAJADOR = "APORTE_TRABAJADOR", "Aporte trabajador"
        APORTE_EMPLEADOR = "APORTE_EMPLEADOR", "Aporte empleador"
        OTRO = "OTRO", "Otro"

    reporte = models.ForeignKey(ReportePersonalMensual, on_delete=models.CASCADE, related_name="conceptos_reporte")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.INGRESO)
    codigo = models.CharField(max_length=20, blank=True)
    concepto = models.CharField(max_length=150)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "reportes_conceptos_personal"
        ordering = ["reporte", "orden", "tipo", "concepto"]


class ReporteIncidenciaPersonal(TimestampedModel):
    class Tipo(models.TextChoices):
        TARDANZA = "TARDANZA", "Tardanza"
        FALTA = "FALTA", "Falta"
        JUSTIFICACION = "JUSTIFICACION", "Justificacion"
        DESCANSO_MEDICO = "DESCANSO_MEDICO", "Descanso medico"
        LICENCIA = "LICENCIA", "Licencia"
        OTRO = "OTRO", "Otro"

    reporte = models.ForeignKey(ReportePersonalMensual, on_delete=models.CASCADE, related_name="incidencias")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.OTRO)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad_dias = models.PositiveSmallIntegerField(default=0)
    cantidad_minutos = models.PositiveIntegerField(default=0)
    referencia_modelo = models.CharField(max_length=50, blank=True)
    referencia_id = models.PositiveIntegerField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "reportes_incidencias_personal"
        ordering = ["reporte", "fecha_inicio", "tipo"]


