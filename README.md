# Backend Django - Sistema Biometrico

## 1) Activar entorno virtual

```powershell
cd "C:\DISCO D\SISTEMA BIOMTRICO\sistemabimetrico-backend"
python -m venv .venv
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

## Docker (Django + Postgres)

```powershell
cd "C:\DISCO D\SISTEMA BIOMTRICO\sistemabimetrico-backend"
Copy-Item .env.example .env -Force
docker compose up --build
```

- Backend: `http://127.0.0.1:8000/`
- Postgres (desde tu PC): `localhost:5433` (en Docker interno sigue siendo `db:5432`)

### Crear todas las tablas (migraciones)

El contenedor `web` ya ejecuta `python manage.py migrate` al iniciar. Si quieres forzarlo:

```powershell
docker compose run --rm web python manage.py migrate
```

### (Opcional) Pasar datos desde `db.sqlite3` a Postgres

1) Exporta datos desde sqlite (una sola vez):

```powershell
$env:DJANGO_DB_ENGINE="sqlite"
docker compose run --rm -e DJANGO_DB_ENGINE=$env:DJANGO_DB_ENGINE web python manage.py dumpdata --natural-foreign --natural-primary -o data.json
```

2) Importa a Postgres:

```powershell
docker compose run --rm web python manage.py loaddata data.json
docker compose run --rm web python manage.py reset_sequences
```

## Endpoints base

- API root: `http://127.0.0.1:8000/api/`
- Health: `http://127.0.0.1:8000/api/health/`
- Admin: `http://127.0.0.1:8000/admin/`
