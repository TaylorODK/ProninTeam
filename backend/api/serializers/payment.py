from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils import timezone
from django.db.models import Sum

from api.models import Payment, Collect
from api.serializers import CommentShowSerializer


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания платежей пользователями.
    Валидация сериализатора проверяет следующее:
    - статус сбора;
    - достижение до момента платежа максимальной суммы сбора;
    - достижение даты завершения сбора;
    - достигает ли сумма платежа минимальной суммы платежа сбора.
    """

    class Meta:
        model = Payment
        fields = ("author", "collect", "amount", "hide_amount")
        read_only_fields = ("author", "collect")

    def validate(self, data):
        collect = self.context["collect"]
        if not collect.is_active:
            raise ValidationError(
                "Сбор завершен, платежи более не принимаются"
            )
        if collect.total_amount:
            current_sum = (
                collect.payments.aggregate(Sum("amount"))["amount__sum"] or 0
            )
            if current_sum + data["amount"] > collect.total_amount:
                collect.is_active = False
                collect.save(update_fields=["is_active"])
                raise ValidationError(
                    "Сбор завершен, платежи более не принимаются"
                )
        if collect.stop_date <= timezone.now():
            collect.is_active = False
            collect.save(update_fields=["is_active"])
            raise ValidationError(
                "Сбор завершен по достижению даты завершения сбора"
            )
        if collect.min_payment > data.get("amount"):
            raise ValidationError(
                f"Минимальная сумма платежа {collect.min_payment}"
            )
        return data


class PaymentShowSerializer(serializers.ModelSerializer):
    """
    Сериализатор отображения данных о платежах
    В сериализаторе добавлены дополнительные поля:
     - show_amount отображение суммы платежа пользователя,
    в случае если пользователь при создании платежа указал
    hide_amount = True, в данных платежа вместо суммы будует
    указано "Сумма скрыта";
    - commets отображение комментариев пользователей;
    - comments_count отображение количества комментариев;
    - likes отображение количества лайков платежа.
    """

    show_amount = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    likes = serializers.IntegerField(source="likes.count", read_only=True)
    comments_count = serializers.IntegerField(
        source="comments.count", read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "author",
            "collect",
            "show_amount",
            "created_at",
            "likes",
            "comments_count",
            "comments",
        )

    def get_show_amount(self, obj):
        amount = obj.amount
        hide_amount = obj.hide_amount
        if hide_amount:
            return "Сумма скрыта"
        return f"{amount} р."

    def get_comments(self, obj):
        return CommentShowSerializer(obj.comments, many=True).data
