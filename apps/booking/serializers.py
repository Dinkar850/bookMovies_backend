from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.cinema import serializers as CinemaSerializers
from apps.cinema.models import Seat
from apps.slot.models import Slot
from apps.slot.serializers import SlotListSerializer

from .constants import BookingDefaults, BookingErrors
from .models import Booking


class BookingCreateRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for creating booking

    Structure:
    {
        "slot": int,
        "seats": [int]
    }

    Notes:
        - Seats must belong to slot cinema
        - Seats must be active
        - Seats must not be empty
        - Duplicate seats not allowed
        - Seats must not already be booked
        - Maximum seats limited by MAX_SEATS_PER_BOOKING
        - Seat and active slot must exist
    """

    # Validation: Existence of seat in cinema and that it is active
    seats = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Seat.objects.filter(is_active=True), allow_empty=False
    )

    # Validation: Existence of an active slot beyond current date and time
    slot = serializers.PrimaryKeyRelatedField(
        queryset=Slot.objects.filter(is_active=True, schedule__gte=timezone.now())
    )

    class Meta:
        model = Booking
        fields = ("slot", "seats")

    def validate(self, attrs):
        """
        Validates the following before insertion:
        - Duplicate seats are not passed
        - Maximum MAX_SEATS_PER_BOOKING seats can be booked per booking
        - Entered seat does not belong to the cinema of the slot
        - Entered seat is already booked for the slot
        """

        slot = attrs["slot"]
        seats = attrs["seats"]
        cinema = slot.cinema
        seat_ids = [seat.id for seat in seats]

        # Validation: Duplicate seats are not passed
        if len(set(seat_ids)) < len(seat_ids):
            raise serializers.ValidationError({"seats": BookingErrors.DUPLICATE_SEATS})

        # Validation: Maximum MAX_SEATS_PER_BOOKING seats can be booked per booking
        if len(seats) > BookingDefaults.MAX_SEATS_PER_BOOKING:
            raise serializers.ValidationError(
                {"seats": BookingErrors.EXCEEDED_SEATS_LIMIT}
            )

        # Validation: Entered seat does not belong to the cinema of the slot

        invalid_seat_ids = [seat.id for seat in seats if seat.cinema_id != cinema.id]

        if invalid_seat_ids:
            raise serializers.ValidationError(
                {"seats": f"{BookingErrors.INVALID_CINEMA}: {invalid_seat_ids}"}
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
                    "seats": f"{BookingErrors.SEATS_ALREADY_BOOKED}: {already_booked_seat_ids}"
                }
            )

        return attrs

    def create(self, validated_data):
        """
        - Creates boooking based on the slot
        - Sets the related seat in the through table with corresponding booking ID
        - Uses atomic transaction for performing the above operations
        """

        slot = validated_data["slot"]
        seats = validated_data["seats"]

        user = self.context["request"].user

        # Prevents creation of bookings without setting seats or vice-versa
        with transaction.atomic():
            booking = Booking.objects.create(
                user=user,
                slot=slot,
                status=Booking.BookingStatus.BOOKED,
            )

            booking.seats.set(seats)

        return booking


class BookingCreateResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for booking create response

    Structure:
    {
        "id": int,
        "created_at": datetime,
        "status": string,
        "total_price": decimal,
        "seat_count": int,
        "seats": [
            {
                "id": int,
                "seat_row": int,
                "seat_number": int
            }
        ]
    }

    Notes:
        - total_price computed dynamically
        - seat_count derived from seats
    """

    seats = CinemaSerializers.SeatSerializer(many=True, read_only=True)
    seat_count = serializers.IntegerField(source="seats.count", read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            "id",
            "created_at",
            "status",
            "total_price",
            "seat_count",
            "seats",
        )

    def get_total_price(self, obj):
        return obj.seats.count() * obj.slot.price


class BookingListSerializer(BookingCreateResponseSerializer):
    """
    Serializer for listing bookings

    Structure:
    {
        "id": int,
        "created_at": datetime,
        "status": string,
        "total_price": decimal,
        "seat_count": int,
        "seats": [
            {
                "id": int,
                "seat_row": int,
                "seat_number": int
            }
        ],
        "slot": {
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
    }
    """

    slot = SlotListSerializer(read_only=True)

    class Meta(BookingCreateResponseSerializer.Meta):
        fields = BookingCreateResponseSerializer.Meta.fields + ("slot",)
