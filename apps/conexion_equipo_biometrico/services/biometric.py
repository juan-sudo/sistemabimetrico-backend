from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from django.utils import timezone


class BiometricConnectionError(Exception):
    pass


@dataclass
class AttendanceRecord:
    user_code: str
    timestamp: Any
    punch: int | None
    raw_data: dict[str, Any] | None = None
    device_user_name: str = ""


def _json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    return str(value)


def _extract_raw_data(raw: Any) -> dict[str, Any]:
    raw_dict: dict[str, Any] = {}
    preferred_fields = (
        "uid", "user_id", "timestamp", "punch",
        "status", "verify_type", "work_code", "workcode", "card",
    )
    for field in preferred_fields:
        if hasattr(raw, field):
            try:
                raw_dict[field] = _json_safe(getattr(raw, field))
            except Exception:
                continue

    try:
        raw_vars = vars(raw)
    except Exception:
        raw_vars = {}
    for key, value in raw_vars.items():
        key_str = str(key)
        if key_str.startswith("_") or key_str in raw_dict:
            continue
        raw_dict[key_str] = _json_safe(value)

    return raw_dict


def _normalize_timestamp(value: Any):
    if value is None:
        raise BiometricConnectionError("El reloj no devolvio fecha/hora en una marcacion.")
    if timezone.is_naive(value):
        return timezone.make_aware(value, timezone.get_current_timezone())
    return value


def _parse_attendance(raw: Any) -> AttendanceRecord:
    user_code = (
        getattr(raw, "user_id", None)
        or getattr(raw, "uid", None)
        or getattr(raw, "pin", None)
        or ""
    )
    punch = getattr(raw, "punch", None)
    timestamp = getattr(raw, "timestamp", None)
    return AttendanceRecord(
        user_code=str(user_code or "").strip(),
        timestamp=_normalize_timestamp(timestamp),
        punch=int(punch) if punch is not None else None,
        raw_data=_extract_raw_data(raw),
    )


def _get_zk_class():
    try:
        from zk import ZK  # type: ignore
        return ZK
    except Exception as exc:
        raise BiometricConnectionError(
            "No esta instalada la libreria del reloj. Instala 'pyzk' en el backend."
        ) from exc


@contextmanager
def _zk_connection(host: str, port: int, password: int, timeout: int):
    ZK = _get_zk_class()
    zk = ZK(host, port=port, timeout=timeout, password=password, force_udp=False, ommit_ping=True)
    conn = None
    try:
        conn = zk.connect()
        yield conn
    except BiometricConnectionError:
        raise
    except Exception as exc:
        raise BiometricConnectionError(
            f"No se pudo conectar al dispositivo biometrico {host}:{port}."
        ) from exc
    finally:
        if conn is not None:
            try:
                conn.disconnect()
            except Exception:
                pass


def read_attendance_logs(host: str, port: int, password: int = 0, timeout: int = 10) -> list[AttendanceRecord]:
    with _zk_connection(host, port, password, timeout) as conn:
        try:
            attendance = conn.get_attendance() or []
        except Exception as exc:
            raise BiometricConnectionError("No se pudo leer marcaciones del dispositivo.") from exc

        users_by_code: dict[str, str] = {}
        try:
            users = conn.get_users() or []
            for user in users:
                code = str(getattr(user, "user_id", None) or getattr(user, "uid", None) or "").strip()
                if code:
                    users_by_code[code] = str(getattr(user, "name", "") or "").strip()
        except Exception:
            pass

        parsed_records = [_parse_attendance(item) for item in attendance]
        for record in parsed_records:
            record.device_user_name = users_by_code.get(record.user_code, "")
        return parsed_records


def read_device_capacity(host: str, port: int, password: int = 0, timeout: int = 10) -> dict[str, Any]:
    with _zk_connection(host, port, password, timeout) as conn:
        try:
            conn.read_sizes()
        except Exception as exc:
            raise BiometricConnectionError("No se pudo leer la capacidad del dispositivo.") from exc

        return {
            "device_name": str(getattr(conn, "get_device_name", lambda: "")() or "").strip(),
            "platform": str(getattr(conn, "get_platform", lambda: "")() or "").strip(),
            "firmware": str(getattr(conn, "get_firmware_version", lambda: "")() or "").strip(),
            "registros_usados": int(getattr(conn, "records", 0) or 0),
            "registros_capacidad": int(getattr(conn, "rec_cap", 0) or 0),
            "registros_disponibles": int(getattr(conn, "rec_av", 0) or 0),
            "usuarios_usados": int(getattr(conn, "users", 0) or 0),
            "usuarios_capacidad": int(getattr(conn, "users_cap", 0) or 0),
            "usuarios_disponibles": int(getattr(conn, "users_av", 0) or 0),
            "huellas_usadas": int(getattr(conn, "fingers", 0) or 0),
            "huellas_capacidad": int(getattr(conn, "fingers_cap", 0) or 0),
            "huellas_disponibles": int(getattr(conn, "fingers_av", 0) or 0),
            "caras_usadas": int(getattr(conn, "faces", 0) or 0),
            "caras_capacidad": int(getattr(conn, "faces_cap", 0) or 0),
            "tarjetas_usadas": int(getattr(conn, "cards", 0) or 0),
        }


def probe_device_connection(host: str, port: int, password: int = 0, timeout: int = 8) -> dict[str, Any]:
    ZK = _get_zk_class()

    # Try TCP first, then UDP as fallback (some ZKTeco models require UDP)
    last_exc: Exception | None = None
    for force_udp in (False, True):
        zk = ZK(host, port=port, timeout=timeout, password=password, force_udp=force_udp, ommit_ping=True)
        conn = None
        try:
            conn = zk.connect()
            return {
                "host": host,
                "port": port,
                "estado": "ok",
                "detalle": "Conexion establecida correctamente.",
            }
        except Exception as exc:
            last_exc = exc
        finally:
            if conn is not None:
                try:
                    conn.disconnect()
                except Exception:
                    pass

    raise BiometricConnectionError(
        f"No se pudo conectar al dispositivo biometrico {host}:{port}."
    ) from last_exc
