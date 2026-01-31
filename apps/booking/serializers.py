from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.cinema import serializers as CinemaSerializers
from apps.cinema.models import Seat
from apps.slot.models import Slot
from apps.slot.serializers import SlotListSerializer

from .constants import MAX_SEATS_PER_BOOKING
from .models import Booking


class BookingCreateRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for booking creation that has:
    - Structure of request: {slot:integer, seats: {integer, integer}
    """

    # Validation: Existence of seat in cinema and that it is active
    seats = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Seat.objects.filter(is_active=True).select_related("cinema__city"),
        source="seat",
    )

    # Validation: Existence of an active slot beyond current date and time
    slot = serializers.PrimaryKeyRelatedField(
        queryset=Slot.objects.filter(
            is_active=True, schedule__gte=timezone.now()
        ).select_related("cinema__city", "movie")
    )

    class Meta:
        model = Booking
        fields = ["slot", "seats"]

    def validate(self, attrs):
        slot = attrs["slot"]
        seats = attrs["seat"]
        cinema = slot.cinema
        seat_ids = [seat.id for seat in seats]

        # Validation: Duplicate seats are not passed
        if len(seat_ids) < len(set(seat_ids)):
            raise serializers.ValidationError(
                {"seats": "Duplicate seat(s) found in request"}
            )

        # Validation: Maximum MAX_SEATS_PER_BOOKING seats can be booked per booking
        if len(seats) > MAX_SEATS_PER_BOOKING:
            raise serializers.ValidationError(
                {
                    "seats": f"More than {MAX_SEATS_PER_BOOKING} seats cannot be booked per booking"
                }
            )

        # Validation: Entered seat does not belong to the cinema of the slot

        invalid_seat_ids = [seat.id for seat in seats if seat.cinema_id != cinema.id]
        # list.sort(invalid_seat_ids)

        if invalid_seat_ids:
            raise serializers.ValidationError(
                {
                    "seats": f"Some or all seats do not belong to the selected slot's cinema: {invalid_seat_ids}"
                }
            )

        # Validation: Entered seat is already booked for the slot

        already_booked_seat_ids = list(
            Seat.objects.filter(
                bookings__slot=slot,
                bookings__status=Booking.BookingStatus.BOOKED,
                id__in=seat_ids,
            )
            .values_list("id", flat=True)
            .order_by("id")
        )

        if already_booked_seat_ids:
            raise serializers.ValidationError(
                {
                    "seats": f"Some or all seats are already booked for this slot: {already_booked_seat_ids}"
                }
            )

        return attrs

    def create(self, validated_data):
        slot = validated_data["slot"]
        seats = validated_data["seat"]

        user = self.context["request"].user

        # Prevents creation of bookings without setting seats or vice-versa
        with transaction.atomic():
            booking = Booking.objects.create(
                user=user,
                slot=slot,
                status=Booking.BookingStatus.BOOKED,
            )

            booking.seat.set(seats)

        return booking


class BookingCreateResponseSerializer(serializers.ModelSerializer):
    """Serializer to be used for returning `seats`, `seat_count` and `total_price` for the current booking"""

    seats = CinemaSerializers.SeatSerializer(many=True, read_only=True, source="seat")
    seat_count = serializers.IntegerField(source="seat.count", read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "created_at",
            "status",
            "total_price",
            "seat_count",
            "seats",
        ]

    def get_total_price(self, obj):
        return obj.seat.count() * obj.slot.price


class BookingListSerializer(BookingCreateResponseSerializer):
    """
    Serializer to be used for returning list of all bookings
    """

    slot = SlotListSerializer(read_only=True)

    class Meta(BookingCreateResponseSerializer.Meta):
        fields = BookingCreateResponseSerializer.Meta.fields + ["slot"]
