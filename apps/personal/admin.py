from django.contrib import admin

from .models.dispositivo import Dispositivo
from .models.personal import Personal
from .models.ubicacion_geografica import UbicacionGeografica

for model in [UbicacionGeografica, Personal, Dispositivo]:
    admin.site.register(model)
