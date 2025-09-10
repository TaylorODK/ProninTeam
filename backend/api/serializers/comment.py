from rest_framework import serializers

from api.models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания комментария.
    """

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "comment",
        )


class CommentShowSerializer(serializers.ModelSerializer):
    """
    Сериализатор отображения комментария.
    В комментарии отображается Имя Фамилия пользователя.
    Если данные поля пустые, то будет отображаться username
    """

    username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "username",
            "comment",
            "created_at",
        )

    def get_username(self, obj):
        full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return full_name or obj.username
