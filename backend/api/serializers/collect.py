from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils import timezone

from api.models import Payment, Collect
from api.serializers import EventSerializer, PaymentShowSerializer


class CollectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collect
        fields = (
            "author",
            "name",
            "slug",
            "event_format",
            "event_reason",
            "event_date",
            "event_time",
            "event_place",
            "description",
            "min_payment",
            "target_amount",
            "total_amount",
            "logo",
            "stop_date",
        )
        read_only_fields = ("author",)


class CollectShowSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    payments = PaymentShowSerializer(
        many=True,
        read_only=True,
    )
    summ = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Collect
        fields = (
            "id",
            "author",
            "name",
            "slug",
            "reason",
            "description",
            "min_payment",
            "target_amount",
            "total_amount",
            "logo",
            "stop_date",
            "payments",
            "summ",
            "is_active",
            "status",
        )

    def get_summ(self, obj):
        return obj.payments_sum or 0

    def get_logo(self, obj):
        if not hasattr(obj, "logo") or not obj.logo:
            return None
        request = self.context.get("request")
        try:
            url = obj.logo.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None

    def get_status(self, obj):
        if not obj.is_active:
            return "Сбор завершен"
        return "Сбор открыт"


class CollectReactivateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collect
        fields = (
            "id",
            "new_amount",
            "new_stop_date",
        )

    def validate_new_amount(self, value):
        collect = self.instance
        if (
            collect
            and collect.total_amount != 0
            and value > collect.total_amount
        ):
            raise ValidationError(
                "Новая цель сбора не должна превышать общей суммы"
            )
        return value

    def validate_new_stop_date(self, value):
        if value <= timezone.now():
            raise ValidationError(
                "Нельзя указывать новую дату окончания сбора в прошлом"
            )
        collect = self.instance
        if collect and value <= collect.stop_date:
            raise ValidationError(
                "Новая дата завершения сбора должна быть позже текущей даты завершения"
            )
        return value

    def update(self, instance, validated_data):
        new_amount = validated_data.get("new_amount")
        new_stop_date = validated_data.get("new_stop_date")
        collect = instance
        if new_amount:
            collect.target_amount = new_amount
        if new_stop_date:
            collect.stop_date = new_stop_date
        collect.is_active = True
        collect.save()
        return collect


class CollectChangeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collect
        fields = (
            "id",
            "name",
            "description",
            "event_format",
            "event_format",
            "event_reason",
            "event_date",
        )
