from rest_framework.routers import DefaultRouter

from .views import PersonalTurnoViewSet, TurnoBloqueHorarioViewSet, TurnoViewSet


router = DefaultRouter()
router.register("turnos", TurnoViewSet, basename="turnos")
router.register("turno-bloques-horario", TurnoBloqueHorarioViewSet, basename="turno-bloques-horario")
router.register("personal-turnos", PersonalTurnoViewSet, basename="personal-turnos")

urlpatterns = router.urls
