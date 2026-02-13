from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.booking.constants import BookingDefaults, BookingErrors
from apps.booking.models import Booking
from apps.cinema import serializers as CinemaSerializers
from apps.cinema.models import Seat
from apps.slot.models import Slot
from apps.slot.serializers import SlotListSerializer


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

    seats = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )

    # Validation: Existence of an active slot beyond current date and time
    slot = serializers.PrimaryKeyRelatedField(
        queryset=Slot.active_objects.filter(schedule__gte=timezone.now()),
        write_only=True,
    )

    class Meta:
        model = Booking
        fields = ("slot", "seats")

    def validate_seats(self, seat_ids):
        """
        Validate seats for:
        - No duplicate seat(s) are entered
        - Maximum MAX_SEATS_PER_BOOKING are booked
        """

        # Validation: Duplicate seats are not passed
        if len(set(seat_ids)) < len(seat_ids):
            raise serializers.ValidationError(BookingErrors.DUPLICATE_SEATS)

        # Validation: Maximum MAX_SEATS_PER_BOOKING seats can be booked per booking
        if len(seat_ids) > BookingDefaults.MAX_SEATS_PER_BOOKING:
            raise serializers.ValidationError(BookingErrors.EXCEEDED_SEATS_LIMIT)

        return seat_ids

    def validate(self, attrs):
        """
        Validates the following before insertion:
        - Entered seat belongs to the cinema of the slot
        - Entered seat is not already booked for that slot
        """

        slot = attrs["slot"]
        seat_ids = attrs["seats"]
        cinema = slot.cinema

        # Validation: Entered seat belongs to the cinema of the slot

        seats = list(Seat.active_objects.filter(id__in=seat_ids, cinema=cinema))

        found_ids = {seat.id for seat in seats}
        requested_ids = set(seat_ids)

        missing_ids = requested_ids - found_ids

        if missing_ids:
            raise serializers.ValidationError(
                {"seats": f"{BookingErrors.INVALID_CINEMA}: {list(missing_ids)}"}
            )

        # Validation: Entered seat is not already booked for that slot

        already_booked_seat_ids = list(
            Seat.active_objects.filter(
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
        - Creates boooking based on the slot with row level locking
        - Sets the related seat in the through table with corresponding booking ID
        - Uses atomic transaction for performing the above operations
        """

        slot = validated_data["slot"]
        seat_ids = validated_data["seats"]

        user = self.context["request"].user

        with transaction.atomic():
            # Lock rows
            seats = list(
                Seat.active_objects.select_for_update().filter(  # row lock
                    id__in=seat_ids, cinema=slot.cinema
                )
            )

            # Re-check booking inside lock
            already_booked = Seat.active_objects.filter(
                bookings__slot=slot,
                bookings__status=Booking.BookingStatus.BOOKED,
                id__in=seat_ids,
            ).exists()

            if already_booked:
                raise serializers.ValidationError(
                    {"seats": BookingErrors.SEATS_ALREADY_BOOKED}
                )

            # Create booking if not already booked before
            booking = Booking.objects.create(
                user=user,
                slot=slot,
                status=Booking.BookingStatus.BOOKED,
            )

            # Set seat ids corresponding to each booking id
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
