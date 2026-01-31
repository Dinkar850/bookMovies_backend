from django.db.models import Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from apps.booking import models as BookingModels
from apps.cinema import models as CinemaModels

from .filters import SlotFilter
from .models import Slot
from .serializers import SlotDetailsSerializer, SlotListSerializer


class SlotBaseMixin:
    def get_now(self):
        """Returns now to a predefined time"""

        return timezone.now()

    def base_queryset(self):
        """Sets queryset for obtaining active slots beyond current date and time plus optimizes fetch using select and prefetch related"""

        now = self.get_now()

        return (
            Slot.objects.filter(is_active=True, schedule__gte=now)
            .order_by("schedule")
            .select_related("movie", "cinema__city", "language")
        )


class SlotListView(SlotBaseMixin, generics.ListAPIView):
    """
    View that is responsible for returning list of active slots with schedule greater than current date and time:
    - filtered based on `SlotFilter`
    """

    serializer_class = SlotListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SlotFilter

    def get_queryset(self):
        return self.base_queryset()


class SlotDetailsView(SlotBaseMixin, generics.RetrieveAPIView):
    """
    View that is responsible for:
    - returning detailed active slot with schedule greater than current date and time
    - including cinema's structure (`rows`, `seats_per_row`)
    - fetching booked seats for this slot
    """

    serializer_class = SlotDetailsSerializer

    def get_queryset(self):
        """Populates `inactive_seats` and `booked_seats` attribute for `confirmed_bookings` by using a custom queryset"""

        # queryset for fetching and ordering all seats
        cinema_seats = CinemaModels.Seat.objects.order_by("seat_row", "seat_number")

        # queryset for filtering confirmed bookings and then fetching only active seats for each booking
        confirmed_bookings_qs = BookingModels.Booking.objects.filter(
            status=BookingModels.Booking.BookingStatus.BOOKED
        ).prefetch_related(
            Prefetch(
                "seat",
                queryset=cinema_seats.filter(is_active=True),
                to_attr="booked_seats",
            )
        )

        return self.base_queryset().prefetch_related(
            # prefetch responsible for populating confirmed_bookings attribute in slot object with booked status and also populating the booked_seats attribute for each confirmed_booking
            Prefetch(
                "bookings",
                queryset=confirmed_bookings_qs,
                to_attr="confirmed_bookings",
            ),
            # prefetch responsible for populating inactive_seats attribute in slot object for that cinema
            Prefetch(
                "cinema__seats",
                queryset=cinema_seats.filter(is_active=False),
                to_attr="inactive_seats",
            ),
        )

    def get_object(self):
        """Get the corresponding slot object as referenced by `pk` in `self.get_queryset()` and set the `booked_seats` attribute to be accessed by `SlotDetailsSerializer`"""

        slot = super().get_object()

        slot.booked_seats = [
            seat for booking in slot.confirmed_bookings for seat in booking.booked_seats
        ]

        return slot
