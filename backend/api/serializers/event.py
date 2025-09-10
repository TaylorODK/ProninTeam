from rest_framework import serializers

from api.models import Event


class EventSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и отображения события связанного со сборами.
    """

    class Meta:
        model = Event
        fields = (
            "id",
            "event_format",
            "event_date",
            "event_time",
            "event_place",
        )
