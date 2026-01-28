from django.db.models import Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from apps.booking import models as BookingModels

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
            .select_related("movie", "cinema", "cinema__city", "language")
            .prefetch_related("movie__language")
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
    - including cinema's structure (`rows`, `seat_per_row`)
    - fetching booked seats for this slot
    """

    serializer_class = SlotDetailsSerializer

    def get_queryset(self):
        # queryset for prefetching ordered booking seats from seats in Booking model to be used in `bookings_queryset`
        booked_seats_queryset = BookingModels.Seat.objects.order_by(
            "seat_row", "seat_number"
        )

        # queryset for prefetching confirmed seats from bookings in Slot model using the previously defined `booked_seats_queryset` to be used in final queryset
        confirmed_bookings_queryset = BookingModels.Booking.objects.filter(
            status=BookingModels.Booking.BookingStatus.BOOKED
        ).prefetch_related(
            Prefetch("seats", queryset=booked_seats_queryset, to_attr="booked_seats")
        )

        # queryset for retrieving booked seats from slots -> bookings -> seats
        return self.base_queryset().prefetch_related(
            Prefetch(
                "bookings",
                queryset=confirmed_bookings_queryset,
                to_attr="confirmed_bookings",
            ),
        )
