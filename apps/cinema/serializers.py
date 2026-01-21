from rest_framework import serializers

from apps.slot import serializers as SlotSerializers

from .models import Cinema


class CinemaListSerializer(serializers.ModelSerializer):
    """
    Serializer for cinemas in list:
    - returns city as strings (defined in def(__str__))
    """

    city = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cinema
        fields = ["id", "name", "address", "city"]


class CinemaDetailsSerializer(CinemaListSerializer):
    """
    Serializer for cinema details with slots that:
    - returns all details as in `CinemaListSerializer`
    - adds rows, seats_per_row and slots information fetched by `CinemaDetailsView` in attribute `active_slots`
    """

    slots = SlotSerializers.SlotListSerializer(
        source="active_slots", many=True, read_only=True
    )

    class Meta(CinemaListSerializer.Meta):
        fields = CinemaListSerializer.Meta.fields + ["rows", "seats_per_row", "slots"]
