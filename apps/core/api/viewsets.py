from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]


__all__ = ["BaseModelViewSet"]
