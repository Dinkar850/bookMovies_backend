from django.db import models, transaction
from django.utils import timezone
from rest_framework import serializers

from apps.slot import models as SlotModels
from apps.slot import serializers as SlotSerializers

from .constants import MAX_SEATS_PER_BOOKING
from .models import Booking, Seat

Slot = SlotModels.Slot


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["seat_row", "seat_number"]


class BookingListSerializer(serializers.ModelSerializer):
    """
    Serializer to be used for:
    - returning list of all bookings
    - specific booking
    - response of create bookings request
    """

    total_price = serializers.SerializerMethodField()
    slot = SlotSerializers.SlotListSerializer(read_only=True)
    seats = SeatSerializer(many=True, read_only=True)
    seat_count = serializers.IntegerField(source="seats.count", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "status",
            "total_price",
            "created_at",
            "seat_count",
            "seats",
            "slot",
        ]

    def get_total_price(self, obj):
        return obj.seats.count() * obj.slot.price


class BookingCreateSerializer(serializers.Serializer):
    """
    Serializer for booking creation that with:
    - Strucutre of request: {slot_id:integer, seats: {{seat_row:integer, seat_number:integer}, ...multiple seats}}
    """

    # Also validates using queryset defined inside __init__ function that was required to tag the instance creation time to current date and time
    slot_id = serializers.PrimaryKeyRelatedField(queryset=Slot.objects.none())
    seats = SeatSerializer(many=True, allow_empty=False)

    def __init__(self, *args, **kwargs):
        """Called during creation of each serializer instance and sets now to the time the instance was created for checking if slot is not a past one and is active"""
        super().__init__(*args, **kwargs)

        # Validation: Existence of an active slot that exists beyond current date and time
        self.fields["slot_id"].queryset = Slot.objects.select_related("cinema").filter(
            is_active=True,
            schedule__gte=timezone.now(),
        )

    def validate(self, attrs):
        slot = attrs["slot_id"]
        seats = attrs["seats"]

        oringinally_entered_seats = [
            (seat["seat_row"], seat["seat_number"]) for seat in seats
        ]
        entered_seats = set(oringinally_entered_seats)

        # Validation: Duplicate seats are not passed
        if len(entered_seats) < len(oringinally_entered_seats):
            raise serializers.ValidationError({"seats": "Duplicate seat(s) in request"})

        # Validation: Maximum MAX_SEATS_PER_BOOKING seats can be booked per booking
        if len(entered_seats) > MAX_SEATS_PER_BOOKING:
            raise serializers.ValidationError(
                {
                    "seats": f"More than {MAX_SEATS_PER_BOOKING} seats can't be booked per booking"
                }
            )

        # Stores `seat_row, seat_number` pairs of MAX_SEATS_PER_BOOKING Q query filters to check existence of already booked seats
        q_pairs = models.Q()

        cinema = slot.cinema

        for row, number in entered_seats:
            # Validation: Seat row is greater than  less than number of rows linked to cinema of that slot
            if row > cinema.rows:
                raise serializers.ValidationError(
                    {"seat_row": f"seat_row cannot exceed {cinema.rows} "}
                )

            # Validation: Seat number is less than number of seats per row linked to cinema of that slot
            if number > cinema.seats_per_row:
                raise serializers.ValidationError(
                    {
                        "seat_number": f"seat_number cannot exceed {cinema.seats_per_row} "
                    }
                )

            q_pairs |= models.Q(seat_row=row, seat_number=number)

        booked_query_set = (
            Seat.objects.filter(
                booking__slot_id=slot.id,
                booking__status=Booking.BookingStatus.BOOKED,
            )
            .filter(q_pairs)
            .values_list("seat_row", "seat_number")
        )

        # Stores seats that were entered for booking but are already booked previously by some other user
        entered_but_previously_booked_seats = list(booked_query_set)

        # Validation: Seat pair entered is not already booked with the BOOKED status
        if entered_but_previously_booked_seats:
            raise serializers.ValidationError(
                {
                    "seats": f"Seat(s) already booked for this slot: {entered_but_previously_booked_seats}"
                }
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        slot = validated_data["slot_id"]
        seats = validated_data["seats"]

        # Prevents only one of the queries to succeed. Using atomic, if one of the queries fail, whole transaction fails which prevents creation of bookings without seats or vice-versa
        with transaction.atomic():
            booking = Booking.objects.create(
                user=user,
                slot=slot,
                status=Booking.BookingStatus.BOOKED,
            )

            Seat.objects.bulk_create(
                [
                    Seat(
                        booking=booking,
                        seat_row=seat["seat_row"],
                        seat_number=seat["seat_number"],
                    )
                    for seat in seats
                ]
            )

        return booking
