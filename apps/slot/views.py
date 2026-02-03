from django.db.models import Prefetch
from django.utils import timezone

from apps.booking import models as BookingModels
from apps.cinema import models as CinemaModels
from apps.core.viewsets import ReadOnlyModelViewset

from .filters import SlotFilter
from .models import Slot
from .serializers import SlotDetailsSerializer, SlotListSerializer


class SlotViewset(ReadOnlyModelViewset):
    """
    Endpoint for:
    - Fetching all slots
    - Fetching a particular slot details with active and booked seats for that slot

    Permissions:
        - AllowAny

    Allowed Methods:
        GET

    LIST
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

    RETRIEVE
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

    filterset_class = SlotFilter
    serializer_class = SlotListSerializer
    pagination_class = None

    def get_serializer_class(self):
        """
        Sets serializer with the following conditions:
        - Uses `SlotListSerializer` when action is `list()`
        - Otherwise uses `SlotDetailsSerializer`
        """

        if self.action == "list":
            return SlotListSerializer

        return SlotDetailsSerializer

    def get_queryset(self):
        """
        - Sets now to current date and time
        - Generates a queryset for retrieving movie entries having at least one active slot
        """

        now = timezone.now()

        base_queryset = (
            Slot.objects.filter(is_active=True, schedule__gte=now)
            .order_by("schedule")
            .select_related("movie", "cinema__city", "language")
        )

        if self.action == "retrieve":
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

            return base_queryset.prefetch_related(
                # prefetch responsible for populating `confirmed_bookings` attribute in slot object with booked status and also populating the `booked_seats` attribute for each confirmed booking
                Prefetch(
                    "bookings",
                    queryset=confirmed_bookings_queryset,
                    to_attr="confirmed_bookings",
                ),
                # prefetch responsible for populating `active_seats`` attribute in slot object for that cinema
                Prefetch(
                    "cinema__seats",
                    queryset=cinema_seats.filter(is_active=True),
                    to_attr="active_seats",
                ),
            )

        return base_queryset

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
