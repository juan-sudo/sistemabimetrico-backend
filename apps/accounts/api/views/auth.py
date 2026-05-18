from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.api.serializers import AuthErrorSerializer, LoginRequestSerializer, LoginResponseSerializer
from apps.usuario.serializers import UserSerializer


User = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiResponse(response=AuthErrorSerializer, description="Faltan credenciales"),
            401: OpenApiResponse(response=AuthErrorSerializer, description="Credenciales invalidas"),
        },
        tags=["Autenticacion"],
        summary="Iniciar sesion",
    )
    def post(self, request):
        username = (request.data.get("username") or request.data.get("email") or "").strip()
        password = request.data.get("password") or ""

        if not username or not password:
            return Response(
                {"detail": "username/email y password son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        candidate_usernames = list(
            dict.fromkeys(
                [username]
                + list(
                    User.objects.filter(
                        Q(username__iexact=username) | Q(email__iexact=username)
                    ).values_list("username", flat=True)
                )
            )
        )

        user = None
        for candidate in candidate_usernames:
            user = authenticate(request, username=candidate, password=password)
            if user:
                break

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

    @extend_schema(
        responses={200: UserSerializer},
        tags=["Autenticacion"],
        summary="Perfil del usuario autenticado",
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)
