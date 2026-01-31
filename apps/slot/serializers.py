from rest_framework import serializers

from apps.cinema import serializers as CinemaSerializers
from apps.movie.serializers import MovieNameSerializer

from .models import Slot


class SlotListSerializer(serializers.ModelSerializer):
    """
    Serializer for slots that:
    - has nested relation with movies to show movie's id and name
    - has nested relation with cinemas to show cinema's id, name, address and city
    - additionally returns slot's id, schedule and price
    """

    movie = MovieNameSerializer(read_only=True)
    cinema = CinemaSerializers.CinemaListSerializer(read_only=True)
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
    - adds `active_seats` in that slot that gets set in `SlotDetailsViewSerializer`
    """

    cinema = CinemaSerializers.CinemaDetailsSerializer(read_only=True)
    booked_seats = CinemaSerializers.SeatSerializer(many=True, read_only=True)
    active_seats = CinemaSerializers.SeatSerializer(
        many=True, read_only=True, source="cinema.active_seats"
    )

    class Meta(SlotListSerializer.Meta):
        fields = SlotListSerializer.Meta.fields + ["booked_seats", "active_seats"]
