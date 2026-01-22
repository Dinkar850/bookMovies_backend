from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import generics

from apps.booking import models as BookingModels
from apps.core import views as CoreViews

from .filters import SlotFilter
from .models import Slot
from .serializers import SlotDetailsSerializer, SlotListSerializer


class SlotBaseMixin:
    """Sets queryset for obtaining active slots beyond current date and time plus optimizes fetch using select and prefetch related"""

    def base_queryset(self, now):
        return (
            Slot.objects.filter(is_active=True, date_time__gte=now)
            .select_related("movie", "cinema", "cinema__city", "language")
            .prefetch_related("movie__language")
        )


class SlotListView(SlotBaseMixin, CoreViews.ListView):
    """
    View that is responsible for returning list of active slots with date_time greater than current date and time:
    - paginated and sorted by `created_at` and `id`
    - filtered based on `SlotFilter`
    """

    serializer_class = SlotListSerializer
    filterset_class = SlotFilter

    def get_queryset(self):
        now = timezone.now()
        return self.base_queryset(now)


class SlotDetailsView(SlotBaseMixin, generics.RetrieveAPIView):
    """
    View that is responsible for:
    - returning detailed active slot with date_time greater than current date and time
    - including cinema's structure (`rows`, `seat_per_row`)
    - fetching booked seats for this slot
    """

    serializer_class = SlotDetailsSerializer

    def get_queryset(self):
        now = timezone.now()

        # queryset for prefetching ordered booking seats from seats in Booking model to be used in `bookings_queryset`
        booked_seats_queryset = BookingModels.Seat.objects.filter(
            booking__status=BookingModels.Booking.BookingStatus.BOOKED
        ).order_by("seat_row", "seat_number")

        print(booked_seats_queryset)

        # queryset for prefetching confirmed seats from bookings in Slot model using the previously defined `booked_seats_queryset` to be used in final queryset
        confirmed_bookings_queryset = BookingModels.Booking.objects.filter(
            status=BookingModels.Booking.BookingStatus.BOOKED
        ).prefetch_related(
            Prefetch("seats", queryset=booked_seats_queryset, to_attr="booked_seats")
        )

        print(confirmed_bookings_queryset)

        # queryset for retrieving booked seats from slots -> bookings -> seats
        return self.base_queryset(now).prefetch_related(
            Prefetch(
                "bookings",
                queryset=confirmed_bookings_queryset,
                to_attr="confirmed_bookings",
            ),
        )
