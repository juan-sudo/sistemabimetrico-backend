from rest_framework import serializers

from apps.usuario.serializers import UserSerializer


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class AuthErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()

