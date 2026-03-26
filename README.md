# Backend Django - Sistema Biometrico

## 1) Activar entorno virtual

```powershell
cd "C:\DISCO D\MUNICIPALIDAD\backend"
.\.venv\Scripts\Activate.ps1
```

## 2) Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

## 3) Configurar variables de entorno

```powershell
Copy-Item .env.example .env
```

Edita `.env` si necesitas cambiar hosts/origins.

## 4) Migraciones

```powershell
python manage.py migrate
python manage.py createsuperuser
```

## 5) Ejecutar servidor

```powershell
python manage.py runserver
```

## Endpoints base

- API root: `http://127.0.0.1:8000/api/`
- Health: `http://127.0.0.1:8000/api/health/`
- Admin: `http://127.0.0.1:8000/admin/`
