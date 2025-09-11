from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django.contrib.auth.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
            "password": {"write_only": True},
        }
