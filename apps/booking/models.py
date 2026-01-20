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

    slot = models.ForeignKey(SlotModels.Slot, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModels.User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.status}: {self.user}, {self.slot}"


class Seat(CoreModels.TimeStampedModel):
    """
    Seat model that contains:

    - **seat_row**: row corresponding to the seat
    - **seat_number**: position of seat in that row
    - **booking**: foreign key reference to the Booking table(many-to-one)
    - **slot**: foreign key reference to the Slot table(many-to-one)
    """

    seat_row = models.CharField(max_length=1)
    seat_number = models.PositiveIntegerField()
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    slot = models.ForeignKey(SlotModels.Slot, on_delete=models.CASCADE, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["slot", "seat_row", "seat_number"],
                name="unique_seats_per_slot",
            )
        ]

    def save(self, *args, **kwargs):
        """Maintains consistent slots from booking id being saved directly as slot in seat"""

        if self.booking_id:
            self.slot = self.booking.slot
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.seat_row}{self.seat_number}"
