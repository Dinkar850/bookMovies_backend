from rest_framework import serializers

from .models import Cinema, Seat


class CinemaListSerializer(serializers.ModelSerializer):
    """
    Serializer for cinemas in list:
    - returns city as strings (defined in def(__str__))
    """

    city = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cinema
        fields = ("id", "name", "address", "city")


class CinemaDetailsSerializer(CinemaListSerializer):
    """
    Serializer for cinema details that:
    - returns all details as in `CinemaListSerializer`
    - adds `rows` and `seats_per_row`
    """

    class Meta(CinemaListSerializer.Meta):
        fields = CinemaListSerializer.Meta.fields + ("rows", "seats_per_row")


class SeatSerializer(serializers.ModelSerializer):
    """Serializer for seat in cinema with `id`, `seat_row`, `seat_number`"""

    class Meta:
        model = Seat
        fields = ("id", "seat_row", "seat_number")
