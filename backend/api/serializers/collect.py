import base64
import uuid

from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator

from api.models import Payment, Collect
from api.serializers import PaymentShowSerializer
from proninteam.constants import MAX_DIGITS, DECIMAL_PLACES


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=filename)

        return super().to_internal_value(data)


class CollectCreateSerializer(serializers.ModelSerializer):
    logo = Base64ImageField(required=True, allow_null=True)

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
    payments = PaymentShowSerializer(
        many=True,
        read_only=True,
    )
    summ = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Collect
        fields = (
            "id",
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
    new_amount = serializers.DecimalField(
        decimal_places=DECIMAL_PLACES,
        max_digits=MAX_DIGITS,
        write_only=True,
        validators=[MinValueValidator(0)],
    )
    new_stop_date = serializers.DateTimeField(write_only=True)

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
                f"Новая цель сбора не должна превышать общей суммы {collect.total_amount} р."
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
                f"Новая дата завершения сбора должна быть позже текущей даты завершения {collect.stop_date}"
            )
        return value

    def validate(self, data):
        collect = self.instance
        if collect.is_active:
            raise ValidationError("Сбор все еще активен")
        return data

    def update(self, instance, validated_data):
        new_amount = validated_data.pop("new_amount", None)
        new_stop_date = validated_data.pop("new_stop_date", None)
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


class CollectDeactivateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collect
        fields = ("id",)

    def validate(self, data):
        collect = self.instance
        if not collect.is_active:
            raise ValidationError("Сбор уже остановлен")
        return data

    def update(self, instance, validated_data):
        collect = instance
        collect.is_active = False
        collect.save()
        return collect
