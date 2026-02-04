from rest_framework import serializers

from apps.cinema import serializers as CinemaSerializers
from apps.movie.serializers import MovieNameSerializer
from apps.slot.models import Slot


class SlotListSerializer(serializers.ModelSerializer):
    """
    Serializer for slot list

    Structure:
    {
        "id": int,
        "schedule": datetime,
        "price": decimal,
        "language": string,
        "movie": {
            "id": int,
            "name": string
        },
        "cinema": {
            "id": int,
            "name": string,
            "address": string,
            "city": string
        }
    }

    Notes:
        - Movie nested using MovieNameSerializer
        - Cinema nested using CinemaListSerializer
        - Language returned using __str__
    """

    movie = MovieNameSerializer(read_only=True)
    cinema = CinemaSerializers.CinemaListSerializer(read_only=True)
    language = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Slot
        fields = ("id", "schedule", "price", "language", "movie", "cinema")


class SlotDetailsSerializer(SlotListSerializer):
    """
    Serializer for slot details

    Structure:
    {
        "id": int,
        "schedule": datetime,
        "price": decimal,
        "language": string,
        "movie": {
            "id": int,
            "name": string
        },
        "cinema": {
            "id": int,
            "name": string,
            "address": string,
            "city": string,
            "rows": int,
            "seats_per_row": int
        },
        "booked_seats": [
            {
                "id": int,
                "seat_row": int,
                "seat_number": int
            }
        ],
        "active_seats": [
            {
                "id": int,
                "seat_row": int,
                "seat_number": int
            }
        ]
    }

    Notes:
        - booked_seats populated dynamically in view
        - active_seats populated from cinema relation
    """

    cinema = CinemaSerializers.CinemaDetailsSerializer(read_only=True)
    booked_seats = CinemaSerializers.SeatSerializer(many=True, read_only=True)
    active_seats = CinemaSerializers.SeatSerializer(
        many=True, read_only=True, source="cinema.active_seats"
    )

    class Meta(SlotListSerializer.Meta):
        fields = SlotListSerializer.Meta.fields + ("booked_seats", "active_seats")
