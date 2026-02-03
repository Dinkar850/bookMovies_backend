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
    """Mixin to be used by all views for getting common queryset"""

    def base_queryset(self):
        """Sets queryset for obtaining active slots beyond current date and time plus optimizes fetch using select and prefetch related"""

        now = timezone.now()

        return (
            Slot.objects.filter(is_active=True, schedule__gte=now)
            .order_by("schedule")
            .select_related("movie", "cinema__city", "language")
        )


class SlotListView(SlotBaseMixin, generics.ListAPIView):
    """
    GET /api/slots/

    Description:
        - Returns list of active upcoming slots
        - Supports filtering using SlotFilter

    Query Params:
        language_id:int
        city_id:int
        cinema_id:int
        movie_id:int
        date:date

    Response:
        200 OK
        [
            {
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
        ]
    """

    serializer_class = SlotListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SlotFilter

    def get_queryset(self):
        """Generates queryset from base mixin to be used by this view"""

        return self.base_queryset()


class SlotDetailsView(SlotBaseMixin, generics.RetrieveAPIView):
    """
    GET /api/slots/{id}/

    Description:
        - Returns detailed information for a single active slot (not expired and `is_active=True`)
        - Includes cinema seating layout
        - Includes booked seats
        - Includes currently active seats

    Response:
        200 OK
        {
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
            "booked_seats": [
                {
                    "id": int,
                    "seat_row": int,
                    "seat_number": int
                }
            ],
            "active_seats": [
                {
                    "id": int,
                    "seat_row": int,
                    "seat_number": int
                }
            ]
        }

    Errors:
        404 Not Found:
            - Slot not found
    """

    serializer_class = SlotDetailsSerializer

    def get_queryset(self):
        """
        - Generates queryset from base mixin to be used by this view
        - Populates `active_seats` and `booked_seats` attribute for `confirmed_bookings` by using a custom queryset
        """

        # queryset for fetching and ordering all seats
        cinema_seats = CinemaModels.Seat.objects.order_by("id")

        # queryset for filtering confirmed bookings and then fetching only active seats for each booking
        confirmed_bookings_queryset = BookingModels.Booking.objects.filter(
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
                queryset=confirmed_bookings_queryset,
                to_attr="confirmed_bookings",
            ),
            # prefetch responsible for populating active_seats attribute in slot object for that cinema
            Prefetch(
                "cinema__seats",
                queryset=cinema_seats.filter(is_active=True),
                to_attr="active_seats",
            ),
        )

    def get_object(self):
        """Get the corresponding slot object as referenced by `pk` in `self.get_queryset()` and set the `booked_seats` attribute to be accessed by `SlotDetailsSerializer`"""

        slot = super().get_object()

        # Sorts slots based on seat id for `booked_seats`
        slot.booked_seats = sorted(
            [
                seat
                for booking in slot.confirmed_bookings
                for seat in booking.booked_seats
            ],
            key=lambda seat: seat.id,
        )

        return slot
