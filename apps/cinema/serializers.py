from rest_framework import serializers

from apps.cinema.models import Cinema, Seat


class CinemaListSerializer(serializers.ModelSerializer):
    """
    Serializer for cinema list

    Structure:
    {
        "id": int,
        "name": string,
        "address": string,
        "city": string
    }

    Notes:
        - City returned using __str__
    """

    city = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cinema
        fields = ("id", "name", "address", "city")


class CinemaDetailsSerializer(CinemaListSerializer):
    """
    Serializer for cinema details

    Structure:
    {
        "id": int,
        "name": string,
        "address": string,
        "city": string,
        "rows": int,
        "seats_per_row": int
    }
    """

    class Meta(CinemaListSerializer.Meta):
        fields = CinemaListSerializer.Meta.fields + ("rows", "seats_per_row")


class SeatSerializer(serializers.ModelSerializer):
    """
    Serializer for seat

    Structure:
    {
        "id": int,
        "seat_row": int,
        "seat_number": int
    }
    """

    class Meta:
        model = Seat
        fields = ("id", "seat_row", "seat_number")
