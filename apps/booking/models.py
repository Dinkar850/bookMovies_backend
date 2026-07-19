from django.db import models

from apps.cinema.models import Seat
from apps.core.models import TimeStampedModel
from apps.slot.models import Slot
from apps.user.models import User


class Booking(TimeStampedModel):
    """
    Booking model that contains:

    - **status**: status of booking, booked(B), cancelled(C) or pending(P)
    - **slot**: foreign key relation with Slot table (many-to-one)
    - **user**: foreign key relation with User table (many-to-one)
    - **seats**: foreign key relation with Seat table (many-to-many)
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
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    seats = models.ManyToManyField(Seat, related_name="bookings")

    def __str__(self):
        return f"Booking #{self.id} ({self.status})"
