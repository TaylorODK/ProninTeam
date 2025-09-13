from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api.models import Like


class LikeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания лайка платежа.
    """

    class Meta:
        model = Like
        fields = ("id", "author", "payment")
        read_only_fields = ("author", "payment")

    def validate(self, data):
        author = self.context["author"]
        payment = self.context["payment"]
        if Like.objects.filter(author=author, payment=payment).exists():
            raise ValidationError("Лайк уже создан")
        return data
