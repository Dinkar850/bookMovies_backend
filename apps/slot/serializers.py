from rest_framework import serializers

from apps.cinema import models as CinemaModels
from apps.cinema import serializers as CinemaSerializers
from apps.movie import models as MovieModels

from .models import Slot

# Serializers for nested relationships:


class MovieNestedSerializer(serializers.ModelSerializer):
    """Serializer for nested relation with movies through slots"""

    class Meta:
        model = MovieModels.Movie
        fields = ["id", "name"]


class CinemaNestedSerializer(serializers.ModelSerializer):
    """Serializer for nested relation with cinemas through slots"""

    city = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CinemaModels.Cinema
        fields = ["id", "name", "address", "city"]


class CinemaDetailsNestedSerializer(CinemaNestedSerializer):
    """Serializer that inherits `CinemaNestedSerializer` for adding `rows` and `seat_per_row` fields"""

    class Meta(CinemaNestedSerializer.Meta):
        fields = CinemaNestedSerializer.Meta.fields + ["rows", "seats_per_row"]


# Main serializers:


class SlotListSerializer(serializers.ModelSerializer):
    """
    Serializer for slots that:
    - has nested relation with movies to show movie's id and name
    - has nested relation with cinemas to show cinema's id, name, address and city
    - additionally returns slot's id, schedule and price
    """

    movie = MovieNestedSerializer(read_only=True)
    cinema = CinemaNestedSerializer(read_only=True)
    language = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Slot
        fields = ["id", "schedule", "price", "language", "movie", "cinema"]


class SlotDetailsSerializer(SlotListSerializer):
    """
    Serializer for showing a detailed slot that contains:
    - all fields from `SlotListSerializer`
    - adds `seat_per_row` and `rows` for cinema details in case slot is selected from a movie details page
    - adds `booked_seats` in that slot that gets set in `SlotDetailsViewSerializer`
    - adds `inactive_seats` in that slot that gets set in `SlotDetailsViewSerializer`
    """

    cinema = CinemaDetailsNestedSerializer(read_only=True)
    booked_seats = CinemaSerializers.SeatSerializer(many=True, read_only=True)
    inactive_seats = CinemaSerializers.SeatSerializer(
        many=True, read_only=True, source="cinema.inactive_seats"
    )

    class Meta(SlotListSerializer.Meta):
        fields = SlotListSerializer.Meta.fields + ["booked_seats", "inactive_seats"]
