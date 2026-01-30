from django.db import models

from apps.cinema import models as CinemaModels
from apps.core import models as CoreModels
from apps.slot import models as SlotModels
from apps.user import models as UserModels


class Booking(CoreModels.TimeStampedModel):
    """
    Booking model that contains:

    - **status**: status of booking, booked(B), cancelled(C) or pending(P)
    - **slot**: foreign key relation with Slot table (many-to-one)
    - **user**: foreign key relation with User table (many-to-one)
    - **seat**: foreign key relation with Seat table (many-to-many)
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
    seat = models.ManyToManyField(CinemaModels.Seat, related_name="bookings")

    def __str__(self):
        return f"{self.status}:{self.user}-{self.slot}"
