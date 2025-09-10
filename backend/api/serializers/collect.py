from rest_framework import serializers

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
    payments = PaymentShowSerializer(many=True, read_only=True,)
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
