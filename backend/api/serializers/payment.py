from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api.models import Payment, Collect
from api.serializers import CommentShowSerializer


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания платежей пользователями.
    Валидация сериализатора проверяет статус сбора (is_active),
    достижение общей суммы сборы, а также дату завершения сбора.
    В случае, если сбор не активен - платеж будет отклонен.
    В случае, если общая сумма сбора уже достигнута либо достигнута
    дата завершения сбора, статус сбора будет изменен на false и платеж
    будет отклонен.
    """

    class Meta:
        model = Payment
        fields = ("user", "collect", "amount", "hide_amount")

    def validate(self, data):
        collect = data.get("collect")
        if not collect.is_active:
            raise ValidationError("Сбор завершен, платежи более не принимаются")
        if collect.total_amount and collect.total_amount > 0:
            current_sum = collect.payment_set.aggregate(Sum("amount"))["amount__sum"] or 0
            if current_sum + data["amount"] > collect.total_amount:
                collect.is_active = False
                collect.save(update_fields=["is_active"])
                raise ValidationError("Сбор завершен, платежи более не принимаются")

        return data


class PaymentShowSerializer(serializers.ModelSerializer):
    """
    Сериализатор отображения данных о платежах
    В сериализаторе добавлены дополнительные поля:
     - show_amount отображение суммы платежа пользователя, в случае если пользователь
    при создании платежа указал hide_amount = True, в данных платежа вместо суммы будует
    указано "Сумма скрыта";
    - commets отображение комментариев пользователей;
    - comments_count отображение количества комментариев;
    - likes отображение количества лайков платежа.
    """

    show_amount = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
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
        return CommentShowSerializer(obj.prefetched_comments, many=True).data
