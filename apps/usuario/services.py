def build_usuario_nombre(user):
    full_name = f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip()
    return full_name or user.username


def build_usuario_rol(user):
    return "ADMINISTRADOR" if user.is_staff or user.is_superuser else "USUARIO"


__all__ = ["build_usuario_nombre", "build_usuario_rol"]
