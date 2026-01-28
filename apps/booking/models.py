from django.core import exceptions, validators
from django.db import models

from apps.core import models as CoreModels
from apps.slot import models as SlotModels
from apps.user import models as UserModels


class Booking(CoreModels.TimeStampedModel):
    """
    Booking model that contains:

    - **status**: status of booking, booked(B), cancelled(C) or pending(P)
    - **slot**: foreign key relation with Slot table (many-to-one)
    - **user**: foreign key relation with User table (many-to-one)
    """

    class BookingStatus(models.TextChoices):
        BOOKED = (
            "B",
            "Booked",
        )
        CANCELLED = (
            "C",
            "Cancelled",
        )
        PENDING = "P", "Pending"

    status = models.CharField(
        max_length=1, choices=BookingStatus, default=BookingStatus.PENDING
    )

    slot = models.ForeignKey(
        SlotModels.Slot, on_delete=models.CASCADE, related_name="bookings"
    )
    user = models.ForeignKey(
        UserModels.User, on_delete=models.CASCADE, related_name="bookings"
    )

    def __str__(self):
        return f"{self.status}: {self.user}, {self.slot}"


class Seat(CoreModels.TimeStampedModel):
    """
    Seat model that contains:
    - **seat_row**: row corresponding to the seat
    - **seat_number**: position of seat in that row
    - **booking**: foreign key reference to the Booking table(many-to-one)
    """

    seat_row = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1)],
        help_text="Specify row of the seat (1-indexed)",
    )
    seat_number = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1)],
        help_text="Specify position of the seat in the row (1-indexed)",
    )
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="seats")

    def clean(self):
        """
        Raises exception in admin panel only, if:
        - another confirmed seat with the same row, number, slot derived from booking_id is being added
        - entered seat row is not in defined range
        - entered seat number is not in defined range
        """
        super().clean()

        if not self.booking_id:
            return

        cinema = self.booking.slot.cinema

        # Checks if entered seat row is greater than rows for the linked cinema
        if self.seat_row > cinema.rows:
            raise exceptions.ValidationError(f"Row must be between 1 and {cinema.rows}")

        # Checks if entered seat number is greater than seats for the linked cinema
        if self.seat_number > cinema.seats_per_row:
            raise exceptions.ValidationError(
                f"Seat number must be between 1 and {cinema.seats_per_row}"
            )

        # Checks if another confirmed seat for the slot of a previous booking already exists
        if (
            Seat.objects.filter(
                booking__slot_id=self.booking.slot_id,
                booking__status=Booking.BookingStatus.BOOKED,
                seat_row=self.seat_row,
                seat_number=self.seat_number,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise exceptions.ValidationError(
                "Another confirmed seat with the same seat row, seat number and slot already exists"
            )

    def __str__(self):
        return f"{self.seat_row},{self.seat_number}"
