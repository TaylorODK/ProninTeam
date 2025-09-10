from rest_framework import serializers

from api.models import Like


class LikeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания лайка платежа.
    """

    class Meta:
        model = Like
        fields = ("id", "user", "payment")
